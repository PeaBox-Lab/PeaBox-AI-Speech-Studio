import copy,json,os,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.config import WORKER_EVENTS_DIR,WORKER_JOBS_DIR
from peabox_voice_studio.services.files import FileLock,atomic_write_bytes
from peabox_voice_studio.services.jobs import refresh_job_status

def now():return datetime.now(timezone.utc)
def _iso(value=None):return (value or now()).isoformat()
def _job_path(queue_id,root=WORKER_JOBS_DIR):return Path(root)/f'{queue_id}.json'
def _event_path(queue_id,root=WORKER_EVENTS_DIR):return Path(root)/f'{queue_id}.jsonl'
def _save(envelope,root=WORKER_JOBS_DIR):
 path=_job_path(envelope['queue_id'],root);path.parent.mkdir(parents=True,exist_ok=True)
 with FileLock(path.with_suffix('.lock')):atomic_write_bytes(path,json.dumps(envelope,ensure_ascii=False,indent=2).encode())
 return envelope
def load(queue_id,root=WORKER_JOBS_DIR):return json.loads(_job_path(queue_id,root).read_text())
def list_queue(root=WORKER_JOBS_DIR):
 rows=[]
 for path in Path(root).glob('*.json'):
  try:rows.append(json.loads(path.read_text()))
  except (OSError,json.JSONDecodeError):continue
 return sorted(rows,key=lambda x:x.get('created_at',''),reverse=True)
def append_event(queue_id,event,details=None,event_root=WORKER_EVENTS_DIR):
 path=_event_path(queue_id,event_root);path.parent.mkdir(parents=True,exist_ok=True);row={'timestamp':_iso(),'event':event,'details':details or {}}
 with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 return row
def read_events(queue_id,limit=500,event_root=WORKER_EVENTS_DIR):
 path=_event_path(queue_id,event_root)
 if not path.exists():return []
 rows=[]
 for line in path.read_text().splitlines()[-limit:]:
  try:rows.append(json.loads(line))
  except json.JSONDecodeError:continue
 return rows
def enqueue(job,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR):
 if any(item.get('provider')!='Kokoro local' for item in job.get('items',[]) if item.get('status')=='queued'):raise ValueError('Local worker queue supports Kokoro local items only; cloud credentials remain session-only')
 queue_id=uuid.uuid4().hex;worker_job=copy.deepcopy(job);worker_job['status']='queued';worker_job['cancel_requested']=False
 envelope={'queue_id':queue_id,'job_id':job['id'],'project_id':job['project_id'],'created_at':_iso(),'updated_at':_iso(),'state':'queued','progress':0.0,'lease':None,'job':worker_job,'last_error':''}
 _save(envelope,queue_root);append_event(queue_id,'queued',{'job_id':job['id']},event_root);return envelope
def request_cancel(queue_id,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR):
 envelope=load(queue_id,queue_root);envelope['job']['cancel_requested']=True
 for item in envelope['job']['items']:
  if item['status']=='queued':item['status']='cancelled'
 refresh_job_status(envelope['job']);envelope['state']='cancel_requested' if envelope['job']['status'] not in {'cancelled','completed'} else envelope['job']['status'];envelope['updated_at']=_iso();_save(envelope,queue_root);append_event(queue_id,'cancel_requested',{},event_root);return envelope
def acquire(queue_id,worker_id,lease_seconds=120,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR,at=None):
 envelope=load(queue_id,queue_root);point=at or now();lease=envelope.get('lease')
 if lease and datetime.fromisoformat(lease['expires_at'])>point and lease['worker_id']!=worker_id:raise RuntimeError('Queue item is leased by another worker')
 envelope['lease']={'worker_id':worker_id,'acquired_at':_iso(point),'expires_at':_iso(point+timedelta(seconds=lease_seconds))};envelope['state']='running';envelope['updated_at']=_iso(point);_save(envelope,queue_root);append_event(queue_id,'lease_acquired',{'worker_id':worker_id},event_root);return envelope
