import json,uuid
from datetime import datetime,timedelta,timezone
from peabox_voice_studio.config import MAINTENANCE_PATH
from peabox_voice_studio.services.files import atomic_write_bytes

def now():return datetime.now(timezone.utc).isoformat()
def load():
    if not MAINTENANCE_PATH.exists():return []
    try:
        data=json.loads(MAINTENANCE_PATH.read_text());return data if isinstance(data,list) else []
    except Exception:return []
def save(plans):atomic_write_bytes(MAINTENANCE_PATH,json.dumps(plans,ensure_ascii=False,indent=2).encode())
def create(name,frequency,tasks=None):return {'id':uuid.uuid4().hex,'name':name.strip() or 'Maintenance plan','frequency':frequency,'tasks':tasks or ['Review project health','Review storage and backups','Review operations log'],'enabled':True,'last_completed_at':'','next_due_at':now(),'history':[]}
def status(plan,at=None):
    if not plan.get('enabled',True):return 'Paused'
    due=plan.get('next_due_at','')
    if not due:return 'Not scheduled'
    current=at or datetime.now(timezone.utc)
    if isinstance(current,str):current=datetime.fromisoformat(current.replace('Z','+00:00'))
    return 'Overdue' if current>datetime.fromisoformat(due.replace('Z','+00:00')) else 'Due'
def complete(plan,results,notes=''):
    completed=datetime.now(timezone.utc);days={'Daily':1,'Weekly':7,'Monthly':30,'Quarterly':90}.get(plan.get('frequency'),7)
    plan['last_completed_at']=completed.isoformat();plan['next_due_at']=(completed+timedelta(days=days)).isoformat();plan.setdefault('history',[]).append({'completed_at':completed.isoformat(),'results':results,'notes':notes});return plan
