import json
from pathlib import Path

from peabox_voice_studio.config import MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, PROJECTS_DIR
from peabox_voice_studio.models import Project, ScriptBlock
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
        if not name.strip():
            raise ValueError("Project name is required")
        return self.save(Project(name=name.strip()[:120], description=description[:2000]))

    def save(self, project: Project) -> Project:
        if len(project.script) > MAX_SCRIPT_CHARS:
            raise ValueError("Master script exceeds the project limit")
        if any(len(block.text) > MAX_BLOCK_CHARS for block in project.blocks):
            raise ValueError("A script block exceeds the block limit")
        project.name = project.name.strip()[:120]
        if not project.name:
            raise ValueError("Project name is required")
        project.touch()
        atomic_write_bytes(self._path(project.id), json.dumps(project.to_dict(), ensure_ascii=False, indent=2).encode("utf-8"))
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
                result.append(Project.from_dict(json.loads(path.read_text(encoding="utf-8"))))
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                continue
        return sorted(result, key=lambda item: item.updated_at, reverse=True)

    def delete(self, project_id: str) -> None:
        self._path(project_id).unlink(missing_ok=False)


def split_script_into_blocks(script: str) -> list[ScriptBlock]:
    paragraphs = [part.strip() for part in script.replace("\r\n", "\n").split("\n\n") if part.strip()]
    return [ScriptBlock(title=f"Block {index}", text=text) for index, text in enumerate(paragraphs, 1)]


def move_block(blocks: list[ScriptBlock], index: int, direction: int) -> list[ScriptBlock]:
    target = index + direction
    if index < 0 or index >= len(blocks) or target < 0 or target >= len(blocks):
        return blocks
    blocks[index], blocks[target] = blocks[target], blocks[index]
    return blocks
