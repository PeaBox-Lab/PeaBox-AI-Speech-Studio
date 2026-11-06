import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from peabox_voice_studio.services.object_storage import apply_migration,audit_manifest,copy_object,delete_object,get_bytes,import_file,list_objects,migration_preview,move_object,object_path,put_bytes,rebuild_manifest,safe_key
class ObjectStorageTests(unittest.TestCase):
 def env(self,d):
  root=Path(d);names={k:root/k for k in ('outputs','models','backups','quarantine','support','worker')};[p.mkdir() for p in names.values()];return names,root/'manifest.json',root/'lock'
 def test_safe_keys_reject_traversal_and_unsupported_chars(self):
  for key in ('../secret','a/../../b','/absolute','a b.wav',''):
   with self.assertRaises(ValueError):safe_key(key)
  self.assertEqual(safe_key('jobs/abc-1.json'),'jobs/abc-1.json')
 def test_put_get_manifest_and_metadata(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d)
   with patch('peabox_voice_studio.services.object_storage.ensure_capacity') as cap:
    meta=put_bytes('outputs','audio/test.wav',b'abc',ns,m,l);cap.assert_called_once()
   self.assertEqual(get_bytes('outputs','audio/test.wav',ns),b'abc');self.assertEqual(meta['bytes'],3);self.assertEqual(len(meta['sha256']),64);self.assertEqual(list_objects(manifest_path=m)[0]['id'],'outputs:audio/test.wav')
 def test_duplicate_requires_overwrite(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);put_bytes('outputs','a.bin',b'a',ns,m,l)
   with self.assertRaises(FileExistsError):put_bytes('outputs','a.bin',b'b',ns,m,l)
   put_bytes('outputs','a.bin',b'b',ns,m,l,True);self.assertEqual(get_bytes('outputs','a.bin',ns),b'b')
 def test_verified_import_copy_move_delete(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);source=Path(d)/'source.wav';source.write_bytes(b'wav');import_file('outputs','one.wav',source,ns,m,l);copy_object('outputs','one.wav','backups','copy.wav',ns,m,l);move_object('backups','copy.wav','support','moved.wav',ns,m,l);self.assertFalse(object_path('backups','copy.wav',ns).exists());self.assertTrue(object_path('support','moved.wav',ns).exists());delete_object('support','moved.wav',ns,m,l);self.assertFalse(object_path('support','moved.wav',ns).exists())
 def test_move_source_option_removes_import_source(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);source=Path(d)/'source.bin';source.write_bytes(b'x');import_file('outputs','source.bin',source,ns,m,l,True);self.assertFalse(source.exists())
 def test_rebuild_and_audit_detect_drift(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);p=ns['models']/'model.bin';p.write_bytes(b'123');rows=rebuild_manifest(ns,m,l);self.assertEqual(len(rows),1);self.assertTrue(audit_manifest(ns,m)['healthy']);p.write_bytes(b'changed');audit=audit_manifest(ns,m);self.assertFalse(audit['healthy']);self.assertIn(audit['issues'][0]['issue'],{'size_changed','hash_changed'})
 def test_missing_object_is_reported(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);put_bytes('outputs','a',b'a',ns,m,l);object_path('outputs','a',ns).unlink();self.assertEqual(audit_manifest(ns,m)['issues'][0]['issue'],'missing')
 def test_migration_preview_and_apply(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d);source=Path(d)/'legacy';source.mkdir();(source/'a.wav').write_bytes(b'a');(source/'sub').mkdir();(source/'sub'/'b.wav').write_bytes(b'bb');preview=migration_preview(source,'outputs',ns);self.assertEqual(preview['files'],2);result=apply_migration(preview,ns,m,l);self.assertEqual(result['files'],2);self.assertEqual(result['failed'],[]);self.assertTrue(object_path('outputs','sub/b.wav',ns).exists())
 def test_unknown_namespace_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   ns,m,l=self.env(d)
   with self.assertRaises(ValueError):object_path('unknown','a',ns)
if __name__=='__main__':unittest.main()
