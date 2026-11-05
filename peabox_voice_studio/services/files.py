import io
import json
import os
import re
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any


def safe_filename(value: str, fallback: str = "audio", limit: int = 80) -> str:
    clean = re.sub(r"[^A-Za-z0-9_.-]+", "_", (value or "").strip()).strip("._")[:limit]
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


def build_render_zip(files: list[Path], manifest: dict[str, Any]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for path in files:
            if path.exists():
                archive.write(path, f"audio/{path.name}")
    return buffer.getvalue()


def collision_safe_path(directory: Path, filename: str) -> Path:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    safe = safe_filename(Path(filename).stem, fallback="output") + Path(filename).suffix.lower()
    candidate = directory / safe
    stem, suffix, counter = candidate.stem, candidate.suffix, 2
    while candidate.exists():
        candidate = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate


def user_safe_error(exc: Exception, fallback: str = "The operation could not be completed") -> str:
    safe_types = (ValueError, FileNotFoundError, PermissionError, TimeoutError)
    if isinstance(exc, safe_types):
        text = str(exc).strip()
        if text:
            return text[:300]
    return fallback


class FileLock:
    def __init__(self, path: Path, timeout: float = 5.0, delay: float = 0.05):
        self.path = Path(path); self.timeout = timeout; self.delay = delay; self.fd = None
    def __enter__(self):
        deadline = time.monotonic() + self.timeout
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(self.fd, str(os.getpid()).encode("ascii"))
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"Timed out waiting for file lock: {self.path.name}")
                time.sleep(self.delay)
    def __exit__(self, exc_type, exc, tb):
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)
        return False
