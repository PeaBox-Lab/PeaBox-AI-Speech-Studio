from functools import lru_cache
from pathlib import Path
from peabox_voice_studio.services.files import delete_with_retry, temporary_upload
@lru_cache(maxsize=5)
def _whisper_model(model_size: str):
    from faster_whisper import WhisperModel
    return WhisperModel(model_size, device="cpu", compute_type="int8")
def transcribe(raw: bytes, original_name: str, model_size: str, language: str):
    path = temporary_upload(raw, Path(original_name).suffix or ".wav")
    try:
        segments, info = _whisper_model(model_size).transcribe(str(path), language=None if language == "Auto" else language, vad_filter=True, beam_size=5)
        return [{"start": x.start, "end": x.end, "text": x.text.strip()} for x in segments], info.language
    finally:
        delete_with_retry(path)
