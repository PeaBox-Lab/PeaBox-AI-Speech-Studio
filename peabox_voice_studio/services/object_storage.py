import hashlib,json,mimetypes,os,re,shutil,tempfile,time,uuid
from contextlib import contextmanager
from datetime import datetime,timezone
from pathlib import Path,PurePosixPath
from peabox_voice_studio.config import BACKUPS_DIR,MODELS_DIR,OBJECT_MANIFEST_PATH,OBJECT_STORAGE_LOCK_PATH,OUTPUTS_DIR,QUARANTINE_DIR,SUPPORT_DIR,WORKER_DIR
from peabox_voice_studio.services.storage_policy import ensure_capacity
NAMESPACES={'outputs':OUTPUTS_DIR,'models':MODELS_DIR,'backups':BACKUPS_DIR,'quarantine':QUARANTINE_DIR,'support':SUPPORT_DIR,'worker':WORKER_DIR}
def now():return datetime.now(timezone.utc).isoformat()
def safe_key(key):
 original=str(key or '').replace('\\','/');raw=original.strip('/');path=PurePosixPath(raw)
 if not raw or original.startswith('/') or path.is_absolute() or any(part in {'','.', '..'} for part in path.parts):raise ValueError('Invalid object key')
 if any(not re.fullmatch(r'[A-Za-z0-9_.-]+',part) for part in path.parts):raise ValueError('Object key contains unsupported characters')
 return '/'.join(path.parts)
def object_path(namespace,key,namespaces=None):
 namespaces=namespaces or NAMESPACES
 if namespace not in namespaces:raise ValueError('Unknown object namespace')
 key=safe_key(key);root=Path(namespaces[namespace]).resolve();path=(root/Path(*PurePosixPath(key).parts)).resolve()
 if root not in path.parents:raise ValueError('Object key escapes namespace')
 return path
def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
@contextmanager
def _lock(path=OBJECT_STORAGE_LOCK_PATH,timeout=5):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);deadline=time.monotonic()+timeout;fd=None
 while True:
  try:fd=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY);break
  except FileExistsError:
   if time.monotonic()>=deadline:raise TimeoutError('Object storage manifest is busy')
   time.sleep(.02)
 try:yield
 finally:
  if fd is not None:os.close(fd)
  path.unlink(missing_ok=True)
def _load(path=OBJECT_MANIFEST_PATH):
 try:
  data=json.loads(Path(path).read_text()) if Path(path).exists() else {'schema':1,'objects':{}}
  return data if isinstance(data,dict) and isinstance(data.get('objects'),dict) else {'schema':1,'objects':{}}
 except (OSError,json.JSONDecodeError):return {'schema':1,'objects':{}}
