import json,tempfile,unittest
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.services.worker_daemon import claim,command,daemon_status,heartbeat,read_state,release,run_daemon,write_state
from peabox_voice_studio.services.worker_queue import enqueue,load

def job():return {'id':'job','project_id':'project','project_name':'P','created_at':'now','updated_at':'now','status':'queued','cancel_requested':False,'items':[{'id':'i','block_id':'b','position':1,'title':'One','text':'hello','processed_text':'hello','provider':'Kokoro local','language':'US English','voice':'af_heart','speed':1.0,'status':'queued','attempts':0,'file':None,'error':None,'estimated_cost_usd':0.0,'recorded_usage_cost_usd':None,'actual_cost_usd':None}],'summary':{}}
class WorkerDaemonTests(unittest.TestCase):
 def paths(self,d):
  root=Path(d);return root/'state.json',root/'daemon.lock',root/'jobs',root/'events'
 def test_claim_is_exclusive_and_release_stops(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);claimed=claim('a',1,state,lock)
   with self.assertRaises(RuntimeError):claim('b',2,state,lock)
   stopped=release('a',state,lock);self.assertEqual(stopped['mode'],'stopped');self.assertFalse(lock.exists())
 def test_stale_daemon_can_be_reclaimed(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);past=datetime.now(timezone.utc)-timedelta(minutes=5);write_state({'worker_id':'old','pid':1,'mode':'running','started_at':past.isoformat(),'heartbeat_at':past.isoformat(),'processed':0,'last_queue_id':'','last_error':''},state);lock.write_text('old');claimed=claim('new',2,state,lock,stale_seconds=30);self.assertEqual(claimed['worker_id'],'new')
 def test_heartbeat_requires_owner(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);claim('a',1,state,lock);before=read_state(state)['heartbeat_at'];after=heartbeat('a',state,datetime.now(timezone.utc)+timedelta(seconds=1));self.assertNotEqual(before,after['heartbeat_at'])
   with self.assertRaises(RuntimeError):heartbeat('b',state)
 def test_control_modes_and_status(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);claim('a',1,state,lock)
   for mode in ('paused','running','draining','shutdown'):self.assertEqual(command(mode,state)['mode'],mode)
   self.assertTrue(daemon_status(state)['active']);release('a',state,lock);self.assertFalse(daemon_status(state)['active'])
 def test_daemon_processes_queue_and_updates_state(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);env=enqueue(job(),q,e);out=Path(d)/'out.wav'
   def renderer(item,name):out.write_bytes(b'wav');return out
   result=run_daemon({'Kokoro local':renderer},0,'daemon',state,lock,q,e,max_cycles=1,sleep=lambda _:None);self.assertEqual(result['mode'],'stopped');self.assertEqual(result['processed'],1);self.assertEqual(load(env['queue_id'],q)['state'],'completed')
 def test_orphan_lock_with_stopped_state_is_replaced(self):
  with tempfile.TemporaryDirectory() as d:
   state,lock,q,e=self.paths(d);write_state({'mode':'stopped'},state);lock.write_text('orphan');claimed=claim('new',2,state,lock);self.assertEqual(claimed['worker_id'],'new')
if __name__=='__main__':unittest.main()
