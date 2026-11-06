import hashlib,json,os,shutil,sqlite3,uuid,zipfile
from datetime import datetime,timezone
from io import BytesIO
from pathlib import Path
from peabox_voice_studio.config import BACKUPS_DIR,BASE_DIR,DATABASE_PATH,DATA_DIR,MODELS_DIR,OUTPUTS_DIR,PROJECTS_DIR,QUARANTINE_DIR,SUPPORT_DIR,VERSION
from peabox_voice_studio.services.files import atomic_write_bytes

def utc_stamp():return datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
def _inside(path:Path,roots):
 p=path.resolve();return any(p==r.resolve() or r.resolve() in p.parents for r in roots)
def sha256(path:Path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def storage_inventory(roots=None):
 roots=roots or {'projects':PROJECTS_DIR,'outputs':OUTPUTS_DIR,'models':MODELS_DIR,'data':DATA_DIR}
 rows=[];seen=set()
 for category,root in roots.items():
  root=Path(root)
  if not root.exists():continue
  for path in root.rglob('*'):
   if not path.is_file() or path.resolve() in seen:continue
   seen.add(path.resolve());stat=path.stat();rows.append({'category':category,'path':str(path.relative_to(BASE_DIR)) if _inside(path,[BASE_DIR]) else str(path),'name':path.name,'bytes':stat.st_size,'modified':datetime.fromtimestamp(stat.st_mtime,timezone.utc).isoformat()})
 return sorted(rows,key=lambda x:(x['category'],x['path']))
def storage_summary(rows=None):
 rows=rows or storage_inventory();summary={}
 for row in rows:
  item=summary.setdefault(row['category'],{'files':0,'bytes':0});item['files']+=1;item['bytes']+=row['bytes']
 return summary
def _project_references(projects):
 refs=set()
 def walk(value):
  if isinstance(value,dict):
   for x in value.values():walk(x)
  elif isinstance(value,list):
   for x in value:walk(x)
  elif isinstance(value,str) and (value.endswith(('.wav','.mp3','.json','.zip','.srt','.vtt','.txt')) or '/' in value or '\\' in value):
   try:
    candidate=Path(value);refs.add(str(candidate.resolve()))
    if not candidate.is_absolute():refs.add(str((BASE_DIR/candidate).resolve()));refs.add(str((OUTPUTS_DIR/candidate.name).resolve()))
   except Exception:pass
 for project in projects:walk(project.to_dict())
 return refs
def orphan_outputs(projects):
 refs=_project_references(projects);return [p for p in OUTPUTS_DIR.rglob('*') if p.is_file() and str(p.resolve()) not in refs]
def quarantine_file(path,reason='Unreferenced output'):
 path=Path(path)
 if not _inside(path,[OUTPUTS_DIR]):raise ValueError('Only output files can be quarantined')
 if not path.exists() or not path.is_file():raise FileNotFoundError('File not found')
 qid=uuid.uuid4().hex;target=QUARANTINE_DIR/f'{qid}_{path.name}';target.parent.mkdir(parents=True,exist_ok=True);shutil.move(str(path),target)
 entry={'id':qid,'original':str(path.resolve()),'quarantined':str(target.resolve()),'name':path.name,'bytes':target.stat().st_size,'sha256':sha256(target),'reason':reason,'created_at':datetime.now(timezone.utc).isoformat(),'restored_at':''}
 atomic_write_bytes(QUARANTINE_DIR/f'{qid}.json',json.dumps(entry,indent=2).encode());return entry
def list_quarantine():
 rows=[]
 for p in QUARANTINE_DIR.glob('*.json'):
  try:rows.append(json.loads(p.read_text()))
  except (OSError,json.JSONDecodeError):continue
 return sorted(rows,key=lambda x:x.get('created_at',''),reverse=True)
def restore_quarantine(qid):
 meta=QUARANTINE_DIR/f'{qid}.json'
 if not meta.exists():raise FileNotFoundError('Quarantine record not found')
 entry=json.loads(meta.read_text());source=Path(entry['quarantined']);target=Path(entry['original'])
 if not source.exists():raise FileNotFoundError('Quarantined file not found')
 if not _inside(target,[OUTPUTS_DIR]):raise ValueError('Invalid restore target')
 target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():target=target.with_name(f'{target.stem}_restored_{utc_stamp()}{target.suffix}')
 shutil.move(str(source),target);entry['restored_at']=datetime.now(timezone.utc).isoformat();entry['restored_to']=str(target.resolve());atomic_write_bytes(meta,json.dumps(entry,indent=2).encode());return entry
def project_snapshot(project):
 payload=json.dumps(project.to_dict(),ensure_ascii=False,indent=2).encode();manifest={'schema':1,'kind':'project-metadata-snapshot','version':VERSION,'project_id':project.id,'created_at':datetime.now(timezone.utc).isoformat(),'includes_media':False,'project_sha256':hashlib.sha256(payload).hexdigest()}
 out=BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('project.json',payload);z.writestr('manifest.json',json.dumps(manifest,indent=2))
 return out.getvalue(),manifest
def backup_database(path=DATABASE_PATH,backup_dir=BACKUPS_DIR):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);backup_dir=Path(backup_dir);backup_dir.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  con=sqlite3.connect(path);con.close()
 target=backup_dir/f'peabox_{utc_stamp()}_{uuid.uuid4().hex[:8]}.db';source=sqlite3.connect(path);dest=sqlite3.connect(target)
 try:source.backup(dest)
 finally:dest.close();source.close()
 return target
def validate_database(path):
 path=Path(path)
 if not path.exists():return {'valid':False,'message':'File not found'}
 try:
  con=sqlite3.connect(f'file:{path}?mode=ro',uri=True);result=con.execute('pragma integrity_check').fetchone()[0];con.close();return {'valid':result=='ok','message':result}
 except sqlite3.Error as exc:return {'valid':False,'message':type(exc).__name__}
def list_backups(backup_dir=BACKUPS_DIR):return sorted(Path(backup_dir).glob('*.db'),key=lambda p:p.stat().st_mtime,reverse=True)
def restore_database(backup,path=DATABASE_PATH):
 backup=Path(backup);path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);check=validate_database(backup)
 if not check['valid']:raise ValueError('Backup database failed integrity check')
 rollback=None
 if path.exists():
  rollback_dir=path.parent/'backups';rollback_dir.mkdir(parents=True,exist_ok=True);rollback=rollback_dir/f'rollback_{utc_stamp()}_{uuid.uuid4().hex[:8]}{path.suffix}';shutil.copy2(path,rollback)
 temp=path.with_suffix('.restore.tmp');shutil.copy2(backup,temp);os.replace(temp,path)
 return {'restored':str(path),'source':str(backup),'rollback':str(rollback) if rollback else ''}
def _sanitize(value):
 if isinstance(value,dict):return {k:_sanitize(v) for k,v in value.items() if not any(token in k.lower() for token in ('key','secret','token','credential','password'))}
 if isinstance(value,list):return [_sanitize(x) for x in value]
 if isinstance(value,str):
  text=value.replace(str(BASE_DIR),'<APP_ROOT>').replace(str(Path.home()),'<USER_HOME>')
  return text
 return value
def support_bundle(diagnostics,repository_health,inventory=None,events=None):
 inventory=inventory or storage_inventory();events=events or []
 safe_events=[{'timestamp':x.get('timestamp'),'event':x.get('event'),'project_id':x.get('project_id','')[:8]} for x in events[:200]]
 report={'version':VERSION,'created_at':datetime.now(timezone.utc).isoformat(),'diagnostics':_sanitize(diagnostics),'repository':_sanitize(repository_health),'storage_summary':storage_summary(inventory),'files':[{'category':x['category'],'extension':Path(x['name']).suffix.lower(),'bytes':x['bytes']} for x in inventory],'events':safe_events,'exclusions':['credentials','project text','transcripts','audio content','absolute user paths']}
 out=BytesIO()
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:z.writestr('support-report.json',json.dumps(report,ensure_ascii=False,indent=2));z.writestr('README.txt','Sanitized PeaBox support bundle. No credentials, project text, transcripts, or media are included.\n')
 return out.getvalue(),report
