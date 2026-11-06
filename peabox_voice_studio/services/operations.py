import json
from pathlib import Path
from peabox_voice_studio.config import OPERATIONS_LOG_PATH
from peabox_voice_studio.models import utc_now
def record(action,status='success',project_id='',details=None,path=OPERATIONS_LOG_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);entry={'timestamp':utc_now(),'action':action,'status':status,'project_id':project_id,'details':details or {}}
 with path.open('a',encoding='utf-8') as f:f.write(json.dumps(entry,ensure_ascii=False)+'\n')
 return entry
def read(limit=500,path=OPERATIONS_LOG_PATH):
 path=Path(path);rows=[]
 if not path.exists():return rows
 for line in path.read_text(errors='replace').splitlines():
  try:rows.append(json.loads(line))
  except:pass
 return list(reversed(rows[-limit:]))
