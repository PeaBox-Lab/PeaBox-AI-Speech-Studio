import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.models import Project,ScriptBlock
from peabox_voice_studio.services.backups import create_snapshot,delete_snapshot,list_snapshots,load_snapshot

class BackupTests(unittest.TestCase):
 def test_snapshot_create_restore_delete(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);project=Project('Demo',script='Hello',blocks=[ScriptBlock('A',text='x')])
   path=create_snapshot(project,'Before',root,keep=3);self.assertTrue(path.exists());self.assertEqual(len(list_snapshots(project.id,root)),1)
   restored=load_snapshot(path);self.assertEqual(restored.script,'Hello');self.assertEqual(restored.id,project.id)
   copy=load_snapshot(path,True);self.assertNotEqual(copy.id,project.id)
   self.assertTrue(delete_snapshot(path,project.id,root))
 def test_retention(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);project=Project('Demo')
   for i in range(5):create_snapshot(project,str(i),root,keep=3)
   self.assertEqual(len(list_snapshots(project.id,root)),3)
 def test_repeated_labels_do_not_overwrite(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);project=Project('Demo')
   first=create_snapshot(project,'same',root);second=create_snapshot(project,'same',root)
   self.assertNotEqual(first,second);self.assertTrue(first.exists());self.assertTrue(second.exists())
 def test_delete_rejects_outside_path(self):
  with tempfile.TemporaryDirectory() as folder:
   with self.assertRaises(ValueError):delete_snapshot(Path(folder)/'x.json','project',Path(folder)/'backups')
if __name__=='__main__':unittest.main()
