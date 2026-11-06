import shutil
import sys
from pathlib import Path
from peabox_voice_studio.config import MODELS_DIR, OUTPUTS_DIR, PROJECTS_DIR
def system_diagnostics() -> list[dict]:
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    compatible = (sys.version_info.major, sys.version_info.minor) in {(3, 10), (3, 11), (3, 12)}
    ffmpeg = shutil.which("ffmpeg")
    rows = [
        {"Check": "Python", "Status": "Ready" if compatible else "Unsupported", "Detail": f"Python {python_version}; supported: 3.10–3.12"},
        {"Check": "FFmpeg", "Status": "Ready" if ffmpeg else "Missing", "Detail": ffmpeg or "Required for compressed audio/video transcription"},
        {"Check": "Project storage", "Status": _directory_status(PROJECTS_DIR), "Detail": str(PROJECTS_DIR)},
        {"Check": "Output storage", "Status": _directory_status(OUTPUTS_DIR), "Detail": str(OUTPUTS_DIR)},
        {"Check": "Kokoro model", "Status": "Ready" if (MODELS_DIR / "kokoro-v1.0.int8.onnx").exists() else "Downloads on first use", "Detail": str(MODELS_DIR / "kokoro-v1.0.int8.onnx")},
        {"Check": "Kokoro voices", "Status": "Ready" if (MODELS_DIR / "voices-v1.0.bin").exists() else "Downloads on first use", "Detail": str(MODELS_DIR / "voices-v1.0.bin")},
    ]
    return rows
def _directory_status(path: Path) -> str:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return "Ready"
    except OSError:
        return "Not writable"
def transcription_readiness(filename: str) -> dict:
    extension = Path(filename or "").suffix.lower()
    compressed = extension in {".mp3", ".m4a", ".ogg", ".mp4", ".mov", ".mkv", ".webm"}
    ffmpeg = shutil.which("ffmpeg")
    ready = not compressed or bool(ffmpeg)
    return {"ready": ready, "requires_ffmpeg": compressed, "ffmpeg_path": ffmpeg, "message": "Ready" if ready else "FFmpeg is required for this media format"}