def heartbeat(queue_id,worker_id,lease_seconds=120,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR,at=None):
 envelope=load(queue_id,queue_root);lease=envelope.get('lease')
 if not lease or lease['worker_id']!=worker_id:raise RuntimeError('Worker does not own lease')
 point=at or now();lease['expires_at']=_iso(point+timedelta(seconds=lease_seconds));envelope['updated_at']=_iso(point);_save(envelope,queue_root);append_event(queue_id,'heartbeat',{'worker_id':worker_id},event_root);return envelope
def release(queue_id,worker_id,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR):
 envelope=load(queue_id,queue_root);lease=envelope.get('lease')
 if lease and lease['worker_id']!=worker_id:raise RuntimeError('Worker does not own lease')
 envelope['lease']=None;envelope['updated_at']=_iso();_save(envelope,queue_root);append_event(queue_id,'lease_released',{'worker_id':worker_id},event_root);return envelope
def recover_stale(queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR,at=None):
 point=at or now();recovered=[]
 for envelope in list_queue(queue_root):
  lease=envelope.get('lease')
  if lease and datetime.fromisoformat(lease['expires_at'])<=point and envelope['state']=='running':
   envelope['lease']=None;envelope['state']='queued';envelope['updated_at']=_iso(point)
   for item in envelope['job']['items']:
    if item['status']=='running':item['status']='queued';item['error']='Recovered after stale worker lease'
   refresh_job_status(envelope['job']);_save(envelope,queue_root);append_event(envelope['queue_id'],'stale_lease_recovered',{},event_root);recovered.append(envelope['queue_id'])
 return recovered
def progress(envelope):
 items=envelope['job'].get('items',[])
 if not items:return 1.0
 terminal=sum(x.get('status') in {'rendered','failed','cancelled'} for x in items);return round(terminal/len(items),4)
def run_one(queue_id,worker_id,renderers,queue_root=WORKER_JOBS_DIR,event_root=WORKER_EVENTS_DIR):
 envelope=acquire(queue_id,worker_id,queue_root=queue_root,event_root=event_root);job=envelope['job']
 try:
  for item in job['items']:
   current=load(queue_id,queue_root)
   if current['job'].get('cancel_requested'):job=current['job'];break
   if item['status']!='queued':continue
   renderer=renderers.get(item['provider']);item['status']='running';item['attempts']+=1;item['error']=None;envelope['job']=job;envelope['progress']=progress(envelope);_save(envelope,queue_root);append_event(queue_id,'item_started',{'item_id':item['id'],'title':item['title']},event_root)
   if not renderer:item['status']='failed';item['error']='Provider renderer unavailable'
   else:
    try:
     output=renderer({**item,'text':item.get('processed_text',item['text'])},f"{item['position']:03}_{item['title']}");item['status']='rendered';item['file']=str(output);item['recorded_usage_cost_usd']=item['estimated_cost_usd']
    except Exception as exc:item['status']='failed';item['error']=str(exc)[:500]
   refresh_job_status(job);envelope['job']=job;envelope['progress']=progress(envelope);envelope['updated_at']=_iso();_save(envelope,queue_root);append_event(queue_id,'item_finished',{'item_id':item['id'],'status':item['status']},event_root)
  refresh_job_status(job);envelope['job']=job;envelope['progress']=progress(envelope);envelope['state']='completed' if job['status']=='completed' else job['status'];envelope['lease']=None;envelope['updated_at']=_iso();_save(envelope,queue_root);append_event(queue_id,'worker_finished',{'state':envelope['state']},event_root);return envelope
 except Exception as exc:
  envelope['state']='failed';envelope['last_error']=str(exc)[:500];envelope['lease']=None;_save(envelope,queue_root);append_event(queue_id,'worker_failed',{'error':type(exc).__name__},event_root);raise
def sync_to_project(project,envelope):
 if project.id!=envelope['project_id']:raise ValueError('Queue item belongs to another project')
 jobs=project.settings.setdefault('batch_jobs',[])
 for i,job in enumerate(jobs):
  if job.get('id')==envelope['job_id']:jobs[i]=copy.deepcopy(envelope['job']);return jobs[i]
 jobs.insert(0,copy.deepcopy(envelope['job']));return jobs[0]
