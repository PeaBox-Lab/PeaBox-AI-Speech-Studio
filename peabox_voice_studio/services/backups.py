import json
from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.config import BACKUPS_DIR,MAX_PROJECT_SNAPSHOTS
from peabox_voice_studio.models import Project,utc_now
from peabox_voice_studio.services.files import atomic_write_bytes,safe_filename
from peabox_voice_studio.services.migrations import migrate_project_payload
def create_snapshot(project,label='',root=BACKUPS_DIR,keep=MAX_PROJECT_SNAPSHOTS):
 folder=Path(root)/project.id;folder.mkdir(parents=True,exist_ok=True);sid=uuid4().hex;path=folder/f"{utc_now().replace(':','-')}_{safe_filename(label or 'snapshot',limit=48)}_{sid[:8]}.json";atomic_write_bytes(path,json.dumps({'schema_version':1,'snapshot_id':sid,'created_at':utc_now(),'label':label[:120],'project':project.to_dict()},indent=2).encode());
 for x in sorted(folder.glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True)[keep:]:x.unlink(missing_ok=True)
 return path
def list_snapshots(project_id,root=BACKUPS_DIR):
 result=[]
 for p in sorted((Path(root)/project_id).glob('*.json'),key=lambda x:x.stat().st_mtime,reverse=True):
  try:d=json.loads(p.read_text());result.append({'path':str(p),'name':p.name,'created_at':d.get('created_at'),'label':d.get('label',''),'bytes':p.stat().st_size})
  except:pass
 return result
def load_snapshot(path,new_identity=False):
 d,_=migrate_project_payload(json.loads(Path(path).read_text()).get('project'));p=Project.from_dict(d)
 if new_identity:p.id=uuid4().hex;p.name=f'{p.name} (snapshot restore)'[:120];p.created_at=utc_now()
 p.updated_at=utc_now();return p
def delete_snapshot(path,project_id,root=BACKUPS_DIR):
 p=Path(path).resolve();folder=(Path(root)/project_id).resolve()
 if folder not in p.parents:raise ValueError('Invalid snapshot path')
 p.unlink();return True
