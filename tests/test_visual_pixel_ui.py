import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class VisualPixelUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_readiness_and_threshold_controls(self):
  for value in ('PNG capture readiness','Per-channel pixel threshold','Allowed changed pixels percent','Run PNG pixel comparison'):self.assertIn(value,self.source)
 def test_report_downloads_exist(self):self.assertIn('Download pixel diff report',self.source);self.assertIn('Download pixel diff bundle',self.source)
 def test_comparison_disabled_until_ready(self):self.assertIn("disabled=not (baseline_inventory['ready'] and candidate_inventory['ready'])",self.source)
if __name__=='__main__':unittest.main()
