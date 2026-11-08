import json
import subprocess
import sys
import tempfile
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyse_robustness import (wilson, binom_two_sided, hodges_lehmann, location_summary,  # noqa: E402
                                ols, mcnemar, distinct_n)


class RobustnessStatsTests(unittest.TestCase):
    def test_wilson_bounds_and_empty(self):
        self.assertIsNone(wilson(0, 0))
        lo, hi = wilson(0, 10)
        self.assertEqual(lo, 0.0)
        self.assertGreater(hi, 0.2)  # zero successes still leaves real uncertainty
        lo, hi = wilson(10, 10)
        self.assertAlmostEqual(hi, 1.0)

    def test_exact_binomial(self):
        self.assertIsNone(binom_two_sided(0, 0))
        self.assertAlmostEqual(binom_two_sided(0, 5), 2 / 32)
        self.assertEqual(binom_two_sided(3, 6), 1.0)

    def test_hodges_lehmann_resists_one_outlier(self):
        diffs = [-3, -2, -4, -3, -2, -1000]
        self.assertLess(abs(hodges_lehmann(diffs) + 3), 1.0)
        self.assertLess(location_summary(diffs)['mean'], -100)

    def test_location_summary_counts_signs(self):
        s = location_summary([1, 2, -1, 0])
        self.assertEqual((s['B_slower_pairs'], s['B_faster_pairs']), (2, 1))
        self.assertIsNone(location_summary([]))

    def test_ols_recovers_line_and_rejects_flat_x(self):
        fit = ols([1, 2, 3, 4], [3, 5, 7, 9])
        self.assertAlmostEqual(fit['seconds_per_output_token'], 2)
        self.assertAlmostEqual(fit['intercept_seconds'], 1)
        self.assertIsNone(ols([5, 5, 5], [1, 2, 3]))

    def test_mcnemar_uses_discordant_pairs_only(self):
        m = mcnemar([(True, True), (True, False), (True, False), (False, False)])
        self.assertEqual((m['only_A'], m['only_B'], m['both'], m['neither']), (2, 0, 1, 1))
        self.assertAlmostEqual(m['exact_p'], 0.5)
        self.assertIsNone(mcnemar([(True, True)])['exact_p'])

    def test_distinct_n_empty(self):
        self.assertIsNone(distinct_n([''], 2))
        self.assertEqual(distinct_n(['a b a b'], 1), 0.5)


# src/common.py imports PyYAML, which the stdlib-only CI job does not install
@unittest.skipUnless(importlib.util.find_spec('yaml'), 'PyYAML not installed')
class RatingSheetTests(unittest.TestCase):
    """make_rating_sheet must fail loudly instead of writing an empty or partial sheet."""

    def run_sheet(self, rows, conditions):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / 'src'
            src.mkdir()
            for name in ('make_rating_sheet.py', 'common.py'):
                (src / name).write_text((ROOT / 'src' / name).read_text(encoding='utf-8'), encoding='utf-8')
            gen = Path(tmp) / 'results/generations'
            gen.mkdir(parents=True)
            for cond, seed, items in rows:
                with (gen / f'm__{cond}__t__seed{seed}.jsonl').open('w', encoding='utf-8') as f:
                    for i in items:
                        f.write(json.dumps({'id': i, 'condition': cond, 'seed': seed, 'model': 'm',
                                            'prompt': 'p', 'generated': 'g'}) + '\n')
            cmd = [sys.executable, str(src / 'make_rating_sheet.py'), '--model', 'm', '--testset', 't',
                   '--conditions', *conditions]
            return subprocess.run(cmd, capture_output=True, text=True)

    def test_no_rated_seed_fails_instead_of_empty_sheet(self):
        r = self.run_sheet([('a', 2, ['x']), ('b', 2, ['x'])], ['a', 'b'])
        self.assertNotEqual(r.returncode, 0)

    def test_missing_condition_fails(self):
        r = self.run_sheet([('a', 1, ['x'])], ['a', 'b'])
        self.assertNotEqual(r.returncode, 0)

    def test_complete_pairs_succeed(self):
        r = self.run_sheet([('a', 1, ['x', 'y']), ('b', 1, ['x', 'y'])], ['a', 'b'])
        self.assertEqual(r.returncode, 0, r.stderr)


if __name__ == '__main__':
    unittest.main()
