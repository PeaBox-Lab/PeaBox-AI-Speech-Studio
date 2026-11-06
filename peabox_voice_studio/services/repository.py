import sqlite3
from peabox_voice_studio.config import DATABASE_PATH
def init(path=DATABASE_PATH):
 path.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(path);c.row_factory=sqlite3.Row;c.execute('create table if not exists projects(id text primary key,name text,updated_at text,path text)');c.commit();return c
def rebuild(items,path=DATABASE_PATH):
 c=init(path);c.execute('delete from projects');c.executemany('insert into projects values(?,?,?,?)',[(p.id,p.name,p.updated_at,str(pp)) for p,pp in items]);c.commit();c.close()
def list_projects(path=DATABASE_PATH):
 c=init(path);rows=[dict(x) for x in c.execute('select * from projects order by updated_at desc')];c.close();return rows
def health(path=DATABASE_PATH):
 try:c=init(path);n=c.execute('select count(*) from projects').fetchone()[0];c.close();return {'ready':True,'projects':n}
 except Exception:return {'ready':False,'projects':0}
