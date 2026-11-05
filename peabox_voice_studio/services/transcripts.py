from copy import deepcopy
from uuid import uuid4

from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.services.subtitles import to_srt, to_vtt


def normalize_segments(rows: list[dict]) -> list[dict]:
    result = []
    previous_end = 0.0
    for index, row in enumerate(rows, 1):
        start = max(0.0, float(row.get("start", previous_end)))
        end = max(start, float(row.get("end", start)))
        result.append({"index": index, "start": round(start, 3), "end": round(end, 3), "speaker": str(row.get("speaker", "")).strip(), "text": str(row.get("text", "")).strip()})
        previous_end = end
    return result


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


def export_transcript_bundle(rows: list[dict]) -> dict[str, str]:
    normalized = normalize_segments(rows)
    subtitle_rows = [{"start": row["start"], "end": row["end"], "text": (f"{row['speaker']}: " if row.get("speaker") else "") + row["text"]} for row in normalized]
    return {"txt": transcript_text(normalized), "srt": to_srt(subtitle_rows), "vtt": to_vtt(subtitle_rows)}


def save_transcript_session(project: Project, name: str, rows: list[dict], source_name: str = "", language: str = "") -> dict:
    name = name.strip() or f"Transcript {utc_now()}"
    session = {"id": uuid4().hex, "name": name[:120], "source_name": source_name[:255], "language": language, "created_at": utc_now(), "segments": normalize_segments(rows)}
    sessions = project.settings.setdefault("transcript_sessions", [])
    sessions.insert(0, session)
    del sessions[20:]
    return session


def delete_transcript_session(project: Project, session_id: str) -> bool:
    sessions = project.settings.setdefault("transcript_sessions", [])
    before = len(sessions)
    project.settings["transcript_sessions"] = [item for item in sessions if item.get("id") != session_id]
    return len(project.settings["transcript_sessions"]) < before
