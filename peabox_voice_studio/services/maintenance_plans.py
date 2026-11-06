import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.config import MAINTENANCE_PATH
from peabox_voice_studio.models import utc_now
from peabox_voice_studio.services.files import atomic_write_bytes
FREQUENCIES={'Daily':1,'Weekly':7,'Monthly':30,'Quarterly':90}
DEFAULT_TASKS=['Review repository health','Review orphaned outputs','Create database backup','Create project snapshots','Review operation log size']
def load_plans(path=MAINTENANCE_PATH):
 try:
  data=json.loads(Path(path).read_text());return data if isinstance(data,list) else []
 except (OSError,json.JSONDecodeError):return []
def save_plans(plans,path=MAINTENANCE_PATH):atomic_write_bytes(Path(path),json.dumps(plans,indent=2).encode());return plans
def create_plan(name,frequency='Weekly',tasks=None,owner='Local User'):
 if frequency not in FREQUENCIES:raise ValueError('Invalid frequency')
 now=utc_now();return {'id':uuid4().hex,'name':name.strip()[:120] or 'Maintenance plan','frequency':frequency,'tasks':tasks or list(DEFAULT_TASKS),'owner':owner.strip()[:120],'enabled':True,'created_at':now,'last_run_at':None,'next_due_at':_future(now,FREQUENCIES[frequency]),'runs':[]}
def plan_status(plan,now=None):
 now=_parse(now or utc_now());due=_parse(plan.get('next_due_at')) if plan.get('next_due_at') else None
 if not plan.get('enabled',True):return 'Disabled'
 if not due:return 'Not scheduled'
 return 'Overdue' if now>due else ('Due soon' if due-now<=timedelta(days=2) else 'Scheduled')
def complete_plan(plan,actor,results,notes=''):
 when=utc_now();plan['last_run_at']=when;plan['next_due_at']=_future(when,FREQUENCIES[plan['frequency']]);plan.setdefault('runs',[]).insert(0,{'id':uuid4().hex,'completed_at':when,'actor':actor[:120],'results':results,'notes':notes[:2000]});plan['runs']=plan['runs'][:50];return plan
def maintenance_health(plans):
 statuses=[plan_status(p) for p in plans if p.get('enabled',True)];return {'enabled':len(statuses),'overdue':statuses.count('Overdue'),'due_soon':statuses.count('Due soon'),'healthy':not any(x=='Overdue' for x in statuses)}
def retention_preview(project_snapshots,db_backups,quarantine_batches,policies):
 return {'snapshots_remove':max(0,project_snapshots-int(policies.get('snapshots_keep',20))),'database_backups_remove':max(0,db_backups-int(policies.get('database_backups_keep',10))),'quarantine_batches_remove':max(0,quarantine_batches-int(policies.get('quarantine_batches_keep',20)))}
def _future(value,days):return (_parse(value)+timedelta(days=days)).isoformat(timespec='seconds')
def _parse(value):return datetime.fromisoformat(value.replace('Z','+00:00')).astimezone(timezone.utc)
