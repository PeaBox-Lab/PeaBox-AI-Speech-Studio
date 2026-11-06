import hashlib
import json
import shutil
from pathlib import Path
from uuid import uuid4

from peabox_voice_studio.config import DATA_DIR, MODELS_DIR, OUTPUTS_DIR, PROJECTS_DIR, QUARANTINE_DIR
from peabox_voice_studio.models import utc_now
from peabox_voice_studio.services.files import atomic_write_bytes, collision_safe_path, safe_filename


def storage_inventory(paths: dict[str, Path] | None = None) -> list[dict]:
    paths = paths or {"Projects": PROJECTS_DIR, "Outputs": OUTPUTS_DIR, "Models": MODELS_DIR, "Data": DATA_DIR, "Quarantine": QUARANTINE_DIR}
    rows=[]
    for label,path in paths.items():
        path=Path(path); files=[item for item in path.rglob('*') if item.is_file()] if path.exists() else []
        rows.append({"Area":label,"Path":str(path),"Files":len(files),"Bytes":sum(item.stat().st_size for item in files),"Exists":path.exists()})
    return rows


def referenced_output_paths(projects: list, output_dir: Path = OUTPUTS_DIR) -> set[Path]:
    output_dir=Path(output_dir).resolve(); referenced=set()
    def add(value):
        if not value:return
        path=Path(value)
        candidate=(path if path.is_absolute() else output_dir/path.name).resolve()
        if candidate.parent==output_dir:referenced.add(candidate)
    for project in projects:
        for item in project.render_history:add(item.get('output'))
        for clip in project.settings.get('audio_clips',[]):add(clip.get('file') or clip.get('file_name'))
        for job in project.settings.get('batch_jobs',[]):
            for item in job.get('items',[]):add(item.get('file'))
        for comparison in project.settings.get('comparison_history',[]):
            for output in comparison.get('outputs',[]):add(output)
        for export in project.settings.get('timeline_exports',[]):add(export.get('output'))
    return referenced


def analyze_output_storage(projects: list, output_dir: Path = OUTPUTS_DIR) -> dict:
    output_dir=Path(output_dir); output_dir.mkdir(parents=True,exist_ok=True)
    referenced=referenced_output_paths(projects,output_dir)
    files=[item.resolve() for item in output_dir.iterdir() if item.is_file() and item.name!='.gitkeep']
    orphaned=sorted(set(files)-referenced,key=lambda item:item.name.lower())
    missing=sorted([item for item in referenced if not item.exists()],key=lambda item:item.name.lower())
    return {
        "files":len(files),"bytes":sum(item.stat().st_size for item in files),
        "referenced":len(set(files)&referenced),"orphaned":len(orphaned),"orphaned_bytes":sum(item.stat().st_size for item in orphaned),
        "missing_references":len(missing),"orphaned_files":[_file_row(item) for item in orphaned],"missing_files":[str(item) for item in missing],
    }


def quarantine_files(paths: list[Path], root: Path = QUARANTINE_DIR) -> dict:
    root=Path(root); root.mkdir(parents=True,exist_ok=True)
    batch_id=uuid4().hex; batch=root/batch_id; batch.mkdir()
    manifest={"schema_version":1,"batch_id":batch_id,"created_at":utc_now(),"files":[]}
    moved=[]
    try:
        for original in paths:
            original=Path(original).resolve()
            if original.parent != OUTPUTS_DIR.resolve():raise ValueError("Only files directly inside the output folder can be quarantined")
            if not original.exists():continue
            destination=collision_safe_path(batch,original.name)
            original.replace(destination);moved.append((original,destination))
            manifest["files"].append({"original":str(original),"quarantined":destination.name,"bytes":destination.stat().st_size,"sha256":hashlib.sha256(destination.read_bytes()).hexdigest()})
        atomic_write_bytes(batch/'manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2).encode())
    except Exception:
        for original,destination in reversed(moved):
            if destination.exists():destination.replace(original)
        shutil.rmtree(batch,ignore_errors=True);raise
    return manifest


def list_quarantine_batches(root: Path = QUARANTINE_DIR) -> list[dict]:
    root=Path(root);result=[]
    if not root.exists():return result
    for folder in sorted((item for item in root.iterdir() if item.is_dir()),key=lambda item:item.stat().st_mtime,reverse=True):
        manifest_path=folder/'manifest.json'
        try:
            manifest=json.loads(manifest_path.read_text())
            result.append({"batch_id":manifest.get("batch_id",folder.name),"created_at":manifest.get("created_at"),"files":len(manifest.get("files",[])),"bytes":sum(item.get("bytes",0) for item in manifest.get("files",[])),"path":str(folder)})
        except (OSError,json.JSONDecodeError):continue
    return result


def restore_quarantine_batch(batch_path: Path, root: Path = QUARANTINE_DIR) -> dict:
    batch=Path(batch_path).resolve();root=Path(root).resolve()
    if root not in batch.parents:raise ValueError("Quarantine batch is outside the quarantine folder")
    manifest=json.loads((batch/'manifest.json').read_text())
    restored=[]
    for item in manifest.get('files',[]):
        source=batch/item['quarantined']
        if not source.exists():continue
        destination=collision_safe_path(Path(item['original']).parent,Path(item['original']).name)
        source.replace(destination);restored.append(str(destination))
    shutil.rmtree(batch,ignore_errors=True)
    return {"restored":len(restored),"files":restored}


def delete_quarantine_batch(batch_path: Path, root: Path = QUARANTINE_DIR) -> bool:
    batch=Path(batch_path).resolve();root=Path(root).resolve()
    if root not in batch.parents:raise ValueError("Quarantine batch is outside the quarantine folder")
    if not batch.exists():return False
    shutil.rmtree(batch);return True


def _file_row(path: Path) -> dict:
    return {"name":path.name,"path":str(path),"bytes":path.stat().st_size,"modified":path.stat().st_mtime}
