import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class OperationsUiTests(unittest.TestCase):
 def setUp(self):
  self.app=(ROOT/'app.py').read_text();self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text()
 def test_operations_screen_registered(self):
  self.assertIn('"Operations Center", "Operations"',self.ui);self.assertIn('page == "Operations"',self.app)
 def test_repository_and_snapshot_actions_exist(self):
  for marker in ('Rebuild project index','Create project snapshot','Restore over active project','Restore as new project','Download operation log'):
   self.assertIn(marker,self.app)
 def test_json_remains_source_of_truth_message(self):
  self.assertIn('JSON projects remain portable source-of-truth',self.app)
if __name__=='__main__':unittest.main()
