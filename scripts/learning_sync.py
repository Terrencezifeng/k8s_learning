#!/usr/bin/env python3
"""Conservative, session-triggered Markdown sync. Python 3.9+, Git; no packages."""
import argparse
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from datetime import datetime, timezone

TARGETS = {
    "https://github.com/Terrencezifeng/k8s_learning.git",
    "https://github.com/Terrencezifeng/k8s_learning",
    "git@github.com:Terrencezifeng/k8s_learning.git",
}
SECRET_PATTERNS = [
    rb"-----BEGIN (?:[A-Z ]*PRIVATE KEY)-----",
    rb"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b",
    rb"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
    rb"(?i)[\"']?client-key-data[\"']?\s*:\s*[\"']?[A-Za-z0-9+/=]{24,}",
    rb"(?i)\b(?:SESSDATA|bili_jct)\s*[=:]\s*[\"']?[A-Za-z0-9%_-]{16,}",
    rb"(?i)\b(?:AKIA|ASIA)[A-Z0-9]{16}\b",
    rb"\b[a-z0-9]{6}\.[a-z0-9]{16}\b",  # kubeadm bootstrap token
    rb"(?i)\b(?:password|passwd|token)[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_+/!@$%&.*=-]{8,}",
    rb"(?i)\bBearer\s+[A-Za-z0-9_+/.-]{16,}",
    rb"\bsk-[A-Za-z0-9_-]{20,}\b",
]


class SyncError(RuntimeError):
    pass


class Repository:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.env = os.environ.copy()
        self.env.update(GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never",
                        GIT_LITERAL_PATHSPECS="1")
        self.env.setdefault("GIT_SSH_COMMAND", "ssh -oBatchMode=yes")

    def run(self, *args, ok=(0,)):
        try:
            result = subprocess.run(["git", "-C", str(self.root), *args],
                                    capture_output=True, env=self.env, timeout=60)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SyncError("Git unavailable or timed out; local files retained.") from exc
        if result.returncode not in ok:
            # Do not print arbitrary remote errors, diffs or credential-helper output.
            raise SyncError("git " + args[0] + " failed; check network, Git login, "
                            "permissions and git status. No force/reset was attempted.")
        return result

    def text(self, *args):
        return self.run(*args).stdout.decode("utf-8", "strict").strip()

    def paths(self, *args):
        return [p.decode("utf-8", "strict") for p in self.run(*args).stdout.split(b"\0") if p]

    def dirty(self):
        return bool(self.run("status", "--porcelain", "-z").stdout)


def allowed(path):
    p = PurePosixPath(path)
    return (path in {"README.md", "PLAN.md", "AGENTS.md"} or
            (p.parts[0] == "docs" and p.suffix.lower() == ".md" and
             not any(part.startswith(".") or part.lower() in {"secrets", "credentials"}
                     for part in p.parts)))


def inspect_content(path, data):
    if not allowed(path):
        raise SyncError("Manual review required for file outside Markdown sync scope: " + path)
    if len(data) > 2 * 1024 * 1024:
        raise SyncError("Manual review required for large Markdown file: " + path)
    try:
        data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise SyncError("Expected UTF-8 Markdown: " + path) from exc
    if any(re.search(pattern, data) for pattern in SECRET_PATTERNS):
        raise SyncError("Possible credential detected; content not printed: " + path)


def inspect_revision(repo, revision, path):
    entry = repo.run("ls-tree", "-z", revision, "--", path).stdout
    if not entry:  # Deletion is allowed, but the path must still be in scope.
        if not allowed(path):
            raise SyncError("Manual review required for deletion: " + path)
        return
    if not entry.startswith(b"100644 blob ") and not entry.startswith(b"100755 blob "):
        raise SyncError("Only regular Markdown files can be synced: " + path)
    inspect_content(path, repo.run("show", revision + ":" + path).stdout)


