import hashlib,mimetypes
from abc import ABC,abstractmethod
from datetime import datetime,timezone
from peabox_voice_studio.services import object_storage
class StorageBackend(ABC):
 name='abstract'
 @abstractmethod
 def put(self,namespace,key,content,overwrite=False):...
 @abstractmethod
 def get(self,namespace,key):...
 @abstractmethod
 def exists(self,namespace,key):...
 @abstractmethod
 def delete(self,namespace,key):...
 @abstractmethod
 def list(self,namespace=None):...
 @abstractmethod
 def copy(self,source_namespace,source_key,target_namespace,target_key,overwrite=False):...
 @abstractmethod
 def move(self,source_namespace,source_key,target_namespace,target_key,overwrite=False):...
 @abstractmethod
 def audit(self):...
class LocalBackend(StorageBackend):
 name='local'
 def __init__(self,namespaces=None,manifest_path=None,lock_path=None):self.namespaces=namespaces;self.manifest_path=manifest_path or object_storage.OBJECT_MANIFEST_PATH;self.lock_path=lock_path or object_storage.OBJECT_STORAGE_LOCK_PATH
 def put(self,namespace,key,content,overwrite=False):return object_storage.put_bytes(namespace,key,content,self.namespaces,self.manifest_path,self.lock_path,overwrite)
 def get(self,namespace,key):return object_storage.get_bytes(namespace,key,self.namespaces)
 def exists(self,namespace,key):return object_storage.object_path(namespace,key,self.namespaces).is_file()
 def delete(self,namespace,key):return object_storage.delete_object(namespace,key,self.namespaces,self.manifest_path,self.lock_path)
 def list(self,namespace=None):return object_storage.list_objects(namespace,self.manifest_path)
 def copy(self,sn,sk,tn,tk,overwrite=False):return object_storage.copy_object(sn,sk,tn,tk,self.namespaces,self.manifest_path,self.lock_path,overwrite)
 def move(self,sn,sk,tn,tk,overwrite=False):return object_storage.move_object(sn,sk,tn,tk,self.namespaces,self.manifest_path,self.lock_path,overwrite)
 def audit(self):return object_storage.audit_manifest(self.namespaces,self.manifest_path)
 def rebuild(self):return object_storage.rebuild_manifest(self.namespaces,self.manifest_path,self.lock_path)
class MemoryBackend(StorageBackend):
 name='memory'
 def __init__(self):self.objects={}
 def _id(self,namespace,key):return object_storage.object_id(namespace,key)
 def _meta(self,namespace,key,content):
  stamp=datetime.now(timezone.utc).isoformat();return {'id':self._id(namespace,key),'namespace':namespace,'key':object_storage.safe_key(key),'name':object_storage.safe_key(key).split('/')[-1],'bytes':len(content),'sha256':hashlib.sha256(content).hexdigest(),'content_type':mimetypes.guess_type(key)[0] or 'application/octet-stream','created_at':stamp,'modified_at':stamp}
 def put(self,namespace,key,content,overwrite=False):
  oid=self._id(namespace,key)
  if oid in self.objects and not overwrite:raise FileExistsError('Object already exists')
  self.objects[oid]={'content':bytes(content),'meta':self._meta(namespace,key,bytes(content))};return dict(self.objects[oid]['meta'])
 def get(self,namespace,key):
  try:return self.objects[self._id(namespace,key)]['content']
  except KeyError:raise FileNotFoundError('Object not found')
 def exists(self,namespace,key):return self._id(namespace,key) in self.objects
 def delete(self,namespace,key):
  try:return self.objects.pop(self._id(namespace,key))['meta']
  except KeyError:raise FileNotFoundError('Object not found')
 def list(self,namespace=None):return sorted([dict(x['meta']) for x in self.objects.values() if namespace is None or x['meta']['namespace']==namespace],key=lambda x:(x['namespace'],x['key']))
 def copy(self,sn,sk,tn,tk,overwrite=False):return self.put(tn,tk,self.get(sn,sk),overwrite)
 def move(self,sn,sk,tn,tk,overwrite=False):meta=self.copy(sn,sk,tn,tk,overwrite);self.delete(sn,sk);return meta
 def audit(self):
  issues=[]
  for oid,item in self.objects.items():
   if len(item['content'])!=item['meta']['bytes']:issues.append({'id':oid,'issue':'size_changed'})
   elif hashlib.sha256(item['content']).hexdigest()!=item['meta']['sha256']:issues.append({'id':oid,'issue':'hash_changed'})
  return {'objects':len(self.objects),'issues':issues,'healthy':not issues}
class BackendRegistry:
 def __init__(self):self.factories={}
 def register(self,name,factory):
  if not name or not callable(factory):raise ValueError('Invalid backend registration')
  self.factories[name]=factory;return name
 def create(self,name,**kwargs):
  if name not in self.factories:raise ValueError('Unknown storage backend')
  backend=self.factories[name](**kwargs)
  if not isinstance(backend,StorageBackend):raise TypeError('Backend does not implement StorageBackend')
  return backend
 def names(self):return sorted(self.factories)
registry=BackendRegistry();registry.register('local',LocalBackend);registry.register('memory',MemoryBackend)
def migration_preview(source,target,namespace=None):
 rows=source.list(namespace);return {'source':source.name,'target':target.name,'namespace':namespace or 'All','items':[{'namespace':x['namespace'],'key':x['key'],'bytes':x['bytes'],'sha256':x['sha256']} for x in rows],'files':len(rows),'bytes':sum(x['bytes'] for x in rows)}
def migrate(preview,source,target,overwrite=False):
 completed=[];failed=[]
 for item in preview.get('items',[]):
  try:
   content=source.get(item['namespace'],item['key']);meta=target.put(item['namespace'],item['key'],content,overwrite)
   if meta['sha256']!=item['sha256']:raise IOError('Migrated object hash mismatch')
   completed.append(meta)
  except Exception as exc:failed.append({'item':item,'error':type(exc).__name__})
 return {'completed':completed,'failed':failed,'files':len(completed),'bytes':sum(x['bytes'] for x in completed)}
def contract_report(backend):
 required=('put','get','exists','delete','list','copy','move','audit');missing=[x for x in required if not callable(getattr(backend,x,None))];return {'backend':backend.name,'valid':not missing,'missing':missing}
