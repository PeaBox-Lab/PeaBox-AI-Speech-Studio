import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from peabox_voice_studio.config import DATABASE_PATH
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
