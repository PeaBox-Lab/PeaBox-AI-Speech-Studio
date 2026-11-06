import json,os,tempfile,time,uuid
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
from peabox_voice_studio.config import RESILIENCE_PROFILES_LOCK_PATH,RESILIENCE_PROFILES_PATH
STATUSES=('Draft','In Review','Changes Requested','Approved','Active','Archived')
TRANSITIONS={'Draft':{'In Review','Archived'},'In Review':{'Changes Requested','Approved','Archived'},'Changes Requested':{'Draft','In Review','Archived'},'Approved':{'Active','Archived'},'Active':{'Approved','Archived'},'Archived':{'Draft'}}
DEFAULT_SETTINGS={'attempts':3,'delay_seconds':0.05,'backoff':2.0,'timeout_seconds':5.0,'failure_threshold':3,'recovery_seconds':30}
def now():return datetime.now(timezone.utc).isoformat()
@contextmanager
def _lock(path=RESILIENCE_PROFILES_LOCK_PATH,timeout=5):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);deadline=time.monotonic()+timeout;fd=None
 while True:
  try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
  except FileExistsError:
   if time.monotonic()>=deadline:raise TimeoutError('Resilience profiles are busy')
   time.sleep(.02)
 try:yield
 finally:
  if fd is not None:os.close(fd)
  path.unlink(missing_ok=True)
def _read(path=RESILIENCE_PROFILES_PATH):
 try:
  data=json.loads(Path(path).read_text()) if Path(path).exists() else {'schema':1,'profiles':[],'audit':[]}
  return data if isinstance(data,dict) and isinstance(data.get('profiles'),list) else {'schema':1,'profiles':[],'audit':[]}
 except (OSError,json.JSONDecodeError):return {'schema':1,'profiles':[],'audit':[]}
