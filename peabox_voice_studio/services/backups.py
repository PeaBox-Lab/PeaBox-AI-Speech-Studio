import json
from pathlib import Path
from uuid import uuid4

from peabox_voice_studio.config import BACKUPS_DIR, MAX_PROJECT_SNAPSHOTS
from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename
from peabox_voice_studio.services.migrations import migrate_project_payload


def create_snapshot(project: Project, label: str = "", root: Path = BACKUPS_DIR, keep: int = MAX_PROJECT_SNAPSHOTS) -> Path:
    folder = Path(root) / project.id; folder.mkdir(parents=True, exist_ok=True)
    timestamp = utc_now().replace(":", "-")
    snapshot_id = uuid4().hex
    filename = f"{timestamp}_{safe_filename(label or 'snapshot', limit=48)}_{snapshot_id[:8]}.json"
    payload = {"schema_version": 1, "snapshot_id": snapshot_id, "created_at": utc_now(), "label": label[:120], "project": project.to_dict()}
    path = folder / filename
    atomic_write_bytes(path, json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"))
    snapshots = sorted(folder.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True)
    for old in snapshots[keep:]: old.unlink(missing_ok=True)
    return path


def list_snapshots(project_id: str, root: Path = BACKUPS_DIR) -> list[dict]:
    folder = Path(root) / project_id
    if not folder.exists(): return []
    result=[]
    for path in sorted(folder.glob("*.json"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            payload=json.loads(path.read_text(encoding="utf-8"))
            result.append({"path": str(path), "name": path.name, "created_at": payload.get("created_at"), "label": payload.get("label", ""), "bytes": path.stat().st_size})
        except (OSError,json.JSONDecodeError): continue
    return result


def load_snapshot(path: Path, new_identity: bool = False) -> Project:
    payload=json.loads(Path(path).read_text(encoding="utf-8"))
    data,_=migrate_project_payload(payload.get("project"))
    project=Project.from_dict(data)
    if new_identity:
        project.id=uuid4().hex; project.name=f"{project.name} (snapshot restore)"[:120]; project.created_at=utc_now()
    project.updated_at=utc_now()
    return project


def delete_snapshot(path: Path, project_id: str, root: Path = BACKUPS_DIR) -> bool:
    candidate=Path(path).resolve(); folder=(Path(root)/project_id).resolve()
    if folder not in candidate.parents or candidate.suffix.lower() != '.json':
        raise ValueError("Snapshot path is outside the project backup folder")
    if not candidate.exists(): return False
    candidate.unlink(); return True
