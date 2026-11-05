import io
import math
import wave
from array import array
from pathlib import Path

from peabox_voice_studio.services.files import atomic_write_bytes, collision_safe_path, safe_filename


def _read_pcm16(raw: bytes) -> tuple[wave._wave_params, array]:
    with wave.open(io.BytesIO(raw), "rb") as reader:
        params = reader.getparams()
        if params.comptype != "NONE":
            raise ValueError("Only uncompressed PCM WAV files are supported")
        if params.sampwidth != 2:
            raise ValueError("Audio Quality Lab currently supports 16-bit PCM WAV files")
        frames = reader.readframes(params.nframes)
    samples = array("h")
    samples.frombytes(frames)
    if samples.itemsize != 2:
        raise ValueError("16-bit PCM is unavailable on this platform")
    return params, samples


def _write_pcm16(params: wave._wave_params, samples: array) -> bytes:
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as writer:
        writer.setnchannels(params.nchannels)
        writer.setsampwidth(2)
        writer.setframerate(params.framerate)
        writer.setcomptype("NONE", "not compressed")
        writer.writeframes(samples.tobytes())
    return buffer.getvalue()


def inspect_wav(raw: bytes) -> dict:
    params, samples = _read_pcm16(raw)
    peak = 0; square_sum = 0; clipped = 0
    for sample in samples:
        absolute = abs(sample); peak = max(peak, absolute); square_sum += sample * sample
        if absolute >= 32767: clipped += 1
    rms = math.sqrt(square_sum / len(samples)) if samples else 0.0
    duration = params.nframes / params.framerate if params.framerate else 0.0
    return {
        "channels": params.nchannels,
        "sample_rate_hz": params.framerate,
        "sample_width_bits": 16,
        "frames": params.nframes,
        "duration_seconds": round(duration, 3),
        "peak_dbfs": _dbfs(peak),
        "rms_dbfs": _dbfs(rms),
        "clipped_samples": clipped,
        "bytes": len(raw),
    }


def normalize_wav(raw: bytes, target_peak_dbfs: float = -1.0) -> tuple[bytes, dict]:
    if target_peak_dbfs > 0 or target_peak_dbfs < -30:
        raise ValueError("Target peak must be between -30 and 0 dBFS")
    params, samples = _read_pcm16(raw)
    peak = max((abs(sample) for sample in samples), default=0)
    if peak == 0:
        return raw, {"gain_db": 0.0, "changed": False, "reason": "Audio is silent"}
    target = 32767 * (10 ** (target_peak_dbfs / 20))
    gain = target / peak
    processed = array("h", (max(-32768, min(32767, round(sample * gain))) for sample in samples))
    gain_db = 20 * math.log10(gain) if gain > 0 else 0.0
    return _write_pcm16(params, processed), {"gain_db": round(gain_db, 3), "changed": abs(gain_db) >= 0.01, "target_peak_dbfs": target_peak_dbfs}


def trim_silence_wav(raw: bytes, threshold_dbfs: float = -40.0, padding_ms: int = 100) -> tuple[bytes, dict]:
    if threshold_dbfs > 0 or threshold_dbfs < -90:
        raise ValueError("Silence threshold must be between -90 and 0 dBFS")
    params, samples = _read_pcm16(raw)
    channels = params.nchannels
    frame_count = len(samples) // channels if channels else 0
    threshold = 32767 * (10 ** (threshold_dbfs / 20))
    first_active = None; last_active = None
    for frame_index in range(frame_count):
        start = frame_index * channels
        frame_peak = max(abs(samples[start + channel]) for channel in range(channels))
        if frame_peak > threshold:
            if first_active is None: first_active = frame_index
            last_active = frame_index
    if first_active is None:
        return raw, {"changed": False, "reason": "No audio exceeded the silence threshold", "removed_seconds": 0.0}
    padding_frames = round(params.framerate * max(0, padding_ms) / 1000)
    first = max(0, first_active - padding_frames)
    last = min(frame_count, last_active + padding_frames + 1)
    trimmed = samples[first * channels:last * channels]
    removed_frames = frame_count - (last - first)
    return _write_pcm16(params, array("h", trimmed)), {
        "changed": removed_frames > 0,
        "removed_seconds": round(removed_frames / params.framerate, 3),
        "start_seconds": round(first / params.framerate, 3),
        "end_seconds": round(last / params.framerate, 3),
        "threshold_dbfs": threshold_dbfs,
        "padding_ms": padding_ms,
    }


def save_processed_wav(raw: bytes, name: str, suffix: str, output_dir: Path) -> Path:
    filename = f"{safe_filename(name)}_{safe_filename(suffix)}.wav"
    return atomic_write_bytes(collision_safe_path(output_dir, filename), raw)


def _dbfs(value: float) -> float | None:
    if value <= 0:
        return None
    return round(20 * math.log10(value / 32767), 3)
