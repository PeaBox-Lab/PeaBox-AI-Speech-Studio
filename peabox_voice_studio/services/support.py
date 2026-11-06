import io,json,platform,sys,zipfile
from peabox_voice_studio.models import utc_now
def create_support_bundle(repository_health,inventory,operations,diagnostics,version,project_summary=None):
 files={'support_manifest.json':{'created_at':utc_now(),'application_version':version,'python':sys.version,'platform':platform.platform(),'project_summary':project_summary or {}},'repository_health.json':repository_health,'storage_inventory.json':inventory,'system_diagnostics.json':diagnostics,'operations.json':operations};b=io.BytesIO()
 with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
  for n,d in files.items():z.writestr(n,json.dumps(d,indent=2,default=str))
 return b.getvalue()
