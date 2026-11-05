from copy import deepcopy

CURRENT_PROJECT_SCHEMA = 2


def migrate_project_payload(payload: dict) -> tuple[dict, list[str]]:
    if not isinstance(payload, dict):
        raise ValueError("Project payload must be an object")
    data = deepcopy(payload)
    notes = []
    schema = int(data.pop("schema_version", 1) or 1)
    if schema > CURRENT_PROJECT_SCHEMA:
        raise ValueError(f"Project schema {schema} is newer than this application supports")
    data.setdefault("settings", {})
    data.setdefault("render_history", [])
    data.setdefault("blocks", [])
    if schema < 2:
        notes.append("Migrated legacy project payload to schema 2")
    return data, notes


def rewrite_import_references(project_data: dict, new_project_id: str, preserve_asset_paths: bool = False) -> list[str]:
    notes = []
    settings = project_data.setdefault("settings", {})
    for job in settings.get("batch_jobs", []):
        if job.get("project_id") != new_project_id:
            job["project_id"] = new_project_id
            notes.append("Updated nested batch-job project reference")
        for item in job.get("items", []):
            if item.get("file") and not preserve_asset_paths:
                item["file"] = None
                if item.get("status") == "rendered":
                    item["status"] = "failed"
                    item["error"] = "Rendered output path was not portable; rerun this item"
    for clip in settings.get("audio_clips", []):
        if clip.get("file") and not preserve_asset_paths:
            clip["file"] = ""
            notes.append("Removed non-portable timeline asset path")
    return list(dict.fromkeys(notes))
