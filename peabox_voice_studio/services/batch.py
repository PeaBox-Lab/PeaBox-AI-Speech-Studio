from pathlib import Path
from typing import Callable

from peabox_voice_studio.models import Project, ScriptBlock, utc_now
from peabox_voice_studio.services.files import safe_filename


def validate_block(block: ScriptBlock, index: int) -> list[dict]:
    issues: list[dict] = []
    if not block.title.strip():
        issues.append({"severity": "error", "block": index, "block_id": block.id, "message": "Block title is empty"})
    if block.enabled and not block.text.strip():
        issues.append({"severity": "error", "block": index, "block_id": block.id, "message": "Enabled block has no text"})
    if block.provider == "Kokoro local" and block.enabled and not block.voice.strip():
        issues.append({"severity": "error", "block": index, "block_id": block.id, "message": "Local block has no voice"})
    if block.enabled and block.provider != "Kokoro local":
        issues.append({"severity": "warning", "block": index, "block_id": block.id, "message": "Cloud block will be skipped by the local renderer"})
    return issues


def validate_batch(project: Project) -> dict:
    issues = [issue for index, block in enumerate(project.blocks, 1) for issue in validate_block(block, index)]
    enabled = [block for block in project.blocks if block.enabled]
    if not project.blocks:
        issues.append({"severity": "error", "block": None, "block_id": None, "message": "Project has no script blocks"})
    elif not enabled:
        issues.append({"severity": "error", "block": None, "block_id": None, "message": "No blocks are enabled"})
    errors = sum(issue["severity"] == "error" for issue in issues)
    warnings = sum(issue["severity"] == "warning" for issue in issues)
    return {"ready": errors == 0, "errors": errors, "warnings": warnings, "issues": issues}


def estimate_block(block: ScriptBlock, rates: dict[str, float]) -> dict:
    characters = len(block.text)
    words = len(block.text.split())
    rate = rates.get(block.provider, 0.0)
    return {"id": block.id, "title": block.title, "provider": block.provider, "voice": block.voice, "characters": characters, "words": words, "estimated_minutes": round(words / 150, 2), "estimated_cost_usd": round(characters / 1_000_000 * rate, 6), "enabled": block.enabled}


def build_manifest(project: Project, rates: dict[str, float]) -> dict:
    rows = [estimate_block(block, rates) for block in project.blocks]
    validation = validate_batch(project)
    return {
        "schema_version": 2,
        "project_id": project.id,
        "project_name": project.name,
        "created_at": utc_now(),
        "validation": validation,
        "blocks": rows,
        "totals": {
            "enabled_blocks": sum(1 for row in rows if row["enabled"]),
            "characters": sum(row["characters"] for row in rows if row["enabled"]),
            "words": sum(row["words"] for row in rows if row["enabled"]),
            "estimated_minutes": round(sum(row["estimated_minutes"] for row in rows if row["enabled"]), 2),
            "estimated_cost_usd": round(sum(row["estimated_cost_usd"] for row in rows if row["enabled"]), 6),
        },
    }


def render_local_blocks(project: Project, generate: Callable[..., Path]) -> tuple[list[Path], list[dict]]:
    files: list[Path] = []
    results: list[dict] = []
    for index, block in enumerate(project.blocks, 1):
        if not block.enabled:
            continue
        if not block.text.strip():
            results.append({"block_id": block.id, "title": block.title, "status": "failed", "reason": "Block text is empty"})
            continue
        if block.provider != "Kokoro local":
            results.append({"block_id": block.id, "title": block.title, "status": "skipped", "reason": "Cloud batch rendering is not configured in this release"})
            continue
        output_name = f"{index:03}_{safe_filename(block.title)}"
        try:
            path = generate(block.text, block.voice, block.language, block.speed, output_name)
            files.append(path)
            results.append({"block_id": block.id, "title": block.title, "status": "rendered", "file": path.name})
        except Exception as exc:
            results.append({"block_id": block.id, "title": block.title, "status": "failed", "reason": str(exc)})
    return files, results


def summarize_results(results: list[dict]) -> dict:
    return {status: sum(row.get("status") == status for row in results) for status in ("rendered", "skipped", "failed")}
