def format_timestamp(seconds: float) -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    secs, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"


def to_srt(rows: list[dict]) -> str:
    return "\n\n".join(f"{i}\n{format_timestamp(row['start'])} --> {format_timestamp(row['end'])}\n{row['text'].strip()}" for i, row in enumerate(rows, 1))
