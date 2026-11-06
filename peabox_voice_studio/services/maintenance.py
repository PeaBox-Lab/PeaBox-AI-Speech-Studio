import json,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.config import BACKUPS_DIR,MAINTENANCE_PATH,QUARANTINE_DIR,SUPPORT_DIR
from peabox_voice_studio.services.files import atomic_write_bytes
def now():return datetime.now(timezone.utc)
def load(path=MAINTENANCE_PATH):
 try:return json.loads(Path(path).read_text()) if Path(path).exists() else []
 except (OSError,json.JSONDecodeError):return []
def save(plans,path=MAINTENANCE_PATH):atomic_write_bytes(Path(path),json.dumps(plans,indent=2).encode())
def create(name,frequency='Weekly'):return {'id':uuid.uuid4().hex,'name':name or 'Maintenance plan','frequency':frequency,'tasks':['Review project health','Review storage','Create backup'],'enabled':True,'next_due_at':now().isoformat(),'history':[],'last_completed_at':''}
def status(plan,at=None):
 if not plan.get('enabled',True):return 'Paused'
 point=at or now();point=datetime.fromisoformat(point) if isinstance(point,str) else point;return 'Overdue' if point>datetime.fromisoformat(plan['next_due_at']) else 'Due'
def complete(plan,notes=''):
 point=now();days={'Daily':1,'Weekly':7,'Monthly':30,'Quarterly':90}.get(plan['frequency'],7);plan['last_completed_at']=point.isoformat();plan['next_due_at']=(point+timedelta(days=days)).isoformat();plan['history'].append({'completed_at':point.isoformat(),'notes':notes});return plan
def retention_preview(keep=5,backup_dir=BACKUPS_DIR,quarantine_dir=QUARANTINE_DIR,support_dir=SUPPORT_DIR):
 candidates=[];backups=sorted(Path(backup_dir).glob('*.db'),key=lambda p:p.stat().st_mtime,reverse=True)
 for p in backups[keep:]:candidates.append({'kind':'backup','path':str(p.resolve()),'name':p.name,'bytes':p.stat().st_size})
 return {'candidates':candidates,'files':len(candidates),'bytes':sum(x['bytes'] for x in candidates)}
def apply_retention(preview,roots=(BACKUPS_DIR,QUARANTINE_DIR,SUPPORT_DIR)):
 roots=[Path(x).resolve() for x in roots];removed=[];skipped=[]
 for item in preview['candidates']:
  p=Path(item['path']).resolve()
  if not any(r in p.parents for r in roots) or not p.is_file():skipped.append(item);continue
  p.unlink();removed.append(item)
 return {'removed':removed,'skipped':skipped}