def _write(data,path=RESILIENCE_PROFILES_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(dir=path.parent,prefix=f'.{path.name}.',suffix='.tmp')
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 except Exception:Path(name).unlink(missing_ok=True);raise
def validate_settings(settings):
 value={**DEFAULT_SETTINGS,**(settings or {})}
 normalized={'attempts':int(value['attempts']),'delay_seconds':float(value['delay_seconds']),'backoff':float(value['backoff']),'timeout_seconds':float(value['timeout_seconds']),'failure_threshold':int(value['failure_threshold']),'recovery_seconds':int(value['recovery_seconds'])}
 if not 1<=normalized['attempts']<=10:raise ValueError('Attempts must be between 1 and 10')
 if not 0<=normalized['delay_seconds']<=60:raise ValueError('Delay must be between 0 and 60 seconds')
 if not 1<=normalized['backoff']<=10:raise ValueError('Backoff must be between 1 and 10')
 if not .1<=normalized['timeout_seconds']<=3600:raise ValueError('Timeout must be between 0.1 and 3600 seconds')
 if not 1<=normalized['failure_threshold']<=100:raise ValueError('Failure threshold must be between 1 and 100')
 if not 1<=normalized['recovery_seconds']<=86400:raise ValueError('Recovery must be between 1 and 86400 seconds')
 return normalized
def _audit(data,actor,action,profile,details=None):data.setdefault('audit',[]).append({'timestamp':now(),'actor':actor[:120],'action':action,'profile_id':profile.get('id',''),'profile_name':profile.get('name',''),'details':details or {}})
def list_profiles(path=RESILIENCE_PROFILES_PATH):return deepcopy(_read(path)['profiles'])
def audit_log(path=RESILIENCE_PROFILES_PATH):return deepcopy(_read(path).get('audit',[]))
def create_profile(name,backend,settings,actor,description='',path=RESILIENCE_PROFILES_PATH,lock_path=RESILIENCE_PROFILES_LOCK_PATH):
 if not name.strip() or not backend.strip() or not actor.strip():raise ValueError('Name, backend, and actor are required')
 profile={'id':uuid.uuid4().hex,'name':name.strip()[:120],'description':description.strip()[:1000],'backend':backend.strip()[:80],'status':'Draft','settings':validate_settings(settings),'created_at':now(),'created_by':actor.strip()[:120],'updated_at':now(),'reviewer':'','review_note':'','approved_at':'','activated_at':'','history':[]}
 with _lock(lock_path):data=_read(path);data['profiles'].append(profile);_audit(data,actor,'profile.created',profile);_write(data,path)
 return deepcopy(profile)
def _find(data,profile_id):
 for profile in data['profiles']:
  if profile.get('id')==profile_id:return profile
 raise KeyError('Resilience profile not found')
def update_profile(profile_id,settings,actor,name=None,description=None,path=RESILIENCE_PROFILES_PATH,lock_path=RESILIENCE_PROFILES_LOCK_PATH):
 with _lock(lock_path):
  data=_read(path);profile=_find(data,profile_id)
  if profile['status'] not in {'Draft','Changes Requested'}:raise ValueError('Only Draft or Changes Requested profiles can be edited')
  before=deepcopy(profile['settings']);profile['settings']=validate_settings(settings)
  if name is not None:profile['name']=name.strip()[:120] or profile['name']
  if description is not None:profile['description']=description.strip()[:1000]
  profile['updated_at']=now();profile['history'].append({'timestamp':profile['updated_at'],'actor':actor[:120],'action':'updated','before':before,'after':deepcopy(profile['settings'])});_audit(data,actor,'profile.updated',profile);_write(data,path);return deepcopy(profile)
def transition(profile_id,target,actor,note='',path=RESILIENCE_PROFILES_PATH,lock_path=RESILIENCE_PROFILES_LOCK_PATH):
 if target not in STATUSES:raise ValueError('Invalid profile status')
 with _lock(lock_path):
  data=_read(path);profile=_find(data,profile_id);current=profile['status']
  if target==current:return deepcopy(profile)
  if target not in TRANSITIONS.get(current,set()):raise ValueError(f'Transition from {current} to {target} is not allowed')
  if target=='Approved':
   if actor.strip()==profile['created_by']:raise ValueError('Reviewer must be different from profile creator')
   profile['reviewer']=actor.strip()[:120];profile['review_note']=note.strip()[:1000];profile['approved_at']=now()
  if target=='Changes Requested':profile['reviewer']=actor.strip()[:120];profile['review_note']=note.strip()[:1000]
  if target=='Active':
   for other in data['profiles']:
    if other.get('backend')==profile['backend'] and other.get('status')=='Active':other['status']='Approved';other['history'].append({'timestamp':now(),'actor':actor[:120],'action':'deactivated_for_new_active','replacement':profile['id']})
   profile['activated_at']=now()
  profile['status']=target;profile['updated_at']=now();profile['history'].append({'timestamp':profile['updated_at'],'actor':actor[:120],'action':'transition','from':current,'to':target,'note':note[:1000]});_audit(data,actor,'profile.transitioned',profile,{'from':current,'to':target});_write(data,path);return deepcopy(profile)
def active_profile(backend,path=RESILIENCE_PROFILES_PATH):return next((x for x in list_profiles(path) if x.get('backend')==backend and x.get('status')=='Active'),None)
def clone_profile(profile_id,name,actor,path=RESILIENCE_PROFILES_PATH,lock_path=RESILIENCE_PROFILES_LOCK_PATH):
 data=_read(path);source=deepcopy(_find(data,profile_id));return create_profile(name or f"{source['name']} copy",source['backend'],source['settings'],actor,source.get('description',''),path,lock_path)
def delete_draft(profile_id,actor,path=RESILIENCE_PROFILES_PATH,lock_path=RESILIENCE_PROFILES_LOCK_PATH):
 with _lock(lock_path):
  data=_read(path);profile=_find(data,profile_id)
  if profile['status']!='Draft':raise ValueError('Only Draft profiles can be deleted')
  data['profiles']=[x for x in data['profiles'] if x['id']!=profile_id];_audit(data,actor,'profile.deleted',profile);_write(data,path);return True
def profile_diff(left,right):
 keys=sorted(set(left.get('settings',{}))|set(right.get('settings',{})));return [{'setting':key,'left':left.get('settings',{}).get(key),'right':right.get('settings',{}).get(key),'changed':left.get('settings',{}).get(key)!=right.get('settings',{}).get(key)} for key in keys]
def instantiate(profile,backend):
 if not profile or profile.get('status')!='Active':raise ValueError('An Active resilience profile is required')
 from peabox_voice_studio.services.backend_resilience import CircuitBreaker,ResilientBackend,RetryPolicy
 s=validate_settings(profile['settings']);return ResilientBackend(backend,RetryPolicy(s['attempts'],s['delay_seconds'],s['backoff']),CircuitBreaker(s['failure_threshold'],s['recovery_seconds']),s['timeout_seconds'])
