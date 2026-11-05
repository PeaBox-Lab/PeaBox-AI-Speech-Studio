from collections.abc import Callable
from pathlib import Path
from typing import Any
from uuid import uuid4

from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.services.batch import estimate_block, validate_batch
from peabox_voice_studio.services.files import safe_filename

TERMINAL_ITEM_STATES = {"rendered", "failed", "cancelled"}


def create_job(project: Project, rates: dict[str, float], configured_providers: set[str], text_processor: Callable[[str, str], str] | None = None) -> dict[str, Any]:
    validation = validate_batch(project, configured_providers)
    if not validation["ready"]:
        raise ValueError("Batch validation must pass before creating a job")
    items = []
    for index, block in enumerate(project.blocks, 1):
        if not block.enabled:
            continue
        estimate = estimate_block(block, rates)
        processed_text = text_processor(block.text, block.provider) if text_processor else block.text
        items.append({
            "id": uuid4().hex, "block_id": block.id, "position": index, "title": block.title,
            "text": block.text, "processed_text": processed_text, "provider": block.provider, "language": block.language, "voice": block.voice,
            "speed": block.speed, "status": "queued", "attempts": 0, "file": None, "error": None,
            "estimated_cost_usd": estimate["estimated_cost_usd"], "actual_cost_usd": None,
        })
    return {
        "id": uuid4().hex, "schema_version": 1, "project_id": project.id, "project_name": project.name,
        "created_at": utc_now(), "updated_at": utc_now(), "status": "queued", "cancel_requested": False,
        "items": items, "summary": summarize_job_items(items),
    }


def summarize_job_items(items: list[dict]) -> dict:
    states = ("queued", "running", "rendered", "failed", "cancelled")
    summary = {state: sum(item["status"] == state for item in items) for state in states}
    summary["estimated_cost_usd"] = round(sum(float(item.get("estimated_cost_usd") or 0) for item in items), 6)
    summary["actual_cost_usd"] = round(sum(float(item.get("actual_cost_usd") or 0) for item in items), 6)
    return summary


def refresh_job_status(job: dict) -> dict:
    states = {item["status"] for item in job["items"]}
    if job.get("cancel_requested") and states.issubset(TERMINAL_ITEM_STATES):
        job["status"] = "cancelled"
    elif states == {"rendered"}:
        job["status"] = "completed"
    elif "running" in states:
        job["status"] = "running"
    elif "queued" in states:
        job["status"] = "queued"
    elif "failed" in states and "rendered" in states:
        job["status"] = "partial"
    elif states == {"failed"}:
        job["status"] = "failed"
    elif states == {"cancelled"}:
        job["status"] = "cancelled"
    else:
        job["status"] = "partial"
    job["summary"] = summarize_job_items(job["items"])
    job["updated_at"] = utc_now()
    return job


def run_job(job: dict, renderers: dict[str, Callable[..., Path]]) -> tuple[list[Path], dict]:
    files: list[Path] = []
    job["status"] = "running"
    for item in job["items"]:
        if item["status"] != "queued":
            if item["status"] == "rendered" and item.get("file"):
                path = Path(item["file"])
                if path.exists(): files.append(path)
            continue
        if job.get("cancel_requested"):
            item["status"] = "cancelled"
            continue
        renderer = renderers.get(item["provider"])
        if renderer is None:
            item["status"] = "failed"; item["error"] = "Provider is not configured for this session"; continue
        item["status"] = "running"; item["attempts"] += 1; item["error"] = None
        output_name = f"{item['position']:03}_{safe_filename(item['title'])}"
        try:
            render_item = dict(item)
            render_item["text"] = item.get("processed_text", item["text"])
            path = renderer(render_item, output_name)
            item["status"] = "rendered"; item["file"] = str(path)
            item["actual_cost_usd"] = item["estimated_cost_usd"]
            files.append(path)
        except Exception as exc:
            item["status"] = "failed"; item["error"] = str(exc)[:500]
    return files, refresh_job_status(job)


def retry_failed(job: dict) -> dict:
    for item in job["items"]:
        if item["status"] == "failed":
            item["status"] = "queued"; item["error"] = None
    job["cancel_requested"] = False
    return refresh_job_status(job)


def request_cancel(job: dict) -> dict:
    job["cancel_requested"] = True
    for item in job["items"]:
        if item["status"] == "queued": item["status"] = "cancelled"
    return refresh_job_status(job)


def add_job(project: Project, job: dict, keep: int = 20) -> None:
    jobs = project.settings.setdefault("batch_jobs", [])
    jobs.insert(0, job)
    del jobs[keep:]


def replace_job(project: Project, job: dict) -> None:
    jobs = project.settings.setdefault("batch_jobs", [])
    for index, existing in enumerate(jobs):
        if existing.get("id") == job.get("id"):
            jobs[index] = job
            return
    jobs.insert(0, job)


def duplicate_job(job: dict) -> dict:
    import copy
    duplicate = copy.deepcopy(job)
    duplicate["id"] = uuid4().hex
    duplicate["created_at"] = utc_now()
    duplicate["updated_at"] = duplicate["created_at"]
    duplicate["status"] = "queued"
    duplicate["cancel_requested"] = False
    for item in duplicate["items"]:
        item["id"] = uuid4().hex
        item["status"] = "queued"
        item["attempts"] = 0
        item["file"] = None
        item["error"] = None
        item["actual_cost_usd"] = None
    duplicate["summary"] = summarize_job_items(duplicate["items"])
    return duplicate


def reopen_cancelled(job: dict) -> dict:
    for item in job["items"]:
        if item["status"] == "cancelled":
            item["status"] = "queued"
            item["error"] = None
    job["cancel_requested"] = False
    return refresh_job_status(job)


def delete_job(project: Project, job_id: str) -> bool:
    jobs = project.settings.setdefault("batch_jobs", [])
    before = len(jobs)
    project.settings["batch_jobs"] = [job for job in jobs if job.get("id") != job_id]
    return len(project.settings["batch_jobs"]) < before
