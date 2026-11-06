import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from peabox_voice_studio.config import DATABASE_BACKUPS_DIR, DATABASE_PATH, MAX_DATABASE_BACKUPS
from peabox_voice_studio.models import Project, utc_now

SCHEMA_VERSION = 1


def initialize_database(path: Path = DATABASE_PATH) -> None:
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Draft',
            risk_level TEXT NOT NULL DEFAULT 'Low',
            block_count INTEGER NOT NULL DEFAULT 0,
            clip_count INTEGER NOT NULL DEFAULT 0,
            job_count INTEGER NOT NULL DEFAULT 0,
            transcript_count INTEGER NOT NULL DEFAULT 0,
            project_path TEXT NOT NULL,
            indexed_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_projects_updated ON projects(updated_at DESC);
        """)
        connection.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('schema_version',?)", (str(SCHEMA_VERSION),))


def upsert_project(project: Project, project_path: Path, path: Path = DATABASE_PATH) -> None:
    initialize_database(path)
    governance = project.settings.get("governance", {})
    values = (
        project.id, project.name, project.description, project.created_at, project.updated_at,
        governance.get("status", "Draft"), governance.get("risk_level", "Low"),
        len(project.blocks), len(project.settings.get("audio_clips", [])), len(project.settings.get("batch_jobs", [])),
        len(project.settings.get("transcript_sessions", [])), str(Path(project_path)), utc_now(),
    )
    with _connect(path) as connection:
        connection.execute("""
        INSERT INTO projects(id,name,description,created_at,updated_at,status,risk_level,block_count,clip_count,job_count,transcript_count,project_path,indexed_at)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name, description=excluded.description, created_at=excluded.created_at, updated_at=excluded.updated_at,
          status=excluded.status, risk_level=excluded.risk_level, block_count=excluded.block_count, clip_count=excluded.clip_count,
          job_count=excluded.job_count, transcript_count=excluded.transcript_count, project_path=excluded.project_path, indexed_at=excluded.indexed_at
        """, values)


def remove_project(project_id: str, path: Path = DATABASE_PATH) -> None:
    initialize_database(path)
    with _connect(path) as connection:
        connection.execute("DELETE FROM projects WHERE id=?", (project_id,))


def list_indexed_projects(path: Path = DATABASE_PATH) -> list[dict]:
    initialize_database(path)
    with _connect(path) as connection:
        connection.row_factory = sqlite3.Row
        return [dict(row) for row in connection.execute("SELECT * FROM projects ORDER BY updated_at DESC")]


def rebuild_index(projects: Iterable[tuple[Project, Path]], path: Path = DATABASE_PATH) -> dict:
    initialize_database(path)
    projects = list(projects)
    with _connect(path) as connection:
        connection.execute("DELETE FROM projects")
    for project, project_path in projects:
        upsert_project(project, project_path, path)
    return {"indexed": len(projects), "rebuilt_at": utc_now()}


def repository_health(path: Path = DATABASE_PATH) -> dict:
    initialize_database(path)
    with _connect(path) as connection:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        schema = connection.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        projects = connection.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
    return {"ready": integrity == "ok", "integrity": integrity, "schema_version": int(schema[0]) if schema else None, "indexed_projects": projects, "database_path": str(path), "bytes": Path(path).stat().st_size if Path(path).exists() else 0}


@contextmanager
def _connect(path: Path):
    connection = sqlite3.connect(path, timeout=10)
    try:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def backup_database(destination: Path, path: Path = DATABASE_PATH) -> Path:
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    initialize_database(path)
    source=sqlite3.connect(path,timeout=10);target=sqlite3.connect(destination)
    try:
        source.backup(target);target.commit()
    finally:
        target.close();source.close()
    return destination


def restore_database(backup: Path, path: Path = DATABASE_PATH) -> dict:
    backup=Path(backup);path=Path(path)
    if not backup.exists():raise FileNotFoundError("Database backup not found")
    with sqlite3.connect(backup) as check:
        integrity=check.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity!='ok':raise ValueError("Database backup failed integrity check")
    temporary=path.with_suffix('.restore.tmp')
    temporary.unlink(missing_ok=True)
    source=sqlite3.connect(backup);target=sqlite3.connect(temporary)
    try:source.backup(target);target.commit()
    finally:target.close();source.close()
    with sqlite3.connect(temporary) as check:
        if check.execute("PRAGMA integrity_check").fetchone()[0]!='ok':raise ValueError("Restored database failed integrity check")
    for suffix in ("-wal","-shm"):
        Path(str(path)+suffix).unlink(missing_ok=True)
    temporary.replace(path)
    return repository_health(path)


def optimize_database(path: Path = DATABASE_PATH) -> dict:
    initialize_database(path)
    before=Path(path).stat().st_size
    with _connect(path) as connection:
        connection.execute("PRAGMA optimize")
        connection.execute("VACUUM")
    return {"before_bytes":before,"after_bytes":Path(path).stat().st_size,"optimized_at":utc_now()}


def create_database_backup(root: Path = DATABASE_BACKUPS_DIR, path: Path = DATABASE_PATH, keep: int = MAX_DATABASE_BACKUPS) -> Path:
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    base=f"peabox_{utc_now().replace(':','-')}"
    destination=root/f"{base}.db";counter=2
    while destination.exists():destination=root/f"{base}_{counter}.db";counter+=1
    backup_database(destination,path)
    backups=sorted(root.glob("*.db"),key=lambda item:item.stat().st_mtime,reverse=True)
    for old in backups[keep:]:old.unlink(missing_ok=True)
    return destination


def list_database_backups(root: Path = DATABASE_BACKUPS_DIR) -> list[dict]:
    root=Path(root)
    if not root.exists():return []
    return [{"path":str(item),"name":item.name,"bytes":item.stat().st_size,"modified":item.stat().st_mtime} for item in sorted(root.glob("*.db"),key=lambda item:item.stat().st_mtime,reverse=True)]
