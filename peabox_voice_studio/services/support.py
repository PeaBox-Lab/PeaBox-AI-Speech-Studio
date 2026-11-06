import io,json,platform,sys,zipfile
from pathlib import Path

from peabox_voice_studio.config import MAX_SUPPORT_BUNDLE_BYTES
from peabox_voice_studio.models import utc_now


def create_support_bundle(repository_health: dict, storage_inventory: list[dict], operations: list[dict], diagnostics: list[dict], version: str, project_summary: dict | None = None) -> bytes:
    payloads={
        'support_manifest.json':{"schema_version":1,"created_at":utc_now(),"application_version":version,"python":sys.version,"platform":platform.platform(),"project_summary":project_summary or {}},
        'repository_health.json':repository_health,
        'storage_inventory.json':storage_inventory,
        'system_diagnostics.json':diagnostics,
        'operations.json':operations,
    }
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,payload in payloads.items():archive.writestr(name,json.dumps(payload,ensure_ascii=False,indent=2,default=str))
    if buffer.tell()>MAX_SUPPORT_BUNDLE_BYTES:raise ValueError("Support bundle exceeds the safe size limit")
    return buffer.getvalue()
