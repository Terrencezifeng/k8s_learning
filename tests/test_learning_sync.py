"""Offline integration tests: two clones and a local bare Git remote."""
import importlib.util
import io
import os
from contextlib import redirect_stderr
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import call, patch

spec = importlib.util.spec_from_file_location(
    "learning_sync", Path(__file__).resolve().parents[1] / "scripts/learning_sync.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RetryTests(unittest.TestCase):
    def test_transient_fetch_and_push_recover_without_logging_remote_output(self):
        for command in ('fetch', 'push'):
            with self.subTest(command=command):
                failure = subprocess.CompletedProcess([], 128, b'',
                    b'Failed to connect to github.com port 443: Timed out; PRIVATE_TEXT')
                success = subprocess.CompletedProcess([], 0, b'ok', b'')
                output = io.StringIO()
                with patch.object(module.subprocess, 'run', side_effect=[
                        subprocess.TimeoutExpired('git', 60), failure, success]) as run, \
                        patch('time.sleep') as sleep, redirect_stderr(output):
                    result = module.Repository('.').run(command, 'origin')
                self.assertIs(result, success)
                self.assertEqual(run.call_count, 3)
                self.assertEqual(sleep.call_args_list, [call(5), call(10)])
                self.assertIn('3/5', output.getvalue())
                self.assertNotIn('PRIVATE_TEXT', output.getvalue())

    def test_retry_budget_is_five_attempts(self):
        for failure in (subprocess.TimeoutExpired('git', 60),
                        subprocess.CompletedProcess([], 128, b'', b'Connection reset by peer')):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(module.subprocess, 'run', side_effect=[failure] * 5) as run, \
                        patch('time.sleep') as sleep, redirect_stderr(io.StringIO()):
                    with self.assertRaisesRegex(module.SyncError, '5 attempts'):
                        module.Repository('.').run('push', 'origin')
                self.assertEqual(run.call_count, 5)
                self.assertEqual(sleep.call_args_list, [call(5), call(10), call(20), call(30)])

    def test_permanent_and_unknown_errors_are_not_retried(self):
        for error in (b'Authentication failed', b'Permission denied (publickey)',
                      b'The requested URL returned error: 403', b'Repository not found',
                      b'SSL certificate problem', b'Host key verification failed',
                      b'[rejected] main -> main (non-fast-forward)\nConnection reset',
                      b'[remote rejected] hook declined', b'Unknown failure'):
            with self.subTest(error=error):
                result = subprocess.CompletedProcess([], 128, b'', error)
                with patch.object(module.subprocess, 'run', return_value=result) as run, \
                        patch('time.sleep') as sleep:
                    with self.assertRaises(module.SyncError):
                        module.Repository('.').run('push', 'origin')
                self.assertEqual(run.call_count, 1)
                sleep.assert_not_called()

    def test_local_commands_and_missing_git_are_not_retried(self):
        for command, failure in (('commit', subprocess.TimeoutExpired('git', 60)),
                                 ('status', subprocess.CompletedProcess([], 128, b'', b'Timed out')),
                                 ('fetch', FileNotFoundError('git'))):
            with self.subTest(command=command):
                with patch.object(module.subprocess, 'run', side_effect=[failure]) as run, \
                        patch('time.sleep') as sleep:
                    with self.assertRaises(module.SyncError):
                        module.Repository('.').run(command)
                self.assertEqual(run.call_count, 1)
                sleep.assert_not_called()

    def test_known_network_errors_retry_but_auth_failure_stops_next_attempt(self):
        for error in (b'Could not resolve host: github.com',
                      b'Failed to connect to github.com port 443: Could not connect to server',
                      b'RPC failed; curl 56 Recv failure: Connection was reset',
                      b'The remote end hung up unexpectedly', b'fatal: early EOF',
                      b'The requested URL returned error: 503'):
            with self.subTest(error=error):
                results = [subprocess.CompletedProcess([], 128, b'', error),
                           subprocess.CompletedProcess([], 128, b'', b'Authentication failed')]
                with patch.object(module.subprocess, 'run', side_effect=results) as run, \
                        patch('time.sleep') as sleep, redirect_stderr(io.StringIO()):
                    with self.assertRaises(module.SyncError):
                        module.Repository('.').run('fetch', 'origin')
                self.assertEqual(run.call_count, 2)
                sleep.assert_called_once_with(5)


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

    def test_lost_push_response_does_not_create_duplicate_commit(self):
        self.edit(self.a, 'network recovery\n')
        before = int(self.git(self.a, 'rev-list', '--count', 'HEAD'))
        real_run = subprocess.run
        pushes = []

        def lost_response(args, **kwargs):
            result = real_run(args, **kwargs)
            if args[3] == 'push':
                pushes.append(args)
                if len(pushes) == 1:
                    self.assertEqual(result.returncode, 0)
                    raise subprocess.TimeoutExpired(args, 60)
            return result

        with patch.object(module.subprocess, 'run', side_effect=lost_response), \
                patch('time.sleep'), redirect_stderr(io.StringIO()):
            self.run_sync(self.a, 'push')
        self.assertEqual(len(pushes), 2)
        self.assertEqual(pushes[0], pushes[1])
        self.assertEqual(before + 1, int(self.git(self.a, 'rev-list', '--count', 'HEAD')))
        self.assertEqual(self.git(self.a, 'rev-parse', 'HEAD'), self.git(self.remote, 'rev-parse', 'main'))
        self.assertFalse((self.a / '.git/learning-sync.lock').exists())

    def test_exhausted_network_retries_retain_commit_for_later_sync(self):
        self.edit(self.a, 'offline note\n')
        remote_before = self.git(self.remote, 'rev-parse', 'main')
        real_run = subprocess.run
        pushes = []

        def offline(args, **kwargs):
            if args[3] == 'push':
                pushes.append(args)
                return subprocess.CompletedProcess(args, 128, b'', b'Connection timed out')
            return real_run(args, **kwargs)

        with patch.object(module.subprocess, 'run', side_effect=offline), \
                patch('time.sleep'), redirect_stderr(io.StringIO()):
            with self.assertRaises(module.SyncError):
                self.run_sync(self.a, 'push')
        self.assertEqual(len(pushes), 5)
        local_commit = self.git(self.a, 'rev-parse', 'HEAD')
        self.assertNotEqual(local_commit, remote_before)
        self.assertEqual(remote_before, self.git(self.remote, 'rev-parse', 'main'))
        self.assertEqual('', self.git(self.a, 'status', '--porcelain'))
        self.assertFalse((self.a / '.git/learning-sync.lock').exists())
        self.run_sync(self.a, 'push')
        self.assertEqual(local_commit, self.git(self.a, 'rev-parse', 'HEAD'))
        self.assertEqual(local_commit, self.git(self.remote, 'rev-parse', 'main'))

    def test_checkpoint_and_status_never_use_network(self):
        self.edit(self.a, 'chapter done\n')
        remote_before = self.git(self.remote, 'rev-parse', 'main')
        real_run = module.Repository.run

        def local_only(repo, *args, **kwargs):
            self.assertNotIn(args[0], {'fetch', 'push', 'ls-remote'})
            return real_run(repo, *args, **kwargs)

        with patch.object(module.Repository, 'run', local_only):
            snapshot = module.checkpoint(self.a, {str(self.remote)})
            status = module.local_status(self.a, {str(self.remote)})
            self.assertEqual(module.checkpoint(self.a, {str(self.remote)}), snapshot)
        self.assertEqual(status['head'], snapshot)
        self.assertEqual(status['ahead_cached'], 1)
        self.assertFalse(status['remote_checked'])
        self.assertFalse(status['dirty'])
        self.assertEqual(remote_before, self.git(self.remote, 'rev-parse', 'main'))

    def test_publisher_uploads_only_snapshot_and_preserves_new_edits_and_index(self):
        self.edit(self.a, 'first chapter\n')
        snapshot = module.checkpoint(self.a, {str(self.remote)})
        self.edit(self.a, 'second chapter\n')
        self.git(self.a, 'add', 'docs')
        staged = self.git(self.a, 'diff', '--cached')
        self.edit(self.a, 'still editing\n')
        working = self.git(self.a, 'diff')
        module.publish(self.a, snapshot, {str(self.remote)})
        self.assertEqual(staged, self.git(self.a, 'diff', '--cached'))
        self.assertEqual(working, self.git(self.a, 'diff'))
        self.assertEqual(snapshot, self.git(self.remote, 'rev-parse', 'main'))
        self.assertEqual('first chapter', self.git(self.remote, 'show', 'main:docs/learning/笔记.md'))

    def test_publisher_retry_remains_fixed_while_next_checkpoint_succeeds(self):
        self.edit(self.a, 'first chapter\n')
        snapshot = module.checkpoint(self.a, {str(self.remote)})
        real_run = subprocess.run
        pushes = []
        next_snapshot = []

        def next_chapter_during_timeout(args, **kwargs):
            if args[3] == 'push':
                pushes.append(args)
                if len(pushes) == 1:
                    self.edit(self.a, 'second chapter\n')
                    next_snapshot.append(module.checkpoint(self.a, {str(self.remote)}))
                    raise subprocess.TimeoutExpired(args, 60)
            return real_run(args, **kwargs)

        with patch.object(module.subprocess, 'run', side_effect=next_chapter_during_timeout), \
                patch('time.sleep'), redirect_stderr(io.StringIO()):
            module.publish(self.a, snapshot, {str(self.remote)})
        self.assertEqual(len(pushes), 2)
        self.assertTrue(all(args[-1] == snapshot + ':refs/heads/main' for args in pushes))
        self.assertEqual(snapshot, self.git(self.remote, 'rev-parse', 'main'))
        self.assertEqual(next_snapshot[0], self.git(self.a, 'rev-parse', 'HEAD'))
        module.publish(self.a, next_snapshot[0], {str(self.remote)})
        self.assertEqual(next_snapshot[0], self.git(self.remote, 'rev-parse', 'main'))

    def test_old_publish_request_cannot_rewind_remote(self):
        self.edit(self.a, 'first\n')
        first = module.checkpoint(self.a, {str(self.remote)})
        self.edit(self.a, 'second\n')
        second = module.checkpoint(self.a, {str(self.remote)})
        module.publish(self.a, second, {str(self.remote)})
        self.assertIn('Already published', module.publish(self.a, first, {str(self.remote)}))
        self.assertEqual(second, self.git(self.remote, 'rev-parse', 'main'))

    def test_remote_ahead_is_fetched_but_not_merged_into_study_files(self):
        snapshot = self.git(self.b, 'rev-parse', 'HEAD')
        self.edit(self.a, 'remote update\n')
        self.run_sync(self.a, 'push')
        self.edit(self.b, 'local ongoing\n')
        before = self.git(self.b, 'status', '--porcelain')
        self.assertIn('newer commits', module.publish(self.b, snapshot, {str(self.remote)}))
        self.assertEqual(snapshot, self.git(self.b, 'rev-parse', 'HEAD'))
        self.assertEqual(before, self.git(self.b, 'status', '--porcelain'))
        self.assertEqual(1, module.local_status(self.b, {str(self.remote)})['behind_cached'])

    def test_publisher_refuses_divergence_without_touching_local_work(self):
        self.edit(self.a, 'a\n')
        self.edit(self.b, 'b\n')
        first = module.checkpoint(self.a, {str(self.remote)})
        second = module.checkpoint(self.b, {str(self.remote)})
        module.publish(self.a, first, {str(self.remote)})
        with self.assertRaisesRegex(module.SyncError, 'diverged'):
            module.publish(self.b, second, {str(self.remote)})
        self.assertEqual(second, self.git(self.b, 'rev-parse', 'HEAD'))
        self.assertEqual(first, self.git(self.remote, 'rev-parse', 'main'))
        self.assertFalse((self.b / '.git/learning-publish.lock').exists())

    def test_checkpoint_and_publisher_retain_existing_safety_checks(self):
        self.edit(self.a, 'manual stage\n')
        self.git(self.a, 'add', 'docs')
        before = self.git(self.a, 'diff', '--cached')
        with self.assertRaises(module.SyncError): module.checkpoint(self.a, {str(self.remote)})
        self.assertEqual(before, self.git(self.a, 'diff', '--cached'))
        # Use the other checkout to test unpublished history, including removed secrets.
        self.edit(self.b, '-----BEGIN ' + 'RSA PRIVATE KEY-----\n')
        self.git(self.b, 'add', 'docs')
        self.git(self.b, 'commit', '-m', 'Bad revision')
        self.edit(self.b, 'removed\n')
        self.git(self.b, 'add', 'docs')
        self.git(self.b, 'commit', '-m', 'Removed text')
        snapshot = self.git(self.b, 'rev-parse', 'HEAD')
        with self.assertRaises(module.SyncError):
            module.publish(self.b, snapshot, {str(self.remote)})
        with self.assertRaises(module.SyncError): module.checkpoint(self.b, {str(self.remote)})

    def test_publisher_requires_immutable_snapshot_on_main_and_trusted_remote(self):
        snapshot = self.git(self.a, 'rev-parse', 'HEAD')
        for revision in ('HEAD', 'main', snapshot[:7], '-' + snapshot):
            with self.subTest(revision=revision):
                with self.assertRaises(module.SyncError):
                    module.publish(self.a, revision, {str(self.remote)})
        with self.assertRaises(module.SyncError): module.publish(self.a, snapshot)
        self.git(self.a, 'checkout', '-b', 'codex/other')
        self.edit(self.a, 'other branch\n')
        self.git(self.a, 'add', 'docs')
        self.git(self.a, 'commit', '-m', 'Other branch')
        other = self.git(self.a, 'rev-parse', 'HEAD')
        self.git(self.a, 'checkout', 'main')
        with self.assertRaises(module.SyncError):
            module.publish(self.a, other, {str(self.remote)})

    def test_publisher_releases_network_lock_after_retry_exhaustion(self):
        self.edit(self.a, 'chapter\n')
        snapshot = module.checkpoint(self.a, {str(self.remote)})
        real_run = subprocess.run

        def offline(args, **kwargs):
            if args[3] == 'push':
                raise subprocess.TimeoutExpired(args, 60)
            return real_run(args, **kwargs)

        with patch.object(module.subprocess, 'run', side_effect=offline), \
                patch('time.sleep'), redirect_stderr(io.StringIO()):
            with self.assertRaises(module.SyncError):
                module.publish(self.a, snapshot, {str(self.remote)})
        self.assertFalse((self.a / '.git/learning-publish.lock').exists())
        self.assertEqual(snapshot, self.git(self.a, 'rev-parse', 'HEAD'))
        module.publish(self.a, snapshot, {str(self.remote)})
        self.assertEqual(snapshot, self.git(self.remote, 'rev-parse', 'main'))


if __name__ == "__main__":
    unittest.main()
