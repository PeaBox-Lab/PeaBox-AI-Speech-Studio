import html
import re
from uuid import uuid4
from peabox_voice_studio.models import Project, utc_now
PAUSE_PATTERN = re.compile(r"\[\[pause:(\d+(?:\.\d+)?)\]\]", re.IGNORECASE)
def list_pronunciations(project: Project) -> list[dict]:
    return project.settings.setdefault("pronunciation_dictionary", [])
def add_pronunciation(project: Project, source: str, replacement: str, case_sensitive: bool = False, whole_word: bool = True) -> dict:
    source = source.strip()
    replacement = replacement.strip()
    if not source or not replacement:
        raise ValueError("Source and replacement are required")
    item = {
        "id": uuid4().hex, "source": source[:200], "replacement": replacement[:400],
        "case_sensitive": bool(case_sensitive), "whole_word": bool(whole_word), "created_at": utc_now(),
    }
    entries = list_pronunciations(project)
    entries.insert(0, item)
    del entries[200:]
    return item
def delete_pronunciation(project: Project, item_id: str) -> bool:
    entries = list_pronunciations(project)
    before = len(entries)
    project.settings["pronunciation_dictionary"] = [item for item in entries if item.get("id") != item_id]
    return len(project.settings["pronunciation_dictionary"]) < before
def apply_pronunciations(text: str, entries: list[dict]) -> str:
    result = text
    for item in entries:
        source = item.get("source", "")
        if not source:
            continue
        pattern = re.escape(source)
        if item.get("whole_word", True):
            pattern = rf"(?<!\w){pattern}(?!\w)"
        flags = 0 if item.get("case_sensitive") else re.IGNORECASE
        result = re.sub(pattern, lambda _: item.get("replacement", ""), result, flags=flags)
    return result
def insert_pause(text: str, seconds: float, position: int | None = None) -> str:
    seconds = max(0.1, min(float(seconds), 10.0))
    marker = f"[[pause:{seconds:g}]]"
    if position is None:
        return f"{text.rstrip()} {marker}".strip()
    position = max(0, min(position, len(text)))
    return text[:position] + marker + text[position:]
def validate_pause_markers(text: str) -> list[str]:
    issues = []
    for raw in re.findall(r"\[\[pause:([^\]]+)\]\]", text, flags=re.IGNORECASE):
        try:
            value = float(raw)
            if value < 0.1 or value > 10:
                issues.append(f"Pause {raw} must be between 0.1 and 10 seconds")
        except ValueError:
            issues.append(f"Pause value '{raw}' is not numeric")
    malformed = re.sub(PAUSE_PATTERN, "", text)
    if "[[pause:" in malformed.lower():
        issues.append("One or more pause markers are malformed")
    return issues
def prepare_text(text: str, project: Project, provider: str) -> str:
    prepared = apply_pronunciations(text, list_pronunciations(project))
    if provider == "Kokoro local":
        return PAUSE_PATTERN.sub(lambda match: _local_pause(float(match.group(1))), prepared)
    return prepared
def _local_pause(seconds: float) -> str:
    count = max(1, min(8, round(seconds * 2)))
    return " " + ("... " * count)
def compile_ssml_text(text: str) -> str:
    parts = []
    cursor = 0
    for match in PAUSE_PATTERN.finditer(text):
        parts.append(html.escape(text[cursor:match.start()]))
        seconds = max(0.1, min(float(match.group(1)), 10.0))
        parts.append(f'<break time="{seconds:g}s"/>')
        cursor = match.end()
    parts.append(html.escape(text[cursor:]))
    return "".join(parts)
def pronunciation_conflicts(entries: list[dict]) -> list[dict]:
    issues = []
    seen = {}
    for index, item in enumerate(entries, 1):
        source = str(item.get("source", "")).strip()
        key = source if item.get("case_sensitive") else source.lower()
        if not source:
            issues.append({"severity": "error", "rule": index, "message": "Pronunciation source is empty"})
            continue
        signature = (key, bool(item.get("case_sensitive")), bool(item.get("whole_word", True)))
        if signature in seen:
            issues.append({"severity": "warning", "rule": index, "message": f"Duplicates rule {seen[signature]} for '{source}'"})
        else:
            seen[signature] = index
    for first_index, first in enumerate(entries, 1):
        first_source = str(first.get("source", ""))
        for second_index, second in enumerate(entries[first_index:], first_index + 1):
            second_source = str(second.get("source", ""))
            if first_source and second_source and first_source.lower() != second_source.lower() and (first_source.lower() in second_source.lower() or second_source.lower() in first_source.lower()):
                issues.append({"severity": "info", "rule": second_index, "message": f"'{second_source}' overlaps rule {first_index} source '{first_source}'; order may affect output"})
    return issues
def pronunciation_preview(text: str, entries: list[dict]) -> dict:
    prepared = apply_pronunciations(text, entries)
    return {"original": text, "prepared": prepared, "changed": prepared != text, "conflicts": pronunciation_conflicts(entries)}