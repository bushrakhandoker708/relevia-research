"""Tests for scripts/privacy_scan.py.

Fake credentials are assembled at run time so that this file does not itself contain a
string the scanner (or GitHub push protection) would flag.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCANNER = ROOT / 'scripts' / 'privacy_scan.py'
FAKE_GROQ = 'gsk_' + 'Ab3' * 18
FAKE_GITHUB = 'ghp_' + 'x9Y' * 12
FAKE_EMAIL = 'someone.private' + '@' + 'mailhost.co.uk'


def run(cwd, *args):
    r = subprocess.run([sys.executable, '-I', str(SCANNER), *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


class PrivacyScanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = self.tmp.name
        for cmd in (['init', '-q'], ['config', 'user.email', 'test@example.com'], ['config', 'user.name', 'Test'],
                    ['config', 'core.hooksPath', os.devnull]):
            subprocess.run(['git', *cmd], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text, stage=True):
        path = pathlib.Path(self.repo, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        if stage:
            subprocess.run(['git', 'add', name], cwd=self.repo, check=True)

    def test_staged_secret_is_blocked_and_never_printed(self):
        self.write('config.js', f'const key = "{FAKE_GROQ}";\nconst t = "{FAKE_GITHUB}";\n')
        code, out = run(self.repo, '--staged')
        self.assertEqual(code, 1)
        self.assertIn('groq_key', out)
        self.assertIn('github_token', out)
        self.assertNotIn(FAKE_GROQ, out)
        self.assertNotIn(FAKE_GITHUB, out)

    def test_clean_change_passes(self):
        self.write('notes.md', 'Synthetic example only. Contact: test@example.com\n')
        self.assertEqual(run(self.repo, '--staged')[0], 0)

    def test_env_file_and_weights_are_blocked_by_name(self):
        self.write('.env', 'X=1\n')
        self.write('adapter.safetensors', 'not really weights\n')
        code, out = run(self.repo, '--staged')
        self.assertEqual(code, 1)
        self.assertEqual(out.count('blocked_filename'), 2)

    def test_env_example_is_allowed(self):
        self.write('.env.example', 'API_URL=\n')
        self.assertEqual(run(self.repo, '--staged')[0], 0)

    def test_only_added_lines_are_checked_in_staged_mode(self):
        self.write('a.md', f'{FAKE_EMAIL}\n')
        subprocess.run(['git', 'commit', '-q', '-m', 'x'], cwd=self.repo, check=True)
        self.write('a.md', f'{FAKE_EMAIL}\nnew harmless line\n')
        self.assertEqual(run(self.repo, '--staged')[0], 0)
        self.assertEqual(run(self.repo, '--tree')[0], 1)

    def test_allowlist_and_pending_entries(self):
        self.write('contact.md', f'{FAKE_EMAIL}\n')
        subprocess.run(['git', 'commit', '-q', '-m', 'x'], cwd=self.repo, check=True)
        fp = hashlib.sha256(FAKE_EMAIL.encode()).hexdigest()[:16]
        entry = {'rule': 'email', 'path': 'contact.md', 'fingerprint': fp, 'reason': 'test'}
        self.write('.privacy-allowlist.json', json.dumps([entry]), stage=False)
        self.assertEqual(run(self.repo, '--tree')[0], 0)
        self.assertEqual(run(self.repo, '--release')[0], 0)
        entry['pending'] = True
        self.write('.privacy-allowlist.json', json.dumps([entry]), stage=False)
        code, out = run(self.repo, '--tree')
        self.assertEqual(code, 0)
        self.assertIn('PENDING-OWNER-DECISION', out)
        self.assertEqual(run(self.repo, '--release')[0], 1)

    def test_history_finds_a_secret_deleted_later(self):
        self.write('old.txt', f'{FAKE_GITHUB}\n')
        subprocess.run(['git', 'commit', '-q', '-m', 'add'], cwd=self.repo, check=True)
        subprocess.run(['git', 'rm', '-q', 'old.txt'], cwd=self.repo, check=True)
        self.write('keep.txt', 'fine\n')
        subprocess.run(['git', 'commit', '-q', '-m', 'remove'], cwd=self.repo, check=True)
        self.assertEqual(run(self.repo, '--tree')[0], 0)
        code, out = run(self.repo, '--history')
        self.assertEqual(code, 1)
        self.assertIn('github_token', out)

    def test_dist_scan_flags_source_maps_and_fails_closed_without_build(self):
        self.write('dist/app.js.map', '{}', stage=False)
        self.write('dist/app.js', f'var e="{FAKE_EMAIL}"', stage=False)
        code, out = run(self.repo, '--dist', 'dist')
        self.assertEqual(code, 1)
        self.assertIn('source_map_in_build', out)
        self.assertIn('email', out)
        self.assertEqual(run(self.repo, '--dist', 'missing')[0], 2)

    def test_outside_a_git_repository_fails_closed(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertEqual(run(plain, '--tree')[0], 2)

    def test_copy_matches_application_repository(self):
        other = ROOT.parent / 'relevia' / 'scripts' / 'privacy_scan.py'
        if not other.exists():
            self.skipTest('application repository not checked out alongside')
        self.assertEqual(other.read_bytes().replace(b'\r\n', b'\n'), SCANNER.read_bytes().replace(b'\r\n', b'\n'))


if __name__ == '__main__':
    unittest.main()
