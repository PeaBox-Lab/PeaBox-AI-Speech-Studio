from pathlib import Path
from uuid import uuid4

from peabox_voice_studio.models import Project, utc_now


def create_comparison_record(project: Project, text: str, variants: list[dict], outputs: list[Path], metrics: list[dict]) -> dict:
    if len(variants) != 2 or len(outputs) != 2 or len(metrics) != 2:
        raise ValueError("A/B comparisons require exactly two variants")
    record = {
        "id": uuid4().hex,
        "created_at": utc_now(),
        "text": text,
        "variants": variants,
        "outputs": [path.name for path in outputs],
        "metrics": metrics,
        "preferred": None,
        "notes": "",
    }
    history = project.settings.setdefault("comparison_history", [])
    history.insert(0, record)
    del history[20:]
    return record


def set_comparison_preference(project: Project, comparison_id: str, preferred: str, notes: str = "") -> bool:
    if preferred not in {"A", "B", "Tie", ""}:
        raise ValueError("Preferred result must be A, B, Tie, or blank")
    for record in project.settings.setdefault("comparison_history", []):
        if record.get("id") == comparison_id:
            record["preferred"] = preferred or None
            record["notes"] = notes[:1000]
            return True
    return False


def delete_comparison(project: Project, comparison_id: str) -> bool:
    history = project.settings.setdefault("comparison_history", [])
    before = len(history)
    project.settings["comparison_history"] = [item for item in history if item.get("id") != comparison_id]
    return len(project.settings["comparison_history"]) < before