def sync(root, mode, targets=None):
    repo = Repository(root)
    approved = TARGETS if targets is None else targets  # Local test repositories only.
    if Path(repo.text("rev-parse", "--show-toplevel")).resolve() != repo.root:
        raise SyncError("Run against this project's repository root.")
    if repo.text("branch", "--show-current") != "main":
        raise SyncError("Session sync requires main; current branch was left unchanged.")
    if repo.text("remote", "get-url", "origin") not in approved:
        raise SyncError("Unexpected origin; refusing to sync to another repository.")
    push_urls = repo.text("remote", "get-url", "--push", "--all", "origin").splitlines()
    if len(push_urls) != 1 or push_urls[0] not in approved:
        raise SyncError("Unexpected push destination; refusing to publish.")
    gitdir = Path(repo.text("rev-parse", "--absolute-git-dir"))
    lock = gitdir / "learning-sync.lock"
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise SyncError("Another sync is active, or a stale learning-sync.lock needs review.") from exc
    try:
        with os.fdopen(fd, "w") as stream:
            stream.write(str(os.getpid()))
        if any((gitdir / marker).exists() for marker in
               ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply")):
            raise SyncError("Finish the existing Git operation before syncing.")
        if repo.run("ls-files", "-u").stdout:
            raise SyncError("Unresolved conflicts; preserve both sides and resolve manually.")
        if repo.run("diff", "--cached", "--name-only", "-z").stdout:
            raise SyncError("Existing staged work found; it was not modified or committed.")
        repo.run("fetch", "--no-tags", "origin", "refs/heads/main:refs/remotes/origin/main")
        ahead, behind = map(int, repo.text("rev-list", "--left-right", "--count",
                                          "HEAD...refs/remotes/origin/main").split())
        if ahead and behind:
            raise SyncError("Both computers have commits; reconcile manually. No automatic merge/rebase.")
        if mode == "pull":
            if repo.dirty():
                raise SyncError("Local edits found; save/sync them before pulling. Nothing overwritten.")
            if behind:
                repo.run("merge", "--ff-only", "refs/remotes/origin/main")
            return "Pull complete." + (" Local commits still need push." if ahead else "")
        if behind:
            if repo.dirty():
                raise SyncError("Remote advanced while local edits exist; preserve both and reconcile.")
            repo.run("merge", "--ff-only", "refs/remotes/origin/main")
        paths = sorted(set(repo.paths("diff", "--name-only", "-z", "--no-renames", "HEAD") +
                           repo.paths("ls-files", "--others", "--exclude-standard", "-z")))
        for path in paths:
            if not allowed(path):
                raise SyncError("Manual review required outside Markdown sync scope: " + path)
            file = repo.root / path
            if file.is_symlink():
                raise SyncError("Symlinks are not synced: " + path)
            try:
                file.resolve().relative_to(repo.root)
            except ValueError as exc:
                raise SyncError("File resolves outside project: " + path) from exc
            if file.exists():
                inspect_content(path, file.read_bytes())
        # Check every unpublished revision, including secrets later removed in another commit.
        for commit in repo.text("rev-list", "refs/remotes/origin/main..HEAD").splitlines():
            for path in repo.paths("diff-tree", "--root", "--no-commit-id", "-r", "-m",
                                   "--no-renames", "--name-only", "-z", commit):
                inspect_revision(repo, commit, path)
        if paths:
            repo.run("add", "--all", "--", *paths)
            # Recheck staged bytes in case an editor saved while staging.
            tree = repo.text("write-tree")
            for path in repo.paths("diff", "--cached", "--name-only", "-z", "--no-renames"):
                inspect_revision(repo, tree, path)
            stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
            repo.run("commit", "-m", "docs: sync learning notes " + stamp)
        repo.run("push", "origin", "HEAD:refs/heads/main")
        # Push errors (including a concurrent writer) retain the local commit for retry.
        return "Push complete; " + repo.text("rev-parse", "--short", "HEAD")
    finally:
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("pull", "push"))
    args = parser.parse_args()
    try:
        print(sync(Path(__file__).resolve().parents[1], args.mode))
    except (SyncError, UnicodeError, ValueError) as exc:
        print("SYNC STOPPED: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
