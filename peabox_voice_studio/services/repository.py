import sqlite3
from pathlib import Path
from peabox_voice_studio.config import DATABASE_PATH
from peabox_voice_studio.models import utc_now
def init(path=DATABASE_PATH):
 p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
 with sqlite3.connect(p) as c:c.execute('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT,updated_at TEXT,status TEXT,issues INTEGER,project_path TEXT,indexed_at TEXT)')
def upsert(project,project_path,issues=0,path=DATABASE_PATH):
 init(path);status=project.settings.get('governance',{}).get('status','Draft')
 with sqlite3.connect(path) as c:c.execute('INSERT INTO projects VALUES(?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,updated_at=excluded.updated_at,status=excluded.status,issues=excluded.issues,project_path=excluded.project_path,indexed_at=excluded.indexed_at',(project.id,project.name,project.updated_at,status,issues,str(project_path),utc_now()))
def list_projects(path=DATABASE_PATH):
 init(path)
 with sqlite3.connect(path) as c:c.row_factory=sqlite3.Row;return [dict(x) for x in c.execute('SELECT * FROM projects ORDER BY updated_at DESC')]
def rebuild(items,path=DATABASE_PATH):
 init(path)
 with sqlite3.connect(path) as c:c.execute('DELETE FROM projects')
 for p,pp,i in items:upsert(p,pp,i,path)
 return len(items)
def health(path=DATABASE_PATH):
 init(path)
 with sqlite3.connect(path) as c:integrity=c.execute('PRAGMA integrity_check').fetchone()[0];count=c.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
 return {'ready':integrity=='ok','integrity':integrity,'projects':count,'bytes':Path(path).stat().st_size}
def remove(project_id,path=DATABASE_PATH):
 c=init(path)
 try:c.execute('delete from projects where id=?',(project_id,));c.commit()
 finally:c.close()
