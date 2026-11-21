"""Tests for the accounting helpers in scripts/lora_pilot.py.

They cover the three faults an external review found on 21 November 2026: validation
token counts off by one, a final partial accumulation group that was never applied, and
adapter folders that collided when two output paths shared a last component. The module
imports torch only inside main(), so these run without the training dependencies.
"""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lora_pilot', ROOT / 'scripts' / 'lora_pilot.py')
lp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lp)
M = -100  # masked label


class ShiftedTargets(unittest.TestCase):
    def test_masked_prompt_prefix(self):
        # labels[0] is masked, so every unmasked label is a target after the shift
        self.assertEqual(lp.shifted_target_count([M, M, 5, 6, 7]), 3)

    def test_unmasked_first_label_is_not_a_target(self):
        self.assertEqual(lp.shifted_target_count([4, 5, 6]), 2)

    def test_no_targets(self):
        self.assertEqual(lp.shifted_target_count([M, M, M]), 0)
        self.assertEqual(lp.shifted_target_count([7]), 0)
        self.assertEqual(lp.shifted_target_count([]), 0)

    def test_old_formula_undercounted(self):
        labels = [M, M, 5, 6, 7]
        old = sum(x != M for x in labels) - 1
        self.assertEqual(old + 1, lp.shifted_target_count(labels))


class AccumulationGroups(unittest.TestCase):
    def test_final_partial_group_is_kept(self):
        groups = lp.accumulation_groups(list(range(10)), 4)
        self.assertEqual(groups, [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]])

    def test_every_example_used_exactly_once(self):
        order = [5, 2, 9, 0, 7, 1, 3]
        for accum in range(1, 9):
            flat = [i for g in lp.accumulation_groups(order, accum) for i in g]
            self.assertEqual(flat, order)

    def test_exact_multiple(self):
        self.assertEqual(len(lp.accumulation_groups(list(range(16)), 8)), 2)

    def test_empty_and_invalid(self):
        self.assertEqual(lp.accumulation_groups([], 8), [])
        with self.assertRaises(ValueError):
            lp.accumulation_groups([1], 0)


class AdapterDir(unittest.TestCase):
    def test_same_basename_different_paths_do_not_collide(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            a = lp.adapter_dir_for(root / 'results' / 'lora' / 'pilot-a', root)
            b = lp.adapter_dir_for(root / 'results' / 'other' / 'pilot-a', root)
            self.assertNotEqual(a, b)
            self.assertEqual(a, root.resolve() / 'adapters' / 'results__lora__pilot-a')

    def test_outside_root_gets_a_path_hash(self):
        with tempfile.TemporaryDirectory() as d1, tempfile.TemporaryDirectory() as d2:
            a = lp.adapter_dir_for(pathlib.Path(d2) / 'x' / 'run', d1)
            b = lp.adapter_dir_for(pathlib.Path(d2) / 'y' / 'run', d1)
            self.assertNotEqual(a, b)
            self.assertTrue(a.name.startswith('run-'))
            self.assertEqual(a.parent, pathlib.Path(d1).resolve() / 'adapters')


class ConfigFreeze(unittest.TestCase):
    def test_pilot_config_freezes_both_partitions(self):
        import json
        data = json.loads((ROOT / 'configs' / 'milestone_4.pilot.json').read_text(encoding='utf-8'))['data']
        for key in ('training_sha256', 'validation_sha256'):
            self.assertRegex(data[key], r'^[0-9a-f]{64}$')


if __name__ == '__main__':
    unittest.main()
