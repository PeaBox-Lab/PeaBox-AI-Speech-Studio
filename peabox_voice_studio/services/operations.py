import json
from datetime import datetime,timezone
from peabox_voice_studio.config import OPERATIONS_LOG_PATH

def record(event,project_id='',details=None):
    OPERATIONS_LOG_PATH.parent.mkdir(parents=True,exist_ok=True)
    row={'timestamp':datetime.now(timezone.utc).isoformat(),'event':event,'project_id':project_id,'details':details or {}}
    with OPERATIONS_LOG_PATH.open('a',encoding='utf-8') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    return row
def read(limit=500):
    if not OPERATIONS_LOG_PATH.exists():return []
    rows=[]
    for line in OPERATIONS_LOG_PATH.read_text(encoding='utf-8').splitlines()[-limit:]:
        try:rows.append(json.loads(line))
        except json.JSONDecodeError:continue
    return list(reversed(rows))
