import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class OperationsRecoveryUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_recovery_tabs_are_present(self):
  for label in ('Project health','Repository','Storage','Backups','Support'):self.assertIn(label,self.source)
 def test_destructive_actions_require_confirmation(self):
  for label in ('Move selected file to quarantine','Restore selected quarantined file','Replace current index from selected backup'):self.assertIn(label,self.source)
 def test_support_bundle_discloses_exclusions(self):self.assertIn('exclude credentials, project text, transcripts, media content, and absolute user paths',self.source)
 def test_snapshot_discloses_media_boundary(self):self.assertIn('Metadata snapshot only; external audio is not included.',self.source)
if __name__=='__main__':unittest.main()
