from uuid import uuid4

from peabox_voice_studio.models import Project, ScriptBlock, utc_now


def list_presets(project: Project) -> list[dict]:
    return project.settings.setdefault("voice_presets", [])


def create_preset(project: Project, name: str, block: ScriptBlock) -> dict:
    if not name.strip():
        raise ValueError("Preset name is required")
    preset = {
        "id": uuid4().hex, "name": name.strip()[:80], "created_at": utc_now(),
        "provider": block.provider, "language": block.language, "voice": block.voice,
        "speed": block.speed, "notes": block.notes,
    }
    presets = list_presets(project)
    presets.insert(0, preset)
    del presets[50:]
    return preset


def apply_preset(block: ScriptBlock, preset: dict) -> None:
    for key in ("provider", "language", "voice", "speed", "notes"):
        if key in preset:
            setattr(block, key, preset[key])


def delete_preset(project: Project, preset_id: str) -> bool:
    presets = list_presets(project)
    before = len(presets)
    project.settings["voice_presets"] = [item for item in presets if item.get("id") != preset_id]
    return len(project.settings["voice_presets"]) < before
