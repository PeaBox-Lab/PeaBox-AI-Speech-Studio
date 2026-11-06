from uuid import uuid4
from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.services.subtitles import to_srt, to_vtt
def _number(value, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback
def normalize_segments(rows: list[dict]) -> list[dict]:
    result = []
    previous_end = 0.0
    for index, row in enumerate(rows or [], 1):
        start = max(0.0, _number(row.get("start"), previous_end))
        end = max(start, _number(row.get("end"), start))
        result.append({"index": index, "start": round(start, 3), "end": round(end, 3), "speaker": str(row.get("speaker", "")).strip(), "text": str(row.get("text", "")).strip()})
        previous_end = end
    return result
def validate_segments(rows: list[dict]) -> dict:
    normalized = normalize_segments(rows)
    issues = []
    previous_end = 0.0
    for row in normalized:
        index = row["index"]
        if not row["text"]:
            issues.append({"severity": "warning", "segment": index, "message": "Segment text is empty"})
        if row["end"] <= row["start"]:
            issues.append({"severity": "error", "segment": index, "message": "End time must be greater than start time"})
        if row["start"] < previous_end:
            issues.append({"severity": "error", "segment": index, "message": f"Segment overlaps the previous segment ending at {previous_end:.3f}s"})
        previous_end = max(previous_end, row["end"])
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {"valid": errors == 0, "errors": errors, "warnings": warnings, "issues": issues, "segments": normalized}
def repair_segment_timing(rows: list[dict], minimum_duration: float = 0.1) -> list[dict]:
    minimum_duration = max(0.001, float(minimum_duration))
    repaired = []
    previous_end = 0.0
    for index, row in enumerate(rows or [], 1):
        raw_start = max(0.0, _number(row.get("start"), previous_end))
        start = max(previous_end, raw_start)
        raw_end = _number(row.get("end"), start + minimum_duration)
        end = max(start + minimum_duration, raw_end)
        repaired.append({"index": index, "start": round(start, 3), "end": round(end, 3), "speaker": str(row.get("speaker", "")).strip(), "text": str(row.get("text", "")).strip()})
        previous_end = end
    return repaired
def transcript_text(rows: list[dict], include_speakers: bool = True) -> str:
    lines = []
    for row in normalize_segments(rows):
        prefix = f"{row['speaker']}: " if include_speakers and row.get("speaker") else ""
        lines.append(prefix + row["text"])
    return "\n".join(lines)
def filter_segments(rows: list[dict], query: str) -> list[dict]:
    query = query.strip().lower()
    if not query:
        return normalize_segments(rows)
    return [row for row in normalize_segments(rows) if query in f"{row.get('speaker', '')} {row.get('text', '')}".lower()]
def export_transcript_bundle(rows: list[dict], require_valid: bool = True) -> dict[str, str]:
    validation = validate_segments(rows)
    if require_valid and not validation["valid"]:
        raise ValueError("Transcript timing must be valid before export")
    normalized = validation["segments"]
    subtitle_rows = [{"start": row["start"], "end": row["end"], "text": (f"{row['speaker']}: " if row.get("speaker") else "") + row["text"]} for row in normalized]
    return {"txt": transcript_text(normalized), "srt": to_srt(subtitle_rows), "vtt": to_vtt(subtitle_rows)}
def save_transcript_session(project: Project, name: str, rows: list[dict], source_name: str = "", language: str = "") -> dict:
    validation = validate_segments(rows)
    if not validation["valid"]:
        raise ValueError("Transcript timing must be valid before saving")
    name = name.strip() or f"Transcript {utc_now()}"
    session = {"id": uuid4().hex, "schema_version": 2, "name": name[:120], "source_name": source_name[:255], "language": language, "created_at": utc_now(), "updated_at": utc_now(), "segments": validation["segments"]}
    sessions = project.settings.setdefault("transcript_sessions", [])
    sessions.insert(0, session)
    del sessions[20:]
    return session
def update_transcript_session(project: Project, session_id: str, rows: list[dict]) -> bool:
    validation = validate_segments(rows)
    if not validation["valid"]:
        raise ValueError("Transcript timing must be valid before updating")
    for session in project.settings.setdefault("transcript_sessions", []):
        if session.get("id") == session_id:
            session["segments"] = validation["segments"]
            session["updated_at"] = utc_now()
            session["schema_version"] = 2
            return True
    return False
def delete_transcript_session(project: Project, session_id: str) -> bool:
    sessions = project.settings.setdefault("transcript_sessions", [])
    before = len(sessions)
    project.settings["transcript_sessions"] = [item for item in sessions if item.get("id") != session_id]
    return len(project.settings["transcript_sessions"]) < before
