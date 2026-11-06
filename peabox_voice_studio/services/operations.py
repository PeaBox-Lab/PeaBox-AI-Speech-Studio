import json
from pathlib import Path
from peabox_voice_studio.config import MAX_OPERATION_LOG_BYTES,OPERATIONS_LOG_PATH
from peabox_voice_studio.models import utc_now
def record_operation(action,status='success',project_id='',details=None,path=OPERATIONS_LOG_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists() and path.stat().st_size>MAX_OPERATION_LOG_BYTES:
  rotated=path.with_suffix('.1.jsonl');rotated.unlink(missing_ok=True);path.replace(rotated)
 e={'timestamp':utc_now(),'action':action[:120],'status':status[:40],'project_id':project_id[:120],'details':details or {}}
 with path.open('a',encoding='utf-8') as f:f.write(json.dumps(e,ensure_ascii=False)+'\n')
 return e
def read_operations(limit=200,path=OPERATIONS_LOG_PATH):
 path=Path(path);rows=[]
 if not path.exists():return rows
 for line in path.read_text(encoding='utf-8',errors='replace').splitlines():
  try:rows.append(json.loads(line))
  except json.JSONDecodeError:pass
 return list(reversed(rows[-max(1,min(limit,2000)):]))
def operation_log_health(path=OPERATIONS_LOG_PATH):
 path=Path(path);return {'exists':path.exists(),'bytes':path.stat().st_size if path.exists() else 0,'entries':len(read_operations(2000,path))}
