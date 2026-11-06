import json
from pathlib import Path
from typing import Any
from peabox_voice_studio.config import DATA_DIR
from peabox_voice_studio.services.files import atomic_write_bytes
PREFERENCES_PATH = DATA_DIR / "ui_preferences.json"
DEFAULTS = {
    "default_area": "Overview",
    "compact_navigation": False,
    "reduced_motion": False,
    "dashboard_detail": "Standard",
    "favorite_project_ids": [],
    "recent_project_ids": [],
    "recent_command_ids": [],
    "onboarding_dismissed": False,
}
def load_preferences(path: Path = PREFERENCES_PATH) -> dict[str, Any]:
    preferences = dict(DEFAULTS)
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            preferences.update({key: raw[key] for key in DEFAULTS if key in raw})
    except (OSError, json.JSONDecodeError, TypeError):
        pass
    return sanitize_preferences(preferences)
def save_preferences(preferences: dict[str, Any], path: Path = PREFERENCES_PATH) -> dict[str, Any]:
    clean = sanitize_preferences(preferences)
    atomic_write_bytes(Path(path), json.dumps(clean, ensure_ascii=False, indent=2).encode("utf-8"))
    return clean
def sanitize_preferences(preferences: dict[str, Any]) -> dict[str, Any]:
    clean = dict(DEFAULTS)
    clean["default_area"] = str(preferences.get("default_area", "Overview"))[:80]
    clean["compact_navigation"] = bool(preferences.get("compact_navigation", False))
    clean["reduced_motion"] = bool(preferences.get("reduced_motion", False))
    detail = str(preferences.get("dashboard_detail", "Standard"))
    clean["dashboard_detail"] = detail if detail in {"Compact", "Standard", "Detailed"} else "Standard"
    clean["favorite_project_ids"] = _clean_ids(preferences.get("favorite_project_ids", []), 100)
    clean["recent_project_ids"] = _clean_ids(preferences.get("recent_project_ids", []), 12)
    clean["recent_command_ids"] = _clean_command_ids(preferences.get("recent_command_ids", []), 10)
    clean["onboarding_dismissed"] = bool(preferences.get("onboarding_dismissed", False))
    return clean
def mark_project_opened(preferences: dict[str, Any], project_id: str) -> dict[str, Any]:
    recent = [item for item in preferences.get("recent_project_ids", []) if item != project_id]
    preferences["recent_project_ids"] = [project_id] + recent
    preferences.update(sanitize_preferences(preferences))
    return preferences
def toggle_favorite(preferences: dict[str, Any], project_id: str) -> bool:
    favorites = list(preferences.get("favorite_project_ids", []))
    if project_id in favorites:
        favorites.remove(project_id)
        active = False
    else:
        favorites.insert(0, project_id)
        active = True
    preferences["favorite_project_ids"] = favorites
    preferences.update(sanitize_preferences(preferences))
    return active
def resolve_projects(projects: list[Any], project_ids: list[str]) -> list[Any]:
    mapping = {project.id: project for project in projects}
    return [mapping[project_id] for project_id in project_ids if project_id in mapping]
def _clean_ids(values: Any, limit: int) -> list[str]:
    result = []
    if not isinstance(values, list):
        return result
    for value in values:
        item = str(value).strip()
        if item and item.isalnum() and item not in result:
            result.append(item)
        if len(result) >= limit:
            break
    return result
def _clean_command_ids(values: Any, limit: int) -> list[str]:
    result = []
    if not isinstance(values, list):
        return result
    for value in values:
        item = str(value).strip()[:80]
        if item and all(character.isalnum() or character in "-_" for character in item) and item not in result:
            result.append(item)
        if len(result) >= limit:
            break
    return result