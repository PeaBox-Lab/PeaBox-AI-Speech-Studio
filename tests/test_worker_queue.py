import tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.worker_queue import acquire,enqueue,heartbeat,list_queue,load,progress,read_events,recover_stale,release,request_cancel,run_one,sync_to_project

def job(provider='Kokoro local',count=2):
 items=[{'id':f'i{i}','block_id':f'b{i}','position':i+1,'title':f'Item {i}','text':'hello','processed_text':'hello','provider':provider,'language':'US English','voice':'af_heart','speed':1.0,'status':'queued','attempts':0,'file':None,'error':None,'estimated_cost_usd':0.0,'recorded_usage_cost_usd':None,'actual_cost_usd':None} for i in range(count)]
 return {'id':'job1','project_id':'project1','project_name':'P','created_at':'now','updated_at':'now','status':'queued','cancel_requested':False,'items':items,'summary':{}}
class WorkerQueueTests(unittest.TestCase):
 def roots(self,d):return Path(d)/'jobs',Path(d)/'events'
 def test_enqueue_and_events(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(),q,e);self.assertEqual(load(env['queue_id'],q)['state'],'queued');self.assertEqual(read_events(env['queue_id'],event_root=e)[0]['event'],'queued')
 def test_cloud_items_are_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d)
   with self.assertRaises(ValueError):enqueue(job('Azure Speech'),q,e)
 def test_exclusive_lease_and_heartbeat(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(),q,e);acquire(env['queue_id'],'a',queue_root=q,event_root=e)
   with self.assertRaises(RuntimeError):acquire(env['queue_id'],'b',queue_root=q,event_root=e)
   heartbeat(env['queue_id'],'a',queue_root=q,event_root=e);release(env['queue_id'],'a',queue_root=q,event_root=e);self.assertIsNone(load(env['queue_id'],q)['lease'])
 def test_stale_lease_recovers_running_item(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(),q,e);past=datetime.now(timezone.utc)-timedelta(minutes=5);acquire(env['queue_id'],'a',lease_seconds=1,queue_root=q,event_root=e,at=past);current=load(env['queue_id'],q);current['job']['items'][0]['status']='running';from peabox_voice_studio.services.worker_queue import _save;_save(current,q);ids=recover_stale(q,e);self.assertEqual(ids,[env['queue_id']]);self.assertEqual(load(env['queue_id'],q)['job']['items'][0]['status'],'queued')
 def test_run_one_progress_and_sync(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);out=Path(d)/'out';out.mkdir();env=enqueue(job(),q,e)
   def renderer(item,name):p=out/f'{name}.wav';p.write_bytes(b'wav');return p
   done=run_one(env['queue_id'],'worker',{'Kokoro local':renderer},q,e);self.assertEqual(done['state'],'completed');self.assertEqual(progress(done),1.0);self.assertEqual(len([x for x in read_events(env['queue_id'],event_root=e) if x['event']=='item_finished']),2)
   p=Project(name='P',id='project1');p.settings['batch_jobs']=[job()];synced=sync_to_project(p,done);self.assertEqual(synced['status'],'completed')
 def test_renderer_failure_is_recorded(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(count=1),q,e)
   def fail(item,name):raise RuntimeError('boom')
   done=run_one(env['queue_id'],'worker',{'Kokoro local':fail},q,e);self.assertEqual(done['job']['items'][0]['status'],'failed');self.assertIn('boom',done['job']['items'][0]['error'])
 def test_cancel_marks_queued_items(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(),q,e);cancelled=request_cancel(env['queue_id'],q,e);self.assertTrue(cancelled['job']['cancel_requested']);self.assertTrue(all(x['status']=='cancelled' for x in cancelled['job']['items']))
 def test_sync_rejects_wrong_project(self):
  with tempfile.TemporaryDirectory() as d:
   q,e=self.roots(d);env=enqueue(job(),q,e)
   with self.assertRaises(ValueError):sync_to_project(Project(name='Other'),env)
if __name__=='__main__':unittest.main()
