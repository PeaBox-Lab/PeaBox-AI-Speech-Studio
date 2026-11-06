import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ObjectStorageUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_objects_tab_and_disclosure(self):self.assertIn("'Objects'",self.source);self.assertIn('No remote storage is configured',self.source)
 def test_manifest_controls_exist(self):
  for label in ('Rebuild object manifest','Audit object manifest','Registered objects'):self.assertIn(label,self.source)
 def test_object_operations_are_guarded(self):
  for label in ('Copy object','Move object','Delete object','Move removes the source after verified copy','Permanently delete selected object'):self.assertIn(label,self.source)
 def test_namespaces_are_visible(self):
  for value in ('outputs','models','backups','quarantine','support','worker'):self.assertIn(value,self.source)
if __name__=='__main__':unittest.main()
