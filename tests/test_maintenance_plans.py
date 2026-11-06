import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.maintenance_plans import complete_plan,create_plan,load_plans,maintenance_health,plan_status,retention_preview,save_plans
class PlanTests(unittest.TestCase):
 def test_create_complete_persist(self):
  plan=create_plan('Weekly','Weekly',owner='Raj');self.assertEqual(plan_status(plan),'Scheduled');complete_plan(plan,'Raj',{'A':'Complete'},'done');self.assertEqual(len(plan['runs']),1)
  with tempfile.TemporaryDirectory() as f:
   p=Path(f)/'plans.json';save_plans([plan],p);self.assertEqual(load_plans(p)[0]['name'],'Weekly')
 def test_overdue_health(self):
  plan=create_plan('D');plan['next_due_at']='2000-01-01T00:00:00+00:00';self.assertEqual(plan_status(plan),'Overdue');self.assertFalse(maintenance_health([plan])['healthy'])
 def test_retention_preview(self):
  self.assertEqual(retention_preview(25,12,30,{'snapshots_keep':20,'database_backups_keep':10,'quarantine_batches_keep':20}),{'snapshots_remove':5,'database_backups_remove':2,'quarantine_batches_remove':10})
if __name__=='__main__':unittest.main()
