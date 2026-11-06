import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class StorageBackendUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_backends_tab_and_contracts(self):
  for value in ("'Backends'",'Registered backends','Local contract','Memory contract'):self.assertIn(value,self.source)
 def test_non_persistent_disclosure(self):self.assertIn('Memory is a non-persistent validation backend',self.source);self.assertIn('Backend selection is not persisted',self.source)
 def test_migration_is_preview_first_and_confirmed(self):self.assertIn('Migration namespace',self.source);self.assertIn('Preview files',self.source);self.assertIn('Run non-persistent migration test',self.source);self.assertIn('disabled=not confirm',self.source)
 def test_remote_credentials_not_configured(self):self.assertIn('Remote backends require a future explicit credential and approval workflow',self.source)
if __name__=='__main__':unittest.main()
