import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.storage_backends import BackendRegistry,LocalBackend,MemoryBackend,StorageBackend,contract_report,migrate,migration_preview,registry
class StorageBackendTests(unittest.TestCase):
 def local(self,d):
  root=Path(d);ns={x:root/x for x in ('outputs','models','backups','quarantine','support','worker')};[p.mkdir() for p in ns.values()];return LocalBackend(ns,root/'manifest.json',root/'lock')
 def exercise(self,backend):
  first=backend.put('outputs','a.bin',b'a');self.assertTrue(backend.exists('outputs','a.bin'));self.assertEqual(backend.get('outputs','a.bin'),b'a');backend.copy('outputs','a.bin','backups','copy.bin');backend.move('backups','copy.bin','support','moved.bin');self.assertFalse(backend.exists('backups','copy.bin'));self.assertTrue(backend.exists('support','moved.bin'));self.assertEqual(len(backend.list()),2);self.assertTrue(backend.audit()['healthy']);backend.delete('support','moved.bin');self.assertEqual(len(backend.list()),1);return first
 def test_local_backend_contract_and_operations(self):
  with tempfile.TemporaryDirectory() as d:self.exercise(self.local(d))
 def test_memory_backend_contract_and_operations(self):self.exercise(MemoryBackend())
 def test_parity_metadata_fields(self):
  with tempfile.TemporaryDirectory() as d:
   local=self.local(d);memory=MemoryBackend();lm=local.put('outputs','a.wav',b'abc');mm=memory.put('outputs','a.wav',b'abc');self.assertEqual({k:lm[k] for k in ('id','namespace','key','name','bytes','sha256','content_type')},{k:mm[k] for k in ('id','namespace','key','name','bytes','sha256','content_type')})
 def test_duplicate_and_overwrite_parity(self):
  for backend in (MemoryBackend(),):
   backend.put('outputs','a',b'a')
   with self.assertRaises(FileExistsError):backend.put('outputs','a',b'b')
   backend.put('outputs','a',b'b',True);self.assertEqual(backend.get('outputs','a'),b'b')
 def test_memory_audit_detects_tamper(self):
  backend=MemoryBackend();meta=backend.put('outputs','a',b'a');backend.objects[meta['id']]['content']=b'changed';self.assertFalse(backend.audit()['healthy'])
 def test_registry_and_contract_report(self):
  self.assertEqual(registry.names(),['local','memory']);self.assertTrue(contract_report(registry.create('memory'))['valid'])
  with self.assertRaises(ValueError):registry.create('remote')
 def test_custom_backend_registration_requires_contract(self):
  custom=BackendRegistry();custom.register('bad',lambda:object())
  with self.assertRaises(TypeError):custom.create('bad')
 def test_migration_preview_and_apply(self):
  source=MemoryBackend();target=MemoryBackend();source.put('outputs','a',b'a');source.put('models','b',b'bb');preview=migration_preview(source,target);self.assertEqual(preview['files'],2);result=migrate(preview,source,target);self.assertEqual(result['files'],2);self.assertEqual(result['failed'],[]);self.assertEqual(target.get('models','b'),b'bb')
 def test_migration_respects_namespace_filter(self):
  source=MemoryBackend();target=MemoryBackend();source.put('outputs','a',b'a');source.put('models','b',b'b');preview=migration_preview(source,target,'outputs');self.assertEqual(preview['files'],1);self.assertEqual(preview['items'][0]['namespace'],'outputs')
 def test_migration_reports_conflict(self):
  source=MemoryBackend();target=MemoryBackend();source.put('outputs','a',b'a');target.put('outputs','a',b'existing');result=migrate(migration_preview(source,target),source,target);self.assertEqual(result['files'],0);self.assertEqual(result['failed'][0]['error'],'FileExistsError')
if __name__=='__main__':unittest.main()
