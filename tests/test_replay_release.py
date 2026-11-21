"""Release-policy replay: self-test, frozen policy copies and the development-input guard.

The replay imports the frozen copies in detectors/release_v1/, so these tests need only
Node.js, not the application checkout.
"""
import hashlib
import json
import pathlib
import shutil
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = ROOT / 'detectors' / 'release_v1'
NODE = shutil.which('node')

# Application commit 3195335; also the hashes recorded in results/release/sim-dev-v1/replay.json.
FROZEN_SHA256 = {
    'releasePolicy.js': '8df1958e9e5689d2d0923e3f996261abb8b0fce5f9f7f838009b0a5116fcbcd2',
    'replyGuard.js': '88d923e23ada4eb74a7e1d94f901c34ae9df10dbcd3652341deb7ec0baf36f16',
    'consts.js': '436618ca16fc38043f82492c93a2f637f760ab80b98b32d02c299129d15451c3',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FrozenPolicies(unittest.TestCase):
    def test_frozen_copies_are_unchanged(self):
        for name, digest in FROZEN_SHA256.items():
            self.assertEqual(sha256(FROZEN / name), digest, name)

    def test_v1_replay_used_the_same_code(self):
        code = json.loads((ROOT / 'results/release/sim-dev-v1/replay.json').read_text(encoding='utf-8'))['code']
        self.assertEqual(code['releasePolicy'], FROZEN_SHA256['releasePolicy.js'])
        self.assertEqual(code['replyGuard'], FROZEN_SHA256['replyGuard.js'])

    def test_v2_replay_used_the_frozen_copies(self):
        code = json.loads((ROOT / 'results/release/sim-dev-v2/replay.json').read_text(encoding='utf-8'))['code']
        self.assertEqual(code['source'], 'detectors/release_v1 (frozen)')
        self.assertEqual(code['releasePolicy'], FROZEN_SHA256['releasePolicy.js'])


@unittest.skipUnless(NODE, 'needs Node.js')
class ReplayScripts(unittest.TestCase):
    def run_node(self, *args):
        return subprocess.run([NODE, *map(str, args)], capture_output=True, text=True, timeout=60, cwd=ROOT)

    def test_self_test(self):
        out = self.run_node(ROOT / 'scripts' / 'replay_release.mjs', '--self-test')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('self-test passed', out.stdout)

    def test_simulator_refuses_test_and_heldout_inputs(self):
        out = self.run_node(ROOT / 'scripts' / 'simulate_traces.mjs', '--check')
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertIn('check passed', out.stdout)

    def test_v2_traces_are_development_only(self):
        prov = json.loads((ROOT / 'results/release/sim-dev-v2/traces.provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(set(prov['corpora']), {'experiment_01/dev-v1', 'experiment_01/dev-v2', 'lora/smoke-v1-generations'})
        traces = json.loads((ROOT / 'results/release/sim-dev-v2/traces.json').read_text(encoding='utf-8'))
        for t in traces:
            self.assertFalse(any(k in t['id'] for k in ('expanded', 'test-v1', 'repeat', 'generative')), t['id'])


if __name__ == '__main__':
    unittest.main()
