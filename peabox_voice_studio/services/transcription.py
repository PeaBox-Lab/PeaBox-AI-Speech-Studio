from pathlib import Path

from peabox_voice_studio.services.files import delete_with_retry, temporary_upload


def transcribe(raw: bytes, original_name: str, model_size: str, language: str):
    from faster_whisper import WhisperModel

    path = temporary_upload(raw, Path(original_name).suffix or ".wav")
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        segments, info = model.transcribe(
            str(path), language=None if language == "Auto" else language,
            vad_filter=True, beam_size=5
        )
        rows = [{"start": item.start, "end": item.end, "text": item.text.strip()} for item in segments]
        return rows, info.language
    finally:
        delete_with_retry(path)
