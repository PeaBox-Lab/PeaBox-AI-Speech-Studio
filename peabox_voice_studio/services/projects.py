import json
from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.config import DATABASE_PATH, MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, PROJECTS_DIR
from peabox_voice_studio.models import Project, ScriptBlock, utc_now
from peabox_voice_studio.services.files import FileLock, atomic_write_bytes
from peabox_voice_studio.services.migrations import CURRENT_PROJECT_SCHEMA, migrate_project_payload, rewrite_import_references
from peabox_voice_studio.services.operations import record_operation
from peabox_voice_studio.services.repository import remove_project as remove_project_index, upsert_project
PROJECT_EXPORT_SCHEMA = CURRENT_PROJECT_SCHEMA
class ProjectStore:
    def __init__(self, root: Path = PROJECTS_DIR):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.is_default_store = self.root.resolve() == PROJECTS_DIR.resolve()
        self.index_path = DATABASE_PATH if self.is_default_store else self.root.parent / "peabox.db"
    def _path(self, project_id: str) -> Path:
        if not project_id or not project_id.isalnum():
            raise ValueError("Invalid project identifier")
        return self.root / f"{project_id}.json"
    def create(self, name: str, description: str = "") -> Project:
        if not name.strip():
            raise ValueError("Project name is required")
        return self.save(Project(name=name.strip()[:120], description=description[:2000]))
    def save(self, project: Project) -> Project:
        validate_project_limits(project)
        project.name = project.name.strip()[:120]
        if not project.name:
            raise ValueError("Project name is required")
        project.touch()
        path = self._path(project.id)
        with FileLock(path.with_suffix(".lock")):
            atomic_write_bytes(path, json.dumps(project.to_dict(), ensure_ascii=False, indent=2).encode("utf-8"))
        try:
            upsert_project(project, path, self.index_path)
            record_operation("project.saved", project_id=project.id, details={"name": project.name}) if self.is_default_store else None
        except Exception as exc:
            # JSON remains the portable source of truth; metadata indexing is recoverable.
            try: record_operation("repository.index_failed", "warning", project.id, {"error_type": type(exc).__name__}) if self.is_default_store else None
            except Exception: pass
        return project
    def load(self, project_id: str) -> Project:
        path = self._path(project_id)
        if not path.exists():
            raise FileNotFoundError("Project not found")
        return Project.from_dict(json.loads(path.read_text(encoding="utf-8")))
    def list(self) -> list[Project]:
        result = []
        for path in self.root.glob("*.json"):
            try:
                project = Project.from_dict(json.loads(path.read_text(encoding="utf-8")))
                result.append(project)
                try: upsert_project(project, path, self.index_path)
                except Exception: pass
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
        return sorted(result, key=lambda item: item.updated_at, reverse=True)
    def delete(self, project_id: str) -> None:
        self._path(project_id).unlink(missing_ok=False)
        try:
            remove_project_index(project_id, self.index_path)
            record_operation("project.deleted", project_id=project_id) if self.is_default_store else None
        except Exception: pass
    def import_project(self, raw: bytes | str, preserve_identity: bool = False) -> Project:
        text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
        payload = json.loads(text)
        if not isinstance(payload, dict):
            raise ValueError("Project JSON must contain an object")
        raw_project_data = payload.get("project", payload)
        project_data, migration_notes = migrate_project_payload(raw_project_data)
        original = Project.from_dict(project_data)
        new_id = original.id if preserve_identity and not self._path(original.id).exists() else uuid4().hex
        migration_notes.extend(rewrite_import_references(project_data, new_id, preserve_asset_paths=False))
        project = Project.from_dict(project_data)
        project.id = new_id
        project.created_at = original.created_at if new_id == original.id else utc_now()
        project.name = f"{project.name} (imported)"[:120]
        project.updated_at = utc_now()
        if migration_notes:
            project.settings["last_import_migration"] = {"at": project.updated_at, "notes": migration_notes}
        return self.save(project)
def validate_project_limits(project: Project) -> None:
    if len(project.script) > MAX_SCRIPT_CHARS:
        raise ValueError("Master script exceeds the project limit")
    if any(len(block.text) > MAX_BLOCK_CHARS for block in project.blocks):
        raise ValueError("A script block exceeds the block limit")
def export_project(project: Project) -> str:
    return json.dumps({"schema_version": PROJECT_EXPORT_SCHEMA, "exported_at": utc_now(), "project": project.to_dict()}, ensure_ascii=False, indent=2)
def split_script_into_blocks(script: str) -> list[ScriptBlock]:
    paragraphs = [part.strip() for part in script.replace("\r\n", "\n").split("\n\n") if part.strip()]
    return [ScriptBlock(title=f"Block {index}", text=text) for index, text in enumerate(paragraphs, 1)]
def move_block(blocks: list[ScriptBlock], index: int, direction: int) -> list[ScriptBlock]:
    target = index + direction
    if index < 0 or index >= len(blocks) or target < 0 or target >= len(blocks):
        return blocks
    blocks[index], blocks[target] = blocks[target], blocks[index]
    return blocks
def set_all_blocks_enabled(blocks: list[ScriptBlock], enabled: bool) -> None:
    for block in blocks:
        block.enabled = enabled