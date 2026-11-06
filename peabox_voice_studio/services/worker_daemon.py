import json,os,time,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.config import WORKER_DAEMON_LOCK_PATH,WORKER_DAEMON_STATE_PATH,WORKER_EVENTS_DIR,WORKER_JOBS_DIR
from peabox_voice_studio.services.files import atomic_write_bytes
from peabox_voice_studio.services.worker_queue import list_queue,recover_stale,run_one

def now():return datetime.now(timezone.utc)
def _iso(value=None):return (value or now()).isoformat()
def default_state():return {'worker_id':'','pid':None,'mode':'stopped','started_at':'','heartbeat_at':'','updated_at':'','processed':0,'last_queue_id':'','last_error':''}
def read_state(path=WORKER_DAEMON_STATE_PATH):
 path=Path(path)
 if not path.exists():return default_state()
 try:return {**default_state(),**json.loads(path.read_text())}
 except (OSError,json.JSONDecodeError):return default_state()
def write_state(state,path=WORKER_DAEMON_STATE_PATH):state['updated_at']=_iso();atomic_write_bytes(Path(path),json.dumps(state,indent=2).encode());return state
def is_stale(state,at=None,stale_seconds=30):
 if state.get('mode')=='stopped' or not state.get('heartbeat_at'):return False
 point=at or now();return datetime.fromisoformat(state['heartbeat_at'])+timedelta(seconds=stale_seconds)<=point
def claim(worker_id=None,pid=None,state_path=WORKER_DAEMON_STATE_PATH,lock_path=WORKER_DAEMON_LOCK_PATH,at=None,stale_seconds=30):
 worker_id=worker_id or f'daemon-{uuid.uuid4().hex[:8]}';pid=pid or os.getpid();point=at or now();state=read_state(state_path);lock_path=Path(lock_path);lock_path.parent.mkdir(parents=True,exist_ok=True)
 active=state.get('mode')!='stopped' and not is_stale(state,point,stale_seconds)
 if lock_path.exists() and active:raise RuntimeError('A worker daemon is already active')
 lock_path.unlink(missing_ok=True)
 fd=os.open(lock_path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);os.write(fd,worker_id.encode());os.close(fd)
 return write_state({'worker_id':worker_id,'pid':pid,'mode':'running','started_at':_iso(point),'heartbeat_at':_iso(point),'processed':state.get('processed',0),'last_queue_id':'','last_error':''},state_path)
def heartbeat(worker_id,state_path=WORKER_DAEMON_STATE_PATH,at=None):
 state=read_state(state_path)
 if state.get('worker_id')!=worker_id:raise RuntimeError('Daemon ownership changed')
 state['heartbeat_at']=_iso(at or now());return write_state(state,state_path)
def command(mode,state_path=WORKER_DAEMON_STATE_PATH):
 if mode not in {'running','paused','draining','shutdown'}:raise ValueError('Unsupported daemon mode')
 state=read_state(state_path);state['mode']=mode;return write_state(state,state_path)
def release(worker_id,state_path=WORKER_DAEMON_STATE_PATH,lock_path=WORKER_DAEMON_LOCK_PATH):
 state=read_state(state_path)
 if state.get('worker_id') and state.get('worker_id')!=worker_id:raise RuntimeError('Daemon ownership changed')
 state['mode']='stopped';state['pid']=None;state['heartbeat_at']='';write_state(state,state_path);Path(lock_path).unlink(missing_ok=True);return state
def daemon_status(state_path=WORKER_DAEMON_STATE_PATH,at=None,stale_seconds=30):
 state=read_state(state_path);state['stale']=is_stale(state,at,stale_seconds);state['active']=state['mode']!='stopped' and not state['stale'];return state
def next_queue(queue_root=WORKER_JOBS_DIR):
 eligible=[x for x in list_queue(queue_root) if x.get('state') in {'queued','partial','failed'} and not x.get('job',{}).get('cancel_requested')]
 return sorted(eligible,key=lambda x:x.get('created_at',''))[0] if eligible else None
def run_daemon(renderers,poll_seconds=2,worker_id=None,state_path=WORKER_DAEMON_STATE_PATH,lock_path=WORKER_DAEMON_LOCK_PATH,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR,max_cycles=None,sleep=time.sleep):
 state=claim(worker_id,state_path=state_path,lock_path=lock_path);worker_id=state['worker_id'];cycles=0
 try:
  while True:
   state=read_state(state_path);mode=state.get('mode','running')
   if mode=='shutdown':break
   recover_stale(queue_root,event_root);item=next_queue(queue_root)
   if mode=='paused':heartbeat(worker_id,state_path);sleep(poll_seconds)
   elif mode=='draining' and item is None:break
   elif item is None:heartbeat(worker_id,state_path);sleep(poll_seconds)
   else:
    try:
     run_one(item['queue_id'],worker_id,renderers,queue_root,event_root);state=read_state(state_path);state['processed']=int(state.get('processed',0))+1;state['last_queue_id']=item['queue_id'];state['last_error']='';state['heartbeat_at']=_iso();write_state(state,state_path)
    except Exception as exc:
     state=read_state(state_path);state['last_error']=str(exc)[:500];state['heartbeat_at']=_iso();write_state(state,state_path)
   cycles+=1
   if max_cycles is not None and cycles>=max_cycles:break
 finally:release(worker_id,state_path,lock_path)
 return read_state(state_path)