def _save(data,path=OBJECT_MANIFEST_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(dir=path.parent,prefix=f'.{path.name}.',suffix='.tmp')
 try:
  with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(data,f,indent=2);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 except Exception:Path(name).unlink(missing_ok=True);raise
def object_id(namespace,key):return f'{namespace}:{safe_key(key)}'
def describe(namespace,key,namespaces=None):
 path=object_path(namespace,key,namespaces)
 if not path.is_file():raise FileNotFoundError('Object not found')
 stat=path.stat();return {'id':object_id(namespace,key),'namespace':namespace,'key':safe_key(key),'name':path.name,'bytes':stat.st_size,'sha256':digest(path),'content_type':mimetypes.guess_type(path.name)[0] or 'application/octet-stream','created_at':datetime.fromtimestamp(stat.st_ctime,timezone.utc).isoformat(),'modified_at':datetime.fromtimestamp(stat.st_mtime,timezone.utc).isoformat()}
def register(namespace,key,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH):
 meta=describe(namespace,key,namespaces)
 with _lock(lock_path):data=_load(manifest_path);data['objects'][meta['id']]=meta;data['updated_at']=now();_save(data,manifest_path)
 return meta
def put_bytes(namespace,key,content,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH,overwrite=False):
 path=object_path(namespace,key,namespaces)
 if path.exists() and not overwrite:raise FileExistsError('Object already exists')
 ensure_capacity(path,len(content));path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(dir=path.parent,prefix=f'.{path.name}.',suffix='.tmp')
 try:
  with os.fdopen(fd,'wb') as f:f.write(content);f.flush();os.fsync(f.fileno())
  os.replace(name,path)
 except Exception:Path(name).unlink(missing_ok=True);raise
 return register(namespace,key,namespaces,manifest_path,lock_path)
def import_file(namespace,key,source,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH,move=False,overwrite=False,verify=True):
 source=Path(source)
 if not source.is_file():raise FileNotFoundError('Import source not found')
 target=object_path(namespace,key,namespaces)
 if target.exists() and not overwrite:raise FileExistsError('Object already exists')
 ensure_capacity(target,source.stat().st_size);target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_name(f'.{target.name}.{uuid.uuid4().hex}.tmp');shutil.copy2(source,temp)
 if verify and digest(source)!=digest(temp):temp.unlink(missing_ok=True);raise IOError('Object verification failed')
 os.replace(temp,target)
 if move:source.unlink()
 return register(namespace,key,namespaces,manifest_path,lock_path)
def get_bytes(namespace,key,namespaces=None):return object_path(namespace,key,namespaces).read_bytes()
def copy_object(source_namespace,source_key,target_namespace,target_key,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH,overwrite=False):return import_file(target_namespace,target_key,object_path(source_namespace,source_key,namespaces),namespaces,manifest_path,lock_path,False,overwrite,True)
def move_object(source_namespace,source_key,target_namespace,target_key,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH,overwrite=False):
 source=object_path(source_namespace,source_key,namespaces);meta=import_file(target_namespace,target_key,source,namespaces,manifest_path,lock_path,True,overwrite,True);unregister(source_namespace,source_key,manifest_path,lock_path);return meta
def delete_object(namespace,key,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH):
 path=object_path(namespace,key,namespaces);path.unlink(missing_ok=False);return unregister(namespace,key,manifest_path,lock_path)
def unregister(namespace,key,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH):
 oid=object_id(namespace,key)
 with _lock(lock_path):data=_load(manifest_path);removed=data['objects'].pop(oid,None);data['updated_at']=now();_save(data,manifest_path)
 return removed
def list_objects(namespace=None,manifest_path=OBJECT_MANIFEST_PATH):
 rows=list(_load(manifest_path)['objects'].values());return sorted([x for x in rows if namespace is None or x['namespace']==namespace],key=lambda x:(x['namespace'],x['key']))
def rebuild_manifest(namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH):
 namespaces=namespaces or NAMESPACES;objects={}
 for namespace,root in namespaces.items():
  root=Path(root)
  if not root.exists():continue
  for path in root.rglob('*'):
   if not path.is_file():continue
   key=path.relative_to(root).as_posix();meta=describe(namespace,key,namespaces);objects[meta['id']]=meta
 data={'schema':1,'updated_at':now(),'objects':objects}
 with _lock(lock_path):_save(data,manifest_path)
 return list_objects(manifest_path=manifest_path)
def audit_manifest(namespaces=None,manifest_path=OBJECT_MANIFEST_PATH):
 namespaces=namespaces or NAMESPACES;rows=list_objects(manifest_path=manifest_path);issues=[]
 for meta in rows:
  path=object_path(meta['namespace'],meta['key'],namespaces)
  if not path.exists():issues.append({'id':meta['id'],'issue':'missing'})
  elif path.stat().st_size!=meta['bytes']:issues.append({'id':meta['id'],'issue':'size_changed'})
  elif digest(path)!=meta['sha256']:issues.append({'id':meta['id'],'issue':'hash_changed'})
 return {'objects':len(rows),'issues':issues,'healthy':not issues}
def migration_preview(source_root,namespace,namespaces=None):
 source_root=Path(source_root);items=[]
 for path in source_root.rglob('*'):
  if path.is_file():items.append({'source':str(path),'namespace':namespace,'key':path.relative_to(source_root).as_posix(),'bytes':path.stat().st_size})
 return {'items':items,'files':len(items),'bytes':sum(x['bytes'] for x in items)}
def apply_migration(preview,namespaces=None,manifest_path=OBJECT_MANIFEST_PATH,lock_path=OBJECT_STORAGE_LOCK_PATH,move=False):
 completed=[];failed=[]
 for item in preview.get('items',[]):
  try:completed.append(import_file(item['namespace'],item['key'],item['source'],namespaces,manifest_path,lock_path,move,False,True))
  except Exception as exc:failed.append({'item':item,'error':type(exc).__name__})
 return {'completed':completed,'failed':failed,'files':len(completed)}
