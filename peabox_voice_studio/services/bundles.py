import hashlib
import io
import json
import zipfile
import tempfile
import shutil
from pathlib import Path, PurePosixPath
from uuid import uuid4
from peabox_voice_studio.models import Project, utc_now
from peabox_voice_studio.config import MAX_BUNDLE_INPUT_BYTES, MAX_BUNDLE_UNCOMPRESSED_BYTES
from peabox_voice_studio.services.audio import inspect_wav
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename
from peabox_voice_studio.services.timeline import refresh_clip
from peabox_voice_studio.services.migrations import migrate_project_payload, rewrite_import_references
BUNDLE_SCHEMA = 1
MAX_BUNDLE_FILES = 500
MAX_BUNDLE_UNCOMPRESSED = MAX_BUNDLE_UNCOMPRESSED_BYTES
def export_timeline_bundle(project: Project) -> bytes:
    buffer = io.BytesIO()
    project_data = project.to_dict()
    clips = project_data.get("settings", {}).get("audio_clips", [])
    asset_map = {}
    existing_assets = [Path(clip.get("file", "")) for clip in clips if Path(clip.get("file", "")).exists()]
    if sum(path.stat().st_size for path in existing_assets) > MAX_BUNDLE_UNCOMPRESSED:
        raise ValueError("Timeline assets exceed the safe bundle export limit")
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
    if len(raw) > MAX_BUNDLE_INPUT_BYTES:
        raise ValueError("Compressed bundle exceeds the safe import limit")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    staged_moves = []
    with tempfile.TemporaryDirectory(dir=output_dir, prefix=".bundle-") as staging_name:
        staging = Path(staging_name)
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
            project_data, migration_notes = migrate_project_payload(payload.get("project"))
            new_project_id = uuid4().hex
            migration_notes.extend(rewrite_import_references(project_data, new_project_id, preserve_asset_paths=True))
            project = Project.from_dict(project_data)
            project.id = new_project_id
            project.name = f"{project.name} (bundle import)"[:120]
            project.created_at = utc_now(); project.updated_at = project.created_at
            clips = project.settings.setdefault("audio_clips", [])
            for clip in clips:
                asset_name = clip.pop("bundle_asset", None) or manifest.get("clip_assets", {}).get(clip.get("id"))
                if not asset_name or asset_name not in names:
                    clip["file"] = ""; continue
                _validate_member(asset_name)
                if PurePosixPath(asset_name).suffix.lower() != ".wav":
                    raise ValueError("Timeline bundle assets must be WAV files")
                raw_asset = archive.read(asset_name); inspect_wav(raw_asset)
                staged = staging / PurePosixPath(asset_name).name
                atomic_write_bytes(staged, raw_asset)
                destination = _collision_safe_path(output_dir, staged.name)
                staged_moves.append((staged, destination, clip))
            # Commit only after every member has validated and staged successfully.
            committed = []
            try:
                for staged, destination, clip in staged_moves:
                    staged.replace(destination)
                    committed.append(destination)
                    refresh_clip(clip, destination)
            except Exception:
                for destination in committed:
                    destination.unlink(missing_ok=True)
                raise
            project.settings["timeline_exports"] = []
            if migration_notes:
                project.settings["last_import_migration"] = {"at": project.updated_at, "notes": migration_notes}
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