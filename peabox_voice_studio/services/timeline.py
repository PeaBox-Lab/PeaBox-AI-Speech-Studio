import hashlib
import io
import json
import math
import wave
from array import array
from pathlib import Path
from uuid import uuid4

from peabox_voice_studio.models import Project, ScriptBlock, utc_now
from peabox_voice_studio.services.audio import inspect_wav
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename


def source_hash(text: str, provider: str = "", voice: str = "", speed: float = 1.0) -> str:
    payload = json.dumps({"text": text, "provider": provider, "voice": voice, "speed": float(speed)}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def block_hash(block: ScriptBlock) -> str:
    return source_hash(block.text, block.provider, block.voice, block.speed)


def waveform_peaks(raw: bytes, buckets: int = 120) -> list[float]:
    params, samples = _read_wav(raw)
    channels = params.nchannels
    frames = len(samples) // channels if channels else 0
    if frames == 0:
        return []
    buckets = max(1, min(int(buckets), frames))
    width = math.ceil(frames / buckets)
    peaks = []
    for bucket in range(buckets):
        start_frame = bucket * width
        end_frame = min(frames, start_frame + width)
        peak = 0
        for frame in range(start_frame, end_frame):
            offset = frame * channels
            peak = max(peak, *(abs(samples[offset + channel]) for channel in range(channels)))
        peaks.append(round(peak / 32767, 4))
    return peaks


def list_clips(project: Project) -> list[dict]:
    return project.settings.setdefault("audio_clips", [])


def add_clip(project: Project, path: Path, title: str = "", track: str = "Voiceover", start_seconds: float = 0.0, gain_db: float = 0.0, block: ScriptBlock | None = None) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError("Audio file does not exist")
    raw = path.read_bytes()
    metrics = inspect_wav(raw)
    clip = {
        "id": uuid4().hex,
        "title": (title.strip() or path.stem)[:120],
        "file": str(path),
        "file_name": path.name,
        "track": track[:80] or "Voiceover",
        "start_seconds": round(max(0.0, float(start_seconds)), 3),
        "gain_db": round(max(-60.0, min(12.0, float(gain_db))), 2),
        "enabled": True,
        "created_at": utc_now(),
        "duration_seconds": metrics["duration_seconds"],
        "sample_rate_hz": metrics["sample_rate_hz"],
        "channels": metrics["channels"],
        "peaks": waveform_peaks(raw),
        "asset_hash": hashlib.sha256(raw).hexdigest(),
        "source_block_id": block.id if block else None,
        "source_hash": block_hash(block) if block else None,
    }
    list_clips(project).append(clip)
    return clip


def remove_clip(project: Project, clip_id: str) -> bool:
    clips = list_clips(project)
    before = len(clips)
    project.settings["audio_clips"] = [clip for clip in clips if clip.get("id") != clip_id]
    return len(project.settings["audio_clips"]) < before


def move_clip(project: Project, index: int, direction: int) -> list[dict]:
    clips = list_clips(project)
    target = index + direction
    if index < 0 or index >= len(clips) or target < 0 or target >= len(clips):
        return clips
    clips[index], clips[target] = clips[target], clips[index]
    return clips


def arrange_sequential(project: Project, gap_seconds: float = 0.25, track: str | None = None) -> None:
    cursor = 0.0
    gap_seconds = max(0.0, float(gap_seconds))
    for clip in list_clips(project):
        if not clip.get("enabled", True) or (track and clip.get("track") != track):
            continue
        clip["start_seconds"] = round(cursor, 3)
        cursor += float(clip.get("duration_seconds", 0)) + gap_seconds


def clip_status(project: Project, clip: dict) -> dict:
    path = Path(clip.get("file", ""))
    missing = not path.exists()
    block = next((item for item in project.blocks if item.id == clip.get("source_block_id")), None)
    stale = bool(block and clip.get("source_hash") and clip.get("source_hash") != block_hash(block))
    return {"missing": missing, "stale": stale, "ready": not missing and not stale}


def validate_timeline(project: Project) -> dict:
    issues = []
    enabled = [clip for clip in list_clips(project) if clip.get("enabled", True)]
    if not enabled:
        issues.append({"severity": "error", "clip": None, "message": "Timeline has no enabled clips"})
    base_format = None
    for index, clip in enumerate(enabled, 1):
        status = clip_status(project, clip)
        if status["missing"]:
            issues.append({"severity": "error", "clip": index, "message": f"Missing file: {clip.get('file_name', '')}"})
            continue
        if status["stale"]:
            issues.append({"severity": "warning", "clip": index, "message": "Source block changed after this clip was rendered"})
        current_format = (clip.get("sample_rate_hz"), clip.get("channels"))
        if base_format is None:
            base_format = current_format
        elif current_format != base_format:
            issues.append({"severity": "error", "clip": index, "message": "All enabled clips must use the same sample rate and channel count"})
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {"valid": errors == 0, "errors": errors, "warnings": warnings, "issues": issues, "enabled_clips": len(enabled)}


def mix_timeline(project: Project, output_name: str, output_dir: Path) -> tuple[Path, dict]:
    validation = validate_timeline(project)
    if not validation["valid"]:
        raise ValueError("Timeline must pass validation before export")
    clips = [clip for clip in list_clips(project) if clip.get("enabled", True)]
    first_params, _ = _read_wav(Path(clips[0]["file"]).read_bytes())
    sample_rate = first_params.framerate
    channels = first_params.nchannels
    end_frames = 0
    decoded = []
    for clip in clips:
        params, samples = _read_wav(Path(clip["file"]).read_bytes())
        start_frame = round(float(clip.get("start_seconds", 0)) * sample_rate)
        frame_count = len(samples) // channels
        end_frames = max(end_frames, start_frame + frame_count)
        decoded.append((clip, samples, start_frame, frame_count))
    mixed = [0.0] * (end_frames * channels)
    for clip, samples, start_frame, frame_count in decoded:
        gain = 10 ** (float(clip.get("gain_db", 0)) / 20)
        for frame in range(frame_count):
            source_offset = frame * channels
            target_offset = (start_frame + frame) * channels
            for channel in range(channels):
                mixed[target_offset + channel] += samples[source_offset + channel] * gain
    clipped_before_limit = sum(abs(value) > 32767 for value in mixed)
    pcm = array("h", [max(-32768, min(32767, round(value))) for value in mixed])
    raw = _write_wav(first_params, pcm)
    output = atomic_write_bytes(Path(output_dir) / f"{safe_filename(output_name)}_timeline.wav", raw)
    manifest = timeline_manifest(project, output.name)
    manifest["mix"] = {"duration_seconds": round(end_frames / sample_rate, 3), "sample_rate_hz": sample_rate, "channels": channels, "clipped_samples_before_limit": clipped_before_limit}
    project.settings.setdefault("timeline_exports", []).insert(0, {"created_at": utc_now(), "output": output.name, "manifest": manifest})
    project.settings["timeline_exports"] = project.settings["timeline_exports"][:20]
    return output, manifest


def timeline_manifest(project: Project, output_name: str = "") -> dict:
    clips = []
    for order, clip in enumerate(list_clips(project), 1):
        clips.append({
            "order": order, "id": clip.get("id"), "title": clip.get("title"), "file_name": clip.get("file_name"),
            "track": clip.get("track"), "start_seconds": clip.get("start_seconds"), "duration_seconds": clip.get("duration_seconds"),
            "gain_db": clip.get("gain_db"), "enabled": clip.get("enabled", True), "source_block_id": clip.get("source_block_id"),
            "source_hash": clip.get("source_hash"), "status": clip_status(project, clip),
        })
    return {"schema_version": 1, "project_id": project.id, "project_name": project.name, "created_at": utc_now(), "output": output_name, "clips": clips}


def _read_wav(raw: bytes) -> tuple[wave._wave_params, array]:
    with wave.open(io.BytesIO(raw), "rb") as reader:
        params = reader.getparams()
        if params.comptype != "NONE" or params.sampwidth != 2:
            raise ValueError("Timeline Studio supports uncompressed 16-bit PCM WAV files")
        frames = reader.readframes(params.nframes)
    samples = array("h"); samples.frombytes(frames)
    return params, samples


def _write_wav(params: wave._wave_params, samples: array) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(params.nchannels); writer.setsampwidth(2); writer.setframerate(params.framerate)
        writer.setcomptype("NONE", "not compressed"); writer.writeframes(samples.tobytes())
    return buffer.getvalue()


def refresh_clip(clip: dict, path: Path | None = None) -> dict:
    resolved = Path(path) if path is not None else Path(clip.get("file", ""))
    if not resolved.exists():
        raise FileNotFoundError("Audio file does not exist")
    raw = resolved.read_bytes()
    metrics = inspect_wav(raw)
    clip["file"] = str(resolved)
    clip["file_name"] = resolved.name
    clip["duration_seconds"] = metrics["duration_seconds"]
    clip["sample_rate_hz"] = metrics["sample_rate_hz"]
    clip["channels"] = metrics["channels"]
    clip["peaks"] = waveform_peaks(raw)
    clip["asset_hash"] = hashlib.sha256(raw).hexdigest()
    clip["updated_at"] = utc_now()
    return clip


def relink_clip(clip: dict, new_path: Path) -> dict:
    return refresh_clip(clip, new_path)


def acknowledge_clip_source(project: Project, clip: dict) -> bool:
    block = next((item for item in project.blocks if item.id == clip.get("source_block_id")), None)
    if block is None:
        return False
    clip["source_hash"] = block_hash(block)
    clip["updated_at"] = utc_now()
    return True


def cleanup_invalid_clips(project: Project, remove_missing: bool = False) -> dict:
    clips = list_clips(project)
    kept = []
    removed = []
    repaired = 0
    seen = set()
    for clip in clips:
        clip_id = clip.get("id") or uuid4().hex
        if clip_id in seen:
            clip_id = uuid4().hex
            repaired += 1
        clip["id"] = clip_id
        seen.add(clip_id)
        clip["start_seconds"] = round(max(0.0, float(clip.get("start_seconds", 0) or 0)), 3)
        clip["gain_db"] = round(max(-60.0, min(12.0, float(clip.get("gain_db", 0) or 0))), 2)
        clip["track"] = str(clip.get("track") or "Voiceover")[:80]
        clip["title"] = str(clip.get("title") or clip.get("file_name") or "Clip")[:120]
        if remove_missing and not Path(clip.get("file", "")).exists():
            removed.append(clip)
            continue
        kept.append(clip)
    project.settings["audio_clips"] = kept
    return {"kept": len(kept), "removed": len(removed), "repaired_ids": repaired}


def duplicate_timeline(project: Project) -> list[dict]:
    import copy
    original = list(list_clips(project))
    duplicate = copy.deepcopy(original)
    for clip in duplicate:
        clip["id"] = uuid4().hex
        clip["created_at"] = utc_now()
        clip["updated_at"] = clip["created_at"]
        clip["title"] = f"{clip.get('title', 'Clip')} copy"[:120]
    project.settings["audio_clips"] = original + duplicate
    return duplicate
