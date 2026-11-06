import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.config import MAINTENANCE_PATH
from peabox_voice_studio.services.files import atomic_write_bytes
from peabox_voice_studio.models import utc_now
FREQ={'Daily':1,'Weekly':7,'Monthly':30,'Quarterly':90}
def load(path=MAINTENANCE_PATH):
 try:return json.loads(Path(path).read_text())
 except:return []
def save(plans,path=MAINTENANCE_PATH):atomic_write_bytes(Path(path),json.dumps(plans,indent=2).encode());return plans
def create(name,frequency='Weekly'):
 now=utc_now();return {'id':uuid4().hex,'name':name or 'Maintenance','frequency':frequency,'tasks':['Review repository health','Run project health checks','Review missing/orphaned assets','Create backup'],'created_at':now,'next_due_at':future(now,FREQ[frequency]),'last_run_at':None,'runs':[],'enabled':True}
def status(plan,now=None):
 if not plan.get('enabled',True):return 'Disabled'
 n=parse(now or utc_now());d=parse(plan['next_due_at']);return 'Overdue' if n>d else ('Due soon' if d-n<=timedelta(days=2) else 'Scheduled')
def complete(plan,results,notes=''):
 now=utc_now();plan['last_run_at']=now;plan['next_due_at']=future(now,FREQ[plan['frequency']]);plan['runs'].insert(0,{'at':now,'results':results,'notes':notes});plan['runs']=plan['runs'][:50];return plan
def future(v,d):return (parse(v)+timedelta(days=d)).isoformat(timespec='seconds')
def parse(v):return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
