import sqlite3
from peabox_voice_studio.config import DATABASE_PATH

def init(path=DATABASE_PATH):
    path.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(path);c.row_factory=sqlite3.Row
    c.execute('create table if not exists projects(id text primary key,name text,description text,updated_at text,path text,issues integer default 0)');c.commit();return c
def upsert(project,project_path,issues=0,path=DATABASE_PATH):
    c=init(path)
    try:c.execute('insert into projects values(?,?,?,?,?,?) on conflict(id) do update set name=excluded.name,description=excluded.description,updated_at=excluded.updated_at,path=excluded.path,issues=excluded.issues',(project.id,project.name,project.description,project.updated_at,str(project_path),issues));c.commit()
    finally:c.close()
def remove(project_id,path=DATABASE_PATH):
    c=init(path)
    try:c.execute('delete from projects where id=?',(project_id,));c.commit()
    finally:c.close()
def list_projects(path=DATABASE_PATH):
    c=init(path)
    try:return [dict(x) for x in c.execute('select * from projects order by updated_at desc')]
    finally:c.close()
def rebuild(items,path=DATABASE_PATH):
    c=init(path)
    try:
        c.execute('delete from projects')
        c.executemany('insert into projects values(?,?,?,?,?,?)',[(p.id,p.name,p.description,p.updated_at,str(pp),issues) for p,pp,issues in items]);c.commit()
    finally:c.close()
def health(path=DATABASE_PATH):
    try:
        c=init(path);count=c.execute('select count(*) from projects').fetchone()[0];c.close();return {'ready':True,'projects':count,'path':str(path)}
    except Exception as exc:return {'ready':False,'projects':0,'error':type(exc).__name__}
