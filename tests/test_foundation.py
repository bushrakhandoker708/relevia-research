import importlib.util
import sys
import unittest
import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from splits import reserve_development, assert_disjoint
spec = importlib.util.spec_from_file_location('harness', ROOT / 'scripts/run_experiment.py')
harness = importlib.util.module_from_spec(spec)
spec.loader.exec_module(harness)


class FoundationTests(unittest.TestCase):
    def test_group_split_deterministic(self):
        rows = [{'id': f'{i}-{turn}', 'conv_id': str(i), 'turn': turn, 'emotion': str(i),
                 'response': 'one two three four five six seven eight nine'} for i in range(100) for turn in (2, 4)]
        a = reserve_development(rows, [], 4)
        self.assertEqual(a, reserve_development(rows, [], 4)); assert_disjoint(a)
        self.assertEqual(len(a['fewshot']), 4)

    def test_leak_fails(self):
        with self.assertRaises(ValueError):
            assert_disjoint({'a': [{'conv_id': 'shared'}], 'b': [{'conv_id': 'shared'}]})

    def fixture(self):
        return ({'experiment_id': 'unit-test-only', 'condition': 'A', 'model_id': 'stub',
                 'model_revision': 'a' * 40, 'prompt_version': 'test', 'prompt': 'synthetic',
                 'dataset_version': 'test', 'seed': 42, 'generation': {'max_new_tokens': 2, 'do_sample': False}},
                [{'scenario_id': 'a', 'conversation_group_id': 'a', 'source': 'synthetic', 'source_license': 'CC0-1.0',
                  'split': 'dev', 'input_text': 'unit test input'}])

    def test_required_revision(self):
        cfg, rows = self.fixture(); cfg['model_revision'] = None
        with self.assertRaises(ValueError): harness.validate(cfg, rows)

    def test_export_unrated(self):
        cfg, rows = self.fixture()
        result = list(harness.execute(cfg, rows, lambda *args: 'unit-test stub output'))[0]
        self.assertEqual(result['status'], 'generated')
        self.assertTrue(all(v is None for v in result['quality'].values()))
        self.assertEqual(result['annotation_status'], 'unrated')

    def test_failure_retained(self):
        cfg, rows = self.fixture()
        def fail(*args): raise RuntimeError('must not serialize arbitrary exception content')
        result = list(harness.execute(cfg, rows, fail))[0]
        self.assertEqual(result['status'], 'failed'); self.assertIsNone(result['response'])
        self.assertEqual(result['error_type'], 'RuntimeError')

    def test_live_data_and_duplicates_rejected(self):
        cfg, rows = self.fixture()
        with self.assertRaises(ValueError): harness.validate(cfg, rows + rows)
        rows[0]['source'] = 'live chat'
        with self.assertRaises(ValueError): harness.validate(cfg, rows)

    def test_prepare_cli_has_no_fabricated_responses_and_refuses_overwrite(self):
        cfg, rows = self.fixture()
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests', prefix='.tmp-') as directory:
            root = Path(directory).resolve()
            self.assertTrue(root.is_relative_to((ROOT / 'tests').resolve()))
            (root / 'config.json').write_text(json.dumps(cfg))
            (root / 'data.jsonl').write_text(json.dumps(rows[0]) + '\n')
            command = [sys.executable, str(ROOT / 'scripts/run_experiment.py'), '--config', str(root / 'config.json'),
                       '--data', str(root / 'data.jsonl'), '--out', str(root / 'run'), '--prepare']
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
            manifest = json.loads((root / 'run/manifest.json').read_text())
            self.assertEqual(manifest['status'], 'prepared_not_run')
            self.assertFalse((root / 'run/responses.jsonl').exists())
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)

    def test_adaptation_not_silently_treated_as_base(self):
        cfg, rows = self.fixture(); cfg['condition'] = 'C'
        with self.assertRaises(ValueError): harness.validate(cfg, rows)


if __name__ == '__main__': unittest.main()
