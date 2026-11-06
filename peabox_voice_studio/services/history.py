from pathlib import Path
from typing import Any
from peabox_voice_studio.models import Project, utc_now
def record_render(project: Project, provider: str, output: Path, characters: int, settings: dict[str, Any]) -> None:
    project.render_history.insert(0, {"created_at": utc_now(), "provider": provider, "output": output.name, "characters": characters, "settings": settings})
    project.render_history = project.render_history[:100]