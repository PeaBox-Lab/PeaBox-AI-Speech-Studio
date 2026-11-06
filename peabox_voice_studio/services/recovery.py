import json,shutil,sqlite3,uuid,zipfile
from io import BytesIO
from pathlib import Path
from peabox_voice_studio.config import BACKUPS_DIR,DATABASE_PATH,OUTPUTS_DIR,QUARANTINE_DIR,VERSION
def inventory():return [{'name':p.name,'bytes':p.stat().st_size,'path':str(p)} for p in OUTPUTS_DIR.rglob('*') if p.is_file()]
def backup_database(path=DATABASE_PATH):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);BACKUPS_DIR.mkdir(parents=True,exist_ok=True)
 if not path.exists():sqlite3.connect(path).close()
 target=BACKUPS_DIR/f'peabox_{uuid.uuid4().hex[:8]}.db';src=sqlite3.connect(path);dst=sqlite3.connect(target);src.backup(dst);src.close();dst.close();return target
def validate_database(path):
 try:c=sqlite3.connect(f'file:{Path(path)}?mode=ro',uri=True);v=c.execute('pragma integrity_check').fetchone()[0];c.close();return v=='ok'
 except sqlite3.Error:return False
def quarantine(path):
 path=Path(path)
 if OUTPUTS_DIR.resolve() not in path.resolve().parents:raise ValueError('Outside outputs')
 target=QUARANTINE_DIR/f'{uuid.uuid4().hex}_{path.name}';QUARANTINE_DIR.mkdir(parents=True,exist_ok=True);shutil.move(path,target);return target
def snapshot(project):
 out=BytesIO();manifest={'version':VERSION,'includes_media':False,'project_id':project.id}
 with zipfile.ZipFile(out,'w') as z:z.writestr('project.json',json.dumps(project.to_dict()));z.writestr('manifest.json',json.dumps(manifest))
 return out.getvalue()
