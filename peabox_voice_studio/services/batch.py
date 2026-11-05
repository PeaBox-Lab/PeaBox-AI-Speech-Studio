from pathlib import Path
from typing import Callable

from peabox_voice_studio.models import Project, ScriptBlock, utc_now
from peabox_voice_studio.services.files import safe_filename


def estimate_block(block: ScriptBlock, rates: dict[str, float]) -> dict:
    characters = len(block.text)
    words = len(block.text.split())
    rate = rates.get(block.provider, 0.0)
    return {
        "id": block.id,
        "title": block.title,
        "provider": block.provider,
        "voice": block.voice,
        "characters": characters,
        "words": words,
        "estimated_minutes": round(words / 150, 2),
        "estimated_cost_usd": round(characters / 1_000_000 * rate, 6),
        "enabled": block.enabled,
    }


def build_manifest(project: Project, rates: dict[str, float]) -> dict:
    rows = [estimate_block(block, rates) for block in project.blocks]
    return {
        "schema_version": 1,
        "project_id": project.id,
        "project_name": project.name,
        "created_at": utc_now(),
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
        if block.provider != "Kokoro local":
            results.append({"block_id": block.id, "status": "skipped", "reason": "Cloud batch rendering is not configured in this release"})
            continue
        output_name = f"{index:03}_{safe_filename(block.title)}"
        try:
            path = generate(block.text, block.voice, block.language, block.speed, output_name)
            files.append(path)
            results.append({"block_id": block.id, "status": "rendered", "file": path.name})
        except Exception as exc:
            results.append({"block_id": block.id, "status": "failed", "reason": str(exc)})
    return files, results
