import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from peabox_voice_studio.models import Project,ScriptBlock
from peabox_voice_studio.services.health import apply_repairs,check_project,repair_preview
from peabox_voice_studio.services.maintenance_plans import complete,create,status
from peabox_voice_studio.services.operations import read,record
from peabox_voice_studio.services.repository import health,list_projects,rebuild,remove,upsert
class OperationsFoundationTests(unittest.TestCase):
 def test_repository_rebuild_and_remove(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'index.db';p=Project(name='Indexed');pp=Path(d)/'project.json';rebuild([(p,pp,2)],db);rows=list_projects(db);self.assertEqual(rows[0]['issues'],2);remove(p.id,db);self.assertEqual(list_projects(db),[])
 def test_repository_upsert_is_idempotent(self):
  with tempfile.TemporaryDirectory() as d:
   db=Path(d)/'index.db';p=Project(name='First');upsert(p,Path(d)/'p.json',path=db);p.name='Updated';upsert(p,Path(d)/'p.json',path=db);self.assertEqual(list_projects(db)[0]['name'],'Updated');self.assertTrue(health(db)['ready'])
 def test_health_preview_does_not_mutate(self):
  p=Project(name='');p.blocks=[ScriptBlock(title='Block',id='same'),ScriptBlock(title='Block',id='same')];report=check_project(p);actions=repair_preview(p,report);self.assertEqual(p.name,'');self.assertEqual(p.blocks[0].id,p.blocks[1].id);self.assertEqual(len(actions),2)
 def test_health_repairs_are_deterministic(self):
  p=Project(name='');p.blocks=[ScriptBlock(title='Block',id='same'),ScriptBlock(title='Block',id='same')];actions=repair_preview(p);apply_repairs(p,actions);self.assertEqual(p.name,'Untitled Project');self.assertNotEqual(p.blocks[0].id,p.blocks[1].id);self.assertEqual(check_project(p)['errors'],0)
 def test_maintenance_completion_advances_due_date(self):
  plan=create('Weekly review','Weekly',['Review health']);old=plan['next_due_at'];complete(plan,{'Review health':'Complete'},'done');self.assertNotEqual(plan['next_due_at'],old);self.assertEqual(len(plan['history']),1)
 def test_paused_maintenance_status(self):
  plan=create('Review','Monthly');plan['enabled']=False;self.assertEqual(status(plan),'Paused')
 def test_operations_log_round_trip(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'ops.jsonl'
   with patch('peabox_voice_studio.services.operations.OPERATIONS_LOG_PATH',path):record('project.saved','abc',{'name':'Demo'});rows=read()
   self.assertEqual(rows[0]['event'],'project.saved');self.assertEqual(rows[0]['project_id'],'abc')
if __name__=='__main__':unittest.main()
