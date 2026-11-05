from pathlib import Path
from peabox_voice_studio.config import MODELS_DIR, OUTPUTS_DIR
from peabox_voice_studio.services.files import safe_filename

MODEL_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"


def _download(path: Path, url: str) -> None:
    if path.exists(): return
    import requests
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    path.write_bytes(response.content)


def generate(text: str, voice: str, language: str, speed: float, output_name: str) -> Path:
    import soundfile as sf
    from kokoro_onnx import Kokoro
    model = MODELS_DIR / "kokoro-v1.0.int8.onnx"
    voices = MODELS_DIR / "voices-v1.0.bin"
    _download(model, MODEL_URL); _download(voices, VOICES_URL)
    samples, rate = Kokoro(str(model), str(voices)).create(text, voice=voice, speed=speed, lang=language)
    output = OUTPUTS_DIR / f"{safe_filename(output_name)}.wav"
    sf.write(output, samples, rate)
    return output
