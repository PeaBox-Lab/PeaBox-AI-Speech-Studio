import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.repository import initialize_database,list_indexed_projects,rebuild_index,remove_project,repository_health,upsert_project

class RepositoryTests(unittest.TestCase):
 def test_index_lifecycle_and_health(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);db=root/'db.sqlite';project=Project('Demo');file=root/'p.json';file.write_text('{}')
   upsert_project(project,file,db)
   rows=list_indexed_projects(db);self.assertEqual(rows[0]['id'],project.id)
   self.assertTrue(repository_health(db)['ready'])
   remove_project(project.id,db);self.assertEqual(list_indexed_projects(db),[])
 def test_rebuild(self):
  with tempfile.TemporaryDirectory() as folder:
   root=Path(folder);db=root/'db.sqlite';items=[]
   for name in ('A','B'):
    p=Project(name);path=root/f'{p.id}.json';path.write_text('{}');items.append((p,path))
   result=rebuild_index(items,db);self.assertEqual(result['indexed'],2);self.assertEqual(len(list_indexed_projects(db)),2)
if __name__=='__main__':unittest.main()
