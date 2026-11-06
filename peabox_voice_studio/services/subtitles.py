def _milliseconds(seconds: float) -> tuple[int, int, int, int]:
    value = max(0, round(float(seconds) * 1000))
    hours, value = divmod(value, 3_600_000)
    minutes, value = divmod(value, 60_000)
    secs, milliseconds = divmod(value, 1000)
    return hours, minutes, secs, milliseconds
def format_timestamp(seconds: float) -> str:
    hours, minutes, secs, milliseconds = _milliseconds(seconds)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
def format_vtt_timestamp(seconds: float) -> str:
    hours, minutes, secs, milliseconds = _milliseconds(seconds)
    return f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
def to_srt(rows: list[dict]) -> str:
    return "\n\n".join(f"{i}\n{format_timestamp(row['start'])} --> {format_timestamp(row['end'])}\n{row['text'].strip()}" for i, row in enumerate(rows, 1))
def to_vtt(rows: list[dict]) -> str:
    cues = "\n\n".join(f"{format_vtt_timestamp(row['start'])} --> {format_vtt_timestamp(row['end'])}\n{row['text'].strip()}" for row in rows)
    return f"WEBVTT\n\n{cues}" if cues else "WEBVTT\n"
