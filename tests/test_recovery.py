import json,sqlite3,tempfile,unittest,zipfile
from io import BytesIO
from pathlib import Path
from unittest.mock import patch
from peabox_voice_studio.models import Project
from peabox_voice_studio.services import recovery
class RecoveryTests(unittest.TestCase):
 def test_inventory_and_summary(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'a.txt').write_text('abc');rows=recovery.storage_inventory({'test':root});summary=recovery.storage_summary(rows);self.assertEqual(summary['test']['files'],1);self.assertEqual(summary['test']['bytes'],3)
 def test_quarantine_and_restore_are_reversible(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);outputs=root/'outputs';q=root/'quarantine';outputs.mkdir();q.mkdir();item=outputs/'audio.wav';item.write_bytes(b'wav')
   with patch.object(recovery,'OUTPUTS_DIR',outputs),patch.object(recovery,'QUARANTINE_DIR',q):
    entry=recovery.quarantine_file(item);self.assertFalse(item.exists());self.assertTrue(Path(entry['quarantined']).exists());restored=recovery.restore_quarantine(entry['id']);self.assertTrue(Path(restored['restored_to']).exists())
 def test_quarantine_rejects_non_output_file(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);outputs=root/'outputs';outputs.mkdir();outside=root/'secret.txt';outside.write_text('x')
   with patch.object(recovery,'OUTPUTS_DIR',outputs):
    with self.assertRaises(ValueError):recovery.quarantine_file(outside)
 def test_database_backup_and_restore_with_rollback(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);db=root/'live.db';backups=root/'backups';con=sqlite3.connect(db);con.execute('create table data(value text)');con.execute("insert into data values('old')");con.commit();con.close();backup=recovery.backup_database(db,backups)
   con=sqlite3.connect(db);con.execute('delete from data');con.execute("insert into data values('new')");con.commit();con.close();result=recovery.restore_database(backup,db);con=sqlite3.connect(db);value=con.execute('select value from data').fetchone()[0];con.close();self.assertEqual(value,'old');self.assertTrue(Path(result['rollback']).exists())
 def test_invalid_database_is_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   bad=Path(d)/'bad.db';bad.write_text('not sqlite');self.assertFalse(recovery.validate_database(bad)['valid'])
   with self.assertRaises(ValueError):recovery.restore_database(bad,Path(d)/'live.db')
 def test_project_snapshot_is_metadata_only(self):
  p=Project(name='Snapshot',script='private script');raw,manifest=recovery.project_snapshot(p);z=zipfile.ZipFile(BytesIO(raw));self.assertEqual(set(z.namelist()),{'project.json','manifest.json'});self.assertFalse(manifest['includes_media']);self.assertIn('private script',z.read('project.json').decode())
 def test_support_bundle_redacts_paths_credentials_and_content(self):
  diagnostics=[{'Check':'Storage','Detail':str(recovery.BASE_DIR/'private')}];events=[{'timestamp':'now','event':'saved','project_id':'123456789','details':{'api_key':'secret','text':'private script'}}]
  raw,report=recovery.support_bundle(diagnostics,{'ready':True},[{'category':'outputs','name':'voice.wav','bytes':10,'path':'private'}],events);text=zipfile.ZipFile(BytesIO(raw)).read('support-report.json').decode();self.assertNotIn('secret',text);self.assertNotIn('private script',text);self.assertNotIn(str(recovery.BASE_DIR),text);self.assertIn('<APP_ROOT>',text);self.assertEqual(report['events'][0]['project_id'],'12345678')
if __name__=='__main__':unittest.main()
