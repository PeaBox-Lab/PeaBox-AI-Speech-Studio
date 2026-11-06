import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MaintenanceUiTests(unittest.TestCase):
 def setUp(self):self.app=(ROOT/'app.py').read_text()
 def test_operations_tabs_and_actions(self):
  for marker in ('Storage maintenance','Database maintenance','Support bundle','Quarantine orphaned outputs','Restore selected database backup','Download sanitized support bundle'):
   self.assertIn(marker,self.app)
 def test_destructive_quarantine_actions_require_confirmation(self):
  self.assertIn('I reviewed the orphan preview',self.app);self.assertIn('Permanently delete selected batch',self.app)
if __name__=='__main__':unittest.main()
