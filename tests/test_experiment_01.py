import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from experiment_01 import check_pair, load_rows
from analyse_experiment_01 import paired_interval, analyse


class ExperimentIntegrityTests(unittest.TestCase):
    def row(self, identifier, group, text):
        return {'scenario_id':identifier,'conversation_group_id':group,'input_text':text}

    def test_group_leak_fails_even_with_different_text(self):
        with self.assertRaises(ValueError):
            check_pair([self.row('a','same','one')],[self.row('b','same','two')])

    def test_normalised_duplicate_fails_with_different_ids(self):
        with self.assertRaises(ValueError):
            check_pair([self.row('a','one',' I feel sad ')],[self.row('b','two','i FEEL sad')])

    def test_quarantine_path_rejected_before_read(self):
        with self.assertRaises(ValueError):
            load_rows(ROOT/'archive/quarantine/empathy_42k.jsonl.quarantined','dev')

    def test_disjoint_passes(self):
        check_pair([self.row('a','one','one')],[self.row('b','two','two')])

    def test_paired_constant_difference_interval(self):
        self.assertEqual(paired_interval([1,1,1])['bootstrap_95_percentile'],[1,1])
        self.assertEqual(paired_interval([-2,-2])['mean_B_minus_A'],-2)

    def test_incomplete_pairs_rejected(self):
        with self.assertRaises(ValueError):
            analyse([{'scenario_id':'one','conversation_group_id':'one','condition':'A'}])

    def test_missing_ratings_are_not_invented(self):
        rows=[{'scenario_id':'one','conversation_group_id':'one','condition':c,'status':'generated',
               'hit_token_limit':False,'output_tokens':2,'elapsed_seconds':1} for c in ['A','B']]
        self.assertIsNone(analyse(rows)['quality'])


if __name__=='__main__': unittest.main()
