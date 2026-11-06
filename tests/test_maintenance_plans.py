import tempfile,unittest
from pathlib import Path
from peabox_voice_studio.services.maintenance_plans import complete,create,load,save,status
class PlanTests(unittest.TestCase):
 def test_plan_lifecycle(self):
  p=create('Weekly');self.assertEqual(status(p),'Scheduled');complete(p,{'x':'Complete'},'done');self.assertEqual(len(p['runs']),1)
  with tempfile.TemporaryDirectory() as d:path=Path(d)/'m.json';save([p],path);self.assertEqual(load(path)[0]['name'],'Weekly')
 def test_overdue(self):
  p=create('Old');p['next_due_at']='2000-01-01T00:00:00+00:00';self.assertEqual(status(p),'Overdue')
if __name__=='__main__':unittest.main()
