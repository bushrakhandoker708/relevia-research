import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from analyse_independent_ratings import score, paired, weighted_kappa


class IndependentRatingsTests(unittest.TestCase):
    def test_missing_is_not_zero(self):
        self.assertIsNone(score('',range(1,6)))
        self.assertEqual(paired({('s','A'):{'relevance':5},('s','B'):{'relevance':None}},'relevance')['n_pairs'],0)

    def test_invalid_quality_score_rejected(self):
        for value in ['0','6','3.5','helpful']:
            with self.assertRaises(ValueError):score(value,range(1,6))

    def test_paired_sign_and_interval(self):
        rows={(s,c):{'relevance':v} for s in ['one','two'] for c,v in [('A',4),('B',2)]}
        result=paired(rows,'relevance')
        self.assertEqual(result['mean_B_minus_A'],-2)
        self.assertEqual(result['bootstrap95'],[-2,-2])

    def test_agreement_and_degenerate_case(self):
        self.assertEqual(weighted_kappa([(1,1),(3,3),(5,5)]),1)
        self.assertLess(weighted_kappa([(1,5),(5,1)]),0)
        self.assertIsNone(weighted_kappa([(3,3),(3,3)]))
        self.assertIsNone(weighted_kappa([]))
