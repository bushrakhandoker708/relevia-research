import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from summarise_controlled import quantile, summary


class ExecutionSummaryTests(unittest.TestCase):
    def test_interpolated_percentile_and_single_observation(self):
        self.assertEqual(quantile([10,20],.5),15)
        self.assertEqual(quantile([10],.95),10)
        self.assertAlmostEqual(quantile([10,20],.95),19.5)

    def test_failure_retained_without_fake_timing(self):
        result=summary([{'status':'failed','error_type':'RuntimeError'}])
        self.assertEqual(result['attempted'],1)
        self.assertEqual(result['generated'],0)
        self.assertIsNone(result['elapsed_seconds'])

    def test_missing_throughput_does_not_become_zero(self):
        row={'status':'generated','elapsed_seconds':3,'input_tokens':8,'output_tokens':1,'ttft_seconds':2,'decode_tokens_per_second':None,'hit_token_limit':False}
        result=summary([row])
        self.assertIsNone(result['decode_tokens_per_second'])
        self.assertEqual(result['ttft_seconds']['mean'],2)
