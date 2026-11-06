import json,os,tempfile,time,uuid
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path
from peabox_voice_studio.config import BACKUPS_DIR,MODELS_DIR,OUTPUTS_DIR,QUARANTINE_DIR,STORAGE_POLICY_LOCK_PATH,STORAGE_POLICY_PATH,STORAGE_RESERVATIONS_PATH,SUPPORT_DIR,WORKER_DIR
DEFAULT_POLICY={'enabled':True,'warning_percent':80,'categories':{'outputs':5*1024**3,'models':4*1024**3,'recovery':2*1024**3,'worker':512*1024**2}}
ROOTS={'outputs':(OUTPUTS_DIR,),'models':(MODELS_DIR,),'recovery':(BACKUPS_DIR,QUARANTINE_DIR,SUPPORT_DIR),'worker':(WORKER_DIR,)}
def _atomic_json(path,payload):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(dir=path.parent,prefix=f'.{path.name}.',suffix='.tmp')
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(payload,f,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 except Exception:Path(name).unlink(missing_ok=True);raise
@contextmanager
def _lock(path=STORAGE_POLICY_LOCK_PATH,timeout=5):
 path=Path(path);deadline=time.monotonic()+timeout;fd=None
 while True:
  try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
  except FileExistsError:
   if time.monotonic()>=deadline:raise TimeoutError('Storage policy is busy')
   time.sleep(.02)
 try:yield
 finally:
  if fd is not None:os.close(fd)
  path.unlink(missing_ok=True)
def load_policy(path=STORAGE_POLICY_PATH):
 path=Path(path)
 if not path.exists():return json.loads(json.dumps(DEFAULT_POLICY))
 try:data=json.loads(path.read_text());return {'enabled':bool(data.get('enabled',True)),'warning_percent':max(1,min(99,int(data.get('warning_percent',80)))),'categories':{**DEFAULT_POLICY['categories'],**{k:max(0,int(v)) for k,v in data.get('categories',{}).items()}}}
 except (OSError,json.JSONDecodeError,TypeError,ValueError):return json.loads(json.dumps(DEFAULT_POLICY))
def save_policy(policy,path=STORAGE_POLICY_PATH):
 normalized={'enabled':bool(policy.get('enabled',True)),'warning_percent':max(1,min(99,int(policy.get('warning_percent',80)))),'categories':{k:max(0,int(policy.get('categories',{}).get(k,v))) for k,v in DEFAULT_POLICY['categories'].items()}};_atomic_json(path,normalized);return normalized
def category_for(path,roots=None):
 path=Path(path).resolve();roots=roots or ROOTS
 for category,items in roots.items():
  for root in items:
   root=Path(root).resolve()
   if path==root or root in path.parents:return category
 return None
def usage(category,roots=None):
 roots=roots or ROOTS;seen=set();total=0;files=0
 for root in roots.get(category,()):
  root=Path(root)
  if not root.exists():continue
  for path in root.rglob('*'):
   if path.is_file() and path.resolve() not in seen:
    seen.add(path.resolve());total+=path.stat().st_size;files+=1
 return {'bytes':total,'files':files}
def _load_reservations(path=STORAGE_RESERVATIONS_PATH):
 try:return json.loads(Path(path).read_text()) if Path(path).exists() else []
 except (OSError,json.JSONDecodeError):return []
def active_reservations(category=None,path=STORAGE_RESERVATIONS_PATH):
 rows=_load_reservations(path);return [r for r in rows if category is None or r['category']==category]
def reserved_bytes(category,path=STORAGE_RESERVATIONS_PATH):return sum(int(x['bytes']) for x in active_reservations(category,path))
def capacity(category,policy=None,roots=None,reservations_path=STORAGE_RESERVATIONS_PATH):
 policy=policy or load_policy();used=usage(category,roots);limit=int(policy['categories'].get(category,0));reserved=reserved_bytes(category,reservations_path);remaining=max(0,limit-used['bytes']-reserved);percent=(used['bytes']+reserved)/limit*100 if limit else 100
 return {'category':category,'limit':limit,'used':used['bytes'],'files':used['files'],'reserved':reserved,'remaining':remaining,'percent':round(percent,2),'warning':percent>=policy['warning_percent'],'blocked':limit==0 or percent>=100}
def ensure_capacity(path,incoming_bytes,policy=None,roots=None,reservations_path=STORAGE_RESERVATIONS_PATH):
 policy=policy or load_policy();category=category_for(path,roots)
 if not category or not policy['enabled']:return {'category':category,'allowed':True}
 current=Path(path).stat().st_size if Path(path).exists() else 0;needed=max(0,int(incoming_bytes)-current);state=capacity(category,policy,roots,reservations_path)
 if needed>state['remaining']:raise OSError(f"Storage quota exceeded for {category}: need {needed} bytes, {state['remaining']} available")
 return {**state,'allowed':True,'needed':needed}
def reserve(category,bytes_required,purpose='',policy=None,roots=None,path=STORAGE_RESERVATIONS_PATH,lock_path=STORAGE_POLICY_LOCK_PATH):
 bytes_required=max(0,int(bytes_required));policy=policy or load_policy()
 with _lock(lock_path):
  state=capacity(category,policy,roots,path)
  if policy['enabled'] and bytes_required>state['remaining']:raise OSError(f"Storage quota exceeded for {category}: need {bytes_required} bytes, {state['remaining']} available")
  rows=_load_reservations(path);row={'id':uuid.uuid4().hex,'category':category,'bytes':bytes_required,'purpose':purpose[:200],'created_at':datetime.now(timezone.utc).isoformat()};rows.append(row);_atomic_json(path,rows);return row
def release_reservation(reservation_id,path=STORAGE_RESERVATIONS_PATH,lock_path=STORAGE_POLICY_LOCK_PATH):
 with _lock(lock_path):
  rows=_load_reservations(path);kept=[x for x in rows if x.get('id')!=reservation_id];_atomic_json(path,kept);return len(rows)!=len(kept)
def policy_status(policy=None,roots=None,reservations_path=STORAGE_RESERVATIONS_PATH):
 policy=policy or load_policy();return [capacity(k,policy,roots,reservations_path) for k in policy['categories']]
