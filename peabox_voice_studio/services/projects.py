import json
from pathlib import Path

from peabox_voice_studio.config import MAX_SCRIPT_CHARS, PROJECTS_DIR
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.files import atomic_write_bytes


class ProjectStore:
    def __init__(self, root: Path = PROJECTS_DIR):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, project_id: str) -> Path:
        if not project_id or not project_id.isalnum():
            raise ValueError("Invalid project identifier")
        return self.root / f"{project_id}.json"

    def create(self, name: str, description: str = "") -> Project:
        name = name.strip()
        if not name:
            raise ValueError("Project name is required")
        project = Project(name=name[:120], description=description[:2000])
        return self.save(project)

    def save(self, project: Project) -> Project:
        if len(project.script) > MAX_SCRIPT_CHARS:
            raise ValueError(f"Script exceeds the {MAX_SCRIPT_CHARS:,}-character project limit")
        project.name = project.name.strip()[:120]
        if not project.name:
            raise ValueError("Project name is required")
        project.touch()
        payload = json.dumps(project.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")
        atomic_write_bytes(self._path(project.id), payload)
        return project

    def load(self, project_id: str) -> Project:
        path = self._path(project_id)
        if not path.exists():
            raise FileNotFoundError("Project not found")
        return Project.from_dict(json.loads(path.read_text(encoding="utf-8")))

    def list(self) -> list[Project]:
        projects: list[Project] = []
        for path in self.root.glob("*.json"):
            try:
                projects.append(Project.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
        return sorted(projects, key=lambda item: item.updated_at, reverse=True)

    def delete(self, project_id: str) -> None:
        self._path(project_id).unlink(missing_ok=False)
