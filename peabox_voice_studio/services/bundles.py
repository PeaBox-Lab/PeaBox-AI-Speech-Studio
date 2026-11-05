import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath
from uuid import uuid4

from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.services.audio import inspect_wav
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename
from peabox_voice_studio.services.timeline import refresh_clip

BUNDLE_SCHEMA = 1
MAX_BUNDLE_FILES = 500
MAX_BUNDLE_UNCOMPRESSED = 2 * 1024 * 1024 * 1024


def export_timeline_bundle(project: Project) -> bytes:
    buffer = io.BytesIO()
    project_data = project.to_dict()
    clips = project_data.get("settings", {}).get("audio_clips", [])
    asset_map = {}
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for clip in clips:
            path = Path(clip.get("file", ""))
            if not path.exists():
                continue
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            archive_name = f"audio/{digest[:16]}_{safe_filename(path.name)}"
            if archive_name not in asset_map.values():
                archive.writestr(archive_name, raw)
            asset_map[clip.get("id", uuid4().hex)] = archive_name
        for clip in clips:
            clip["bundle_asset"] = asset_map.get(clip.get("id"))
            clip["file"] = ""
        manifest = {
            "schema_version": BUNDLE_SCHEMA,
            "created_at": utc_now(),
            "project_name": project.name,
            "clip_assets": asset_map,
        }
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr("project.json", json.dumps({"schema_version": 1, "exported_at": utc_now(), "project": project_data}, ensure_ascii=False, indent=2))
    return buffer.getvalue()


def import_timeline_bundle(raw: bytes, output_dir: Path) -> Project:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_BUNDLE_FILES:
            raise ValueError("Bundle contains too many files")
        if sum(info.file_size for info in infos) > MAX_BUNDLE_UNCOMPRESSED:
            raise ValueError("Bundle is too large when extracted")
        names = {info.filename for info in infos}
        if "project.json" not in names or "manifest.json" not in names:
            raise ValueError("Bundle is missing project.json or manifest.json")
        for info in infos:
            _validate_member(info.filename)
            if info.flag_bits & 0x1:
                raise ValueError("Encrypted bundle members are not supported")
            if (info.external_attr >> 16) & 0o170000 == 0o120000:
                raise ValueError("Bundle symbolic links are not supported")
        manifest = json.loads(archive.read("manifest.json").decode("utf-8-sig"))
        payload = json.loads(archive.read("project.json").decode("utf-8-sig"))
        if manifest.get("schema_version") != BUNDLE_SCHEMA:
            raise ValueError("Unsupported timeline bundle schema")
        project_data = payload.get("project")
        if not isinstance(project_data, dict):
            raise ValueError("Bundle project payload is invalid")
        project = Project.from_dict(project_data)
        project.id = uuid4().hex
        project.name = f"{project.name} (bundle import)"[:120]
        project.created_at = utc_now()
        project.updated_at = project.created_at
        clips = project.settings.setdefault("audio_clips", [])
        for clip in clips:
            asset_name = clip.pop("bundle_asset", None) or manifest.get("clip_assets", {}).get(clip.get("id"))
            if not asset_name:
                clip["file"] = ""
                continue
            _validate_member(asset_name)
            if asset_name not in names:
                clip["file"] = ""
                continue
            if PurePosixPath(asset_name).suffix.lower() != ".wav":
                raise ValueError("Timeline bundle assets must be WAV files")
            raw_asset = archive.read(asset_name)
            inspect_wav(raw_asset)
            destination = _collision_safe_path(output_dir, PurePosixPath(asset_name).name)
            atomic_write_bytes(destination, raw_asset)
            refresh_clip(clip, destination)
        project.settings["timeline_exports"] = []
        return project


def _validate_member(name: str) -> None:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "\\" in name or ":" in name:
        raise ValueError("Bundle contains an unsafe path")
    if name.startswith("/"):
        raise ValueError("Bundle contains an unsafe path")


def _collision_safe_path(directory: Path, filename: str) -> Path:
    safe = safe_filename(filename, fallback="asset.wav")
    candidate = directory / safe
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while candidate.exists():
        candidate = directory / f"{stem}_{counter}{suffix}"
        counter += 1
    return candidate
