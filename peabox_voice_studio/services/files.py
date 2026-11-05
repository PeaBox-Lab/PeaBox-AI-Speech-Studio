import os
import re
import tempfile
import time
from pathlib import Path


def safe_filename(value: str, fallback: str = "audio", limit: int = 80) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", (value or "").strip())
    clean = clean.strip("._")[:limit]
    return clean or fallback


def atomic_write_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        Path(temp_name).unlink(missing_ok=True)
        raise
    return path


def temporary_upload(raw: bytes, suffix: str) -> Path:
    fd, name = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as handle:
        handle.write(raw)
    return Path(name)


def delete_with_retry(path: Path, attempts: int = 10, delay: float = 0.3) -> None:
    for attempt in range(attempts):
        try:
            path.unlink(missing_ok=True)
            return
        except PermissionError:
            if attempt == attempts - 1:
                raise
            time.sleep(delay)
