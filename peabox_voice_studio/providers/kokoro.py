import hashlib
from functools import lru_cache
from pathlib import Path
from peabox_voice_studio.config import MODELS_DIR, OUTPUTS_DIR
from peabox_voice_studio.services.files import atomic_write_bytes, collision_safe_path, safe_filename
MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"
MIN_DOWNLOAD_BYTES = 1024
def _download(path: Path, url: str) -> None:
    checksum_path = path.with_suffix(path.suffix + ".sha256")
    if path.exists():
        if checksum_path.exists() and checksum_path.read_text(encoding="ascii").strip() != hashlib.sha256(path.read_bytes()).hexdigest():
            raise ValueError(f"Integrity check failed for {path.name}; delete it and download again")
        return
    import requests
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    if len(response.content) < MIN_DOWNLOAD_BYTES:
        raise ValueError(f"Downloaded {path.name} is unexpectedly small")
    atomic_write_bytes(path, response.content)
    atomic_write_bytes(checksum_path, hashlib.sha256(response.content).hexdigest().encode("ascii"))
@lru_cache(maxsize=1)
def _load_engine(model_path: str, voices_path: str):
    from kokoro_onnx import Kokoro
    return Kokoro(model_path, voices_path)
def generate(text: str, voice: str, language: str, speed: float, output_name: str) -> Path:
    import soundfile as sf
    model = MODELS_DIR / "kokoro-v1.0.int8.onnx"
    voices = MODELS_DIR / "voices-v1.0.bin"
    _download(model, MODEL_URL); _download(voices, VOICES_URL)
    samples, rate = _load_engine(str(model), str(voices)).create(text, voice=voice, speed=speed, lang=language)
    output = collision_safe_path(OUTPUTS_DIR, f"{safe_filename(output_name)}.wav")
    from peabox_voice_studio.services.storage_policy import ensure_capacity
    ensure_capacity(output, int(getattr(samples, "nbytes", len(samples) * 4)) + 4096)
    sf.write(output, samples, rate)
    return output
