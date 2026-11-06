import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class VisualQaUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text();self.generator=(ROOT/'generate_visual_baselines.py').read_text()
 def test_visual_qa_tab_and_metrics(self):
  for value in ("'Visual QA'",'Pages','Screen modules','Planned captures','Contract issues'):self.assertIn(value,self.source)
 def test_visual_disclosure_and_downloads(self):self.assertIn('PNG capture remains an external browser step',self.source);self.assertIn('Download UI baseline JSON',self.source);self.assertIn('Download screenshot manifest',self.source)
 def test_generator_validates_before_writing(self):self.assertIn('validate_baseline',self.generator);self.assertIn('Visual baseline validation failed',self.generator)
if __name__=='__main__':unittest.main()
