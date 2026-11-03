"""Offline integration tests: two clones and a local bare Git remote."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "learning_sync", Path(__file__).resolve().parents[1] / "scripts/learning_sync.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.remote = self.root / "remote.git"
        self.a, self.b = self.root / "a", self.root / "b"
        self.git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        self.git(self.root, "clone", str(self.remote), str(self.a))
        self.identity(self.a)
        (self.a / "README.md").write_text("# Study\n", encoding="utf-8")
        (self.a / ".gitignore").write_text(".local/\n.idea/\n", encoding="utf-8")
        self.git(self.a, "add", "README.md", ".gitignore")
        self.git(self.a, "commit", "-m", "Initial")
        self.git(self.a, "push", "-u", "origin", "main")
        self.git(self.root, "clone", str(self.remote), str(self.b))
        self.identity(self.b)

    def git(self, root, *args):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                                encoding="utf-8", errors="strict", timeout=30)
        if result.returncode:
            self.fail("git " + args[0] + " failed: " + result.stderr)
        return result.stdout.strip()

    def identity(self, root):
        self.git(root, "config", "user.name", "Sync Test")
        self.git(root, "config", "user.email", "test@example.invalid")
        self.git(root, "config", "commit.gpgsign", "false")
        self.git(root, "config", "core.autocrlf", "false")

    def run_sync(self, root, mode):
        return module.sync(root, mode, {str(self.remote)})

    def edit(self, root, text, filename="docs/learning/笔记.md"):
        path = root / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_two_computers_roundtrip_and_repeat(self):
        self.edit(self.a, "Mac 学习记录\n")
        self.run_sync(self.a, "push")
        self.run_sync(self.b, "pull")
        self.assertEqual((self.b / "docs/learning/笔记.md").read_text(encoding="utf-8"), "Mac 学习记录\n")
        self.edit(self.b, "Windows 补充\n")
        self.run_sync(self.b, "push")
        self.run_sync(self.a, "pull")
        before = self.git(self.a, "rev-parse", "HEAD")
        self.run_sync(self.a, "push")
        self.assertEqual(before, self.git(self.a, "rev-parse", "HEAD"))

    def test_dirty_pull_retains_local_file(self):
        path = self.edit(self.b, "unsaved-to-git\n")
        with self.assertRaises(module.SyncError): self.run_sync(self.b, "pull")
        self.assertEqual(path.read_text(), "unsaved-to-git\n")

    def test_remote_advanced_and_dirty_stops_before_commit(self):
        self.edit(self.a, "remote\n")
        self.run_sync(self.a, "push")
        path = self.edit(self.b, "local\n")
        before = self.git(self.b, "rev-parse", "HEAD")
        with self.assertRaises(module.SyncError): self.run_sync(self.b, "push")
        self.assertEqual(before, self.git(self.b, "rev-parse", "HEAD"))
        self.assertEqual(path.read_text(), "local\n")

    def test_divergent_commits_preserved(self):
        self.edit(self.a, "a\n")
        self.run_sync(self.a, "push")
        self.edit(self.b, "b\n")
        self.git(self.b, "add", "docs")
        self.git(self.b, "commit", "-m", "Local change")
        before = self.git(self.b, "rev-parse", "HEAD")
        with self.assertRaises(module.SyncError): self.run_sync(self.b, "push")
        self.assertEqual(before, self.git(self.b, "rev-parse", "HEAD"))

    def test_existing_stage_is_not_committed(self):
        self.edit(self.a, "manual stage\n")
        self.git(self.a, "add", "docs")
        before = self.git(self.a, "diff", "--cached")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")
        self.assertEqual(before, self.git(self.a, "diff", "--cached"))

    def test_credential_in_notes_is_blocked(self):
        self.edit(self.a, "-----BEGIN " + "OPENSSH PRIVATE KEY-----\n")
        before = self.git(self.remote, "rev-parse", "main")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")
        self.assertEqual(before, self.git(self.remote, "rev-parse", "main"))
        self.assertEqual("", self.git(self.a, "diff", "--cached", "--name-only"))

    def test_secret_removed_in_later_commit_still_blocks_history(self):
        self.edit(self.a, "-----BEGIN " + "RSA PRIVATE KEY-----\n")
        self.git(self.a, "add", "docs")
        self.git(self.a, "commit", "-m", "Bad local revision")
        self.edit(self.a, "removed\n")
        self.git(self.a, "add", "docs")
        self.git(self.a, "commit", "-m", "Removed text")
        before = self.git(self.remote, "rev-parse", "main")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")
        self.assertEqual(before, self.git(self.remote, "rev-parse", "main"))

    def test_kubernetes_credential_formats_are_blocked(self):
        synthetic = [
            "kubeadm join --token " + "a" * 6 + "." + "b" * 16,
            "password: " + "SyntheticOnly123",
            '"client-key-data": "' + "Z" * 32 + '"',
            "client-key-data: '" + "Z" * 32 + "'",
            "Authorization: Bearer " + "SyntheticOnly" * 3,
        ]
        for text in synthetic:
            with self.subTest(format=text.split(":")[0]):
                with self.assertRaises(module.SyncError):
                    module.inspect_content("docs/example.md", text.encode())

    def test_bootstrap_token_removed_from_history_still_blocks(self):
        self.edit(self.a, "kubeadm join --token " + "a" * 6 + "." + "b" * 16)
        self.git(self.a, "add", "docs")
        self.git(self.a, "commit", "-m", "Synthetic credential")
        self.edit(self.a, "removed\n")
        self.git(self.a, "add", "docs")
        self.git(self.a, "commit", "-m", "Removed text")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")

    def test_ignored_local_data_never_added(self):
        self.edit(self.a, "private\n", ".local/cookies.txt")
        self.edit(self.a, "local IDE\n", ".idea/workspace.xml")
        self.edit(self.a, "note\n")
        self.run_sync(self.a, "push")
        files = self.git(self.a, "ls-tree", "-r", "--name-only", "HEAD")
        self.assertNotIn("cookies", files)
        self.assertNotIn(".idea", files)

    def test_non_markdown_file_requires_review(self):
        self.edit(self.a, "print('hello')\n", "scripts/new.py")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")

    def test_wrong_remote_and_branch_blocked(self):
        with self.assertRaises(module.SyncError): module.sync(self.a, "push")
        self.git(self.a, "checkout", "-b", "codex/test")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "pull")

    def test_push_failure_retains_commit_for_retry(self):
        self.git(self.remote, "config", "receive.denyNonFastForwards", "true")
        # Deny updating the current branch of a non-bare remote without shell hooks.
        self.git(self.remote, "config", "core.bare", "false")
        self.git(self.remote, "config", "receive.denyCurrentBranch", "refuse")
        self.edit(self.a, "saved before rejection\n")
        old = self.git(self.a, "rev-parse", "HEAD")
        with self.assertRaises(module.SyncError): self.run_sync(self.a, "push")
        self.assertNotEqual(old, self.git(self.a, "rev-parse", "HEAD"))
        self.assertEqual("", self.git(self.a, "status", "--porcelain"))
        self.git(self.remote, "config", "core.bare", "true")
        self.run_sync(self.a, "push")
        self.assertEqual(self.git(self.a, "rev-parse", "HEAD"), self.git(self.remote, "rev-parse", "main"))


if __name__ == "__main__":
    unittest.main()
