import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable
from peabox_voice_studio.config import DATABASE_BACKUPS_DIR,DATABASE_PATH,MAX_DATABASE_BACKUPS
from peabox_voice_studio.models import Project,utc_now
SCHEMA_VERSION=1
@contextmanager
def _connect(path):
 c=sqlite3.connect(path,timeout=10)
 try:c.execute('PRAGMA journal_mode=WAL');c.execute('PRAGMA foreign_keys=ON');yield c;c.commit()
 except Exception:c.rollback();raise
 finally:c.close()
def initialize_database(path=DATABASE_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with _connect(path) as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL,updated_at TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Draft',risk_level TEXT NOT NULL DEFAULT 'Low',block_count INTEGER NOT NULL DEFAULT 0,clip_count INTEGER NOT NULL DEFAULT 0,job_count INTEGER NOT NULL DEFAULT 0,transcript_count INTEGER NOT NULL DEFAULT 0,project_path TEXT NOT NULL,indexed_at TEXT NOT NULL);CREATE INDEX IF NOT EXISTS idx_projects_updated ON projects(updated_at DESC);''')
  c.execute("INSERT OR REPLACE INTO meta VALUES('schema_version',?)",(str(SCHEMA_VERSION),))
def upsert_project(project,project_path,path=DATABASE_PATH):
 initialize_database(path);g=project.settings.get('governance',{});v=(project.id,project.name,project.description,project.created_at,project.updated_at,g.get('status','Draft'),g.get('risk_level','Low'),len(project.blocks),len(project.settings.get('audio_clips',[])),len(project.settings.get('batch_jobs',[])),len(project.settings.get('transcript_sessions',[])),str(project_path),utc_now())
 with _connect(path) as c:c.execute('''INSERT INTO projects VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,description=excluded.description,updated_at=excluded.updated_at,status=excluded.status,risk_level=excluded.risk_level,block_count=excluded.block_count,clip_count=excluded.clip_count,job_count=excluded.job_count,transcript_count=excluded.transcript_count,project_path=excluded.project_path,indexed_at=excluded.indexed_at''',v)
def remove_project(project_id,path=DATABASE_PATH):
 initialize_database(path)
 with _connect(path) as c:c.execute('DELETE FROM projects WHERE id=?',(project_id,))
def list_indexed_projects(path=DATABASE_PATH):
 initialize_database(path)
 with _connect(path) as c:c.row_factory=sqlite3.Row;return [dict(r) for r in c.execute('SELECT * FROM projects ORDER BY updated_at DESC')]
def rebuild_index(projects:Iterable,path=DATABASE_PATH):
 initialize_database(path);projects=list(projects)
 with _connect(path) as c:c.execute('DELETE FROM projects')
 for p,pp in projects:upsert_project(p,pp,path)
 return {'indexed':len(projects),'rebuilt_at':utc_now()}
def repository_health(path=DATABASE_PATH):
 initialize_database(path)
 with _connect(path) as c:
  integrity=c.execute('PRAGMA integrity_check').fetchone()[0];schema=c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone();count=c.execute('SELECT COUNT(*) FROM projects').fetchone()[0]
 return {'ready':integrity=='ok','integrity':integrity,'schema_version':int(schema[0]),'indexed_projects':count,'database_path':str(path),'bytes':Path(path).stat().st_size}
def backup_database(destination,path=DATABASE_PATH):
 initialize_database(path);destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True);s=sqlite3.connect(path);t=sqlite3.connect(destination)
 try:s.backup(t);t.commit()
 finally:t.close();s.close()
 return destination
def create_database_backup(root=DATABASE_BACKUPS_DIR,path=DATABASE_PATH,keep=MAX_DATABASE_BACKUPS):
 root=Path(root);root.mkdir(parents=True,exist_ok=True);base=f"peabox_{utc_now().replace(':','-')}";d=root/f'{base}.db';i=2
 while d.exists():d=root/f'{base}_{i}.db';i+=1
 backup_database(d,path)
 for old in sorted(root.glob('*.db'),key=lambda x:x.stat().st_mtime,reverse=True)[keep:]:old.unlink(missing_ok=True)
 return d
def list_database_backups(root=DATABASE_BACKUPS_DIR):
 return [{'path':str(x),'name':x.name,'bytes':x.stat().st_size,'modified':x.stat().st_mtime} for x in sorted(Path(root).glob('*.db'),key=lambda x:x.stat().st_mtime,reverse=True)]
def restore_database(backup,path=DATABASE_PATH):
 backup=Path(backup);path=Path(path)
 with sqlite3.connect(backup) as c:
  if c.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Database backup failed integrity check')
 temp=path.with_suffix('.restore.tmp');temp.unlink(missing_ok=True);s=sqlite3.connect(backup);t=sqlite3.connect(temp)
 try:s.backup(t);t.commit()
 finally:t.close();s.close()
 for suffix in ('-wal','-shm'):Path(str(path)+suffix).unlink(missing_ok=True)
 temp.replace(path);return repository_health(path)
def optimize_database(path=DATABASE_PATH):
 initialize_database(path);before=Path(path).stat().st_size
 with sqlite3.connect(path) as c:c.execute('PRAGMA optimize');c.execute('VACUUM')
 return {'before_bytes':before,'after_bytes':Path(path).stat().st_size,'optimized_at':utc_now()}
