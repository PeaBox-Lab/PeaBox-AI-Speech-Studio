import json,uuid
from datetime import datetime,timedelta,timezone
from pathlib import Path
from peabox_voice_studio.config import BACKUPS_DIR,MAINTENANCE_PATH,QUARANTINE_DIR,SUPPORT_DIR
from peabox_voice_studio.services.files import atomic_write_bytes

def now():return datetime.now(timezone.utc)
def iso(value):return value.astimezone(timezone.utc).isoformat()
def load(path=MAINTENANCE_PATH):
 path=Path(path)
 if not path.exists():return []
 try:
  data=json.loads(path.read_text(encoding='utf-8'));return data if isinstance(data,list) else []
 except (OSError,json.JSONDecodeError):return []
def save(plans,path=MAINTENANCE_PATH):atomic_write_bytes(Path(path),json.dumps(plans,ensure_ascii=False,indent=2).encode())
def next_due(frequency,base=None):
 base=base or now();days={'Daily':1,'Weekly':7,'Monthly':30,'Quarterly':90}.get(frequency,7);return iso(base+timedelta(days=days))
def create(name,frequency='Weekly',tasks=None):
 created=now();return {'id':uuid.uuid4().hex,'name':name.strip() or 'Maintenance plan','frequency':frequency,'tasks':tasks or ['Review project health','Review storage inventory','Create database backup','Review quarantine'],'enabled':True,'created_at':iso(created),'last_completed_at':'','next_due_at':iso(created),'history':[]}
def status(plan,at=None):
 if not plan.get('enabled',True):return 'Paused'
 due=plan.get('next_due_at')
 if not due:return 'Not scheduled'
 point=at or now()
 if isinstance(point,str):point=datetime.fromisoformat(point.replace('Z','+00:00'))
 due_at=datetime.fromisoformat(due.replace('Z','+00:00'))
 return 'Overdue' if point>due_at else 'Due'
def complete(plan,results,notes='',completed_at=None):
 completed_at=completed_at or now();entry={'completed_at':iso(completed_at),'results':results,'notes':notes};plan.setdefault('history',[]).append(entry);plan['last_completed_at']=entry['completed_at'];plan['next_due_at']=next_due(plan.get('frequency','Weekly'),completed_at);return plan
def pause(plan,value=True):plan['enabled']=not value;return plan
def _age_days(path,point):return max(0,(point-datetime.fromtimestamp(path.stat().st_mtime,timezone.utc)).days)
def retention_preview(policy=None,at=None,backup_dir=BACKUPS_DIR,quarantine_dir=QUARANTINE_DIR,support_dir=SUPPORT_DIR):
 policy={'keep_backups':5,'restored_quarantine_days':30,'support_days':14,**(policy or {})};point=at or now();candidates=[]
 backups=sorted(Path(backup_dir).glob('*.db'),key=lambda p:p.stat().st_mtime,reverse=True)
 for p in backups[max(0,int(policy['keep_backups'])):]:candidates.append({'kind':'backup','path':str(p.resolve()),'name':p.name,'bytes':p.stat().st_size,'reason':f"Beyond latest {policy['keep_backups']} backups"})
 for meta in Path(quarantine_dir).glob('*.json'):
  try:entry=json.loads(meta.read_text())
  except (OSError,json.JSONDecodeError):continue
  if entry.get('restored_at') and _age_days(meta,point)>=int(policy['restored_quarantine_days']):candidates.append({'kind':'quarantine-record','path':str(meta.resolve()),'name':meta.name,'bytes':meta.stat().st_size,'reason':f"Restored record older than {policy['restored_quarantine_days']} days"})
 for p in Path(support_dir).glob('*'):
  if p.is_file() and _age_days(p,point)>=int(policy['support_days']):candidates.append({'kind':'support-artifact','path':str(p.resolve()),'name':p.name,'bytes':p.stat().st_size,'reason':f"Support artifact older than {policy['support_days']} days"})
 return {'policy':policy,'generated_at':iso(point),'candidates':sorted(candidates,key=lambda x:(x['kind'],x['name'])),'files':len(candidates),'bytes':sum(x['bytes'] for x in candidates)}
def apply_retention(preview,backup_dir=BACKUPS_DIR,quarantine_dir=QUARANTINE_DIR,support_dir=SUPPORT_DIR):
 roots=[Path(backup_dir).resolve(),Path(quarantine_dir).resolve(),Path(support_dir).resolve()];allowed={'backup','quarantine-record','support-artifact'};removed=[];skipped=[]
 for item in preview.get('candidates',[]):
  path=Path(item.get('path','')).resolve()
  if item.get('kind') not in allowed or not any(path==r or r in path.parents for r in roots):skipped.append({'item':item,'reason':'Outside retention safety boundary'});continue
  if not path.exists() or not path.is_file():skipped.append({'item':item,'reason':'File no longer exists'});continue
  path.unlink();removed.append(item)
 return {'removed':removed,'skipped':skipped,'files':len(removed),'bytes':sum(x['bytes'] for x in removed)}
