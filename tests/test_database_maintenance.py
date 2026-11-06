import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.repository import backup_database,create_database_backup,list_database_backups,list_indexed_projects,optimize_database,restore_database,upsert_project
class DatabaseMaintenanceTests(unittest.TestCase):
 def test_backup_restore_and_optimize(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);db=root/'live.db';backup=root/'backup.db';project=Project('A');file=root/'p.json';file.write_text('{}')
   upsert_project(project,file,db);backup_database(backup,db);self.assertTrue(backup.exists())
   from peabox_voice_studio.services.repository import remove_project
   remove_project(project.id,db);self.assertEqual(list_indexed_projects(db),[])
   health=restore_database(backup,db);self.assertTrue(health['ready']);self.assertEqual(len(list_indexed_projects(db)),1)
   result=optimize_database(db);self.assertIn('after_bytes',result)
 def test_invalid_backup_is_rejected(self):
  with tempfile.TemporaryDirectory() as folder:
   bad=Path(folder)/'bad.db';bad.write_text('bad')
   with self.assertRaises(Exception):restore_database(bad,Path(folder)/'live.db')
 def test_managed_backup_retention_and_unique_names(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);db=root/'live.db';backups=root/'backups';project=Project('A');file=root/'p.json';file.write_text('{}');upsert_project(project,file,db)
   first=create_database_backup(backups,db,keep=2);second=create_database_backup(backups,db,keep=2);third=create_database_backup(backups,db,keep=2)
   self.assertNotEqual(first,second);self.assertEqual(len(list_database_backups(backups)),2);self.assertTrue(third.exists())

if __name__=='__main__':unittest.main()
