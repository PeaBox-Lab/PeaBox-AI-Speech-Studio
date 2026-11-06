from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.models import utc_now
VALID={'queued','running','rendered','failed','cancelled'}
def check_project(p):
 issues=[];seen=set()
 for i,b in enumerate(p.blocks,1):
  if b.id in seen:issues.append(issue('error','duplicate_block_id',f'Duplicate block ID at block {i}',i))
  seen.add(b.id)
  if not b.title.strip():issues.append(issue('warning','empty_block_title',f'Block {i} title is empty',i))
 for j,job in enumerate(p.settings.get('batch_jobs',[]),1):
  if job.get('project_id')!=p.id:issues.append(issue('error','job_project_mismatch',f'Job {j} references another project',j))
  for k,x in enumerate(job.get('items',[]),1):
   if x.get('status') not in VALID:issues.append({'severity':'error','code':'invalid_job_status','message':f'Job {j} item {k} invalid','context':{'job':j,'item':k}})
   if x.get('file') and not Path(x['file']).exists():issues.append({'severity':'warning','code':'missing_job_output','message':f'Job {j} item {k} missing','context':{'job':j,'item':k}})
 for i,c in enumerate(p.settings.get('audio_clips',[]),1):
  if not c.get('id'):issues.append(issue('error','missing_clip_id',f'Clip {i} has no ID',i))
  if c.get('file') and not Path(c['file']).exists():issues.append(issue('error','missing_clip_file',f'Clip {i} file missing',i))
 errors=sum(x['severity']=='error' for x in issues);warnings=sum(x['severity']=='warning' for x in issues)
 return {'project_id':p.id,'checked_at':utc_now(),'healthy':errors==0,'errors':errors,'warnings':warnings,'issues':issues}
def repair_preview(p,r):
 result=[]
 for x in r['issues']:
  c=x['code'];ctx=x['context'];a=None
  if c=='duplicate_block_id':a={'action':'regenerate_block_id','index':ctx['index']}
  elif c=='empty_block_title':a={'action':'set_block_title','index':ctx['index']}
  elif c=='job_project_mismatch':a={'action':'repair_job_project','index':ctx['index']}
  elif c=='invalid_job_status':a={'action':'set_job_failed',**ctx}
  elif c=='missing_job_output':a={'action':'clear_job_output',**ctx}
  elif c=='missing_clip_id':a={'action':'regenerate_clip_id','index':ctx['index']}
  elif c=='missing_clip_file':a={'action':'disable_missing_clip','index':ctx['index']}
  if a:a['description']=x['message'];result.append(a)
 return result
def apply_repairs(p,actions):
 done=[]
 for a in actions:
  n=a['action']
  if n=='regenerate_block_id':p.blocks[a['index']-1].id=uuid4().hex
  elif n=='set_block_title':p.blocks[a['index']-1].title=f"Block {a['index']}"
  elif n=='repair_job_project':p.settings['batch_jobs'][a['index']-1]['project_id']=p.id
  elif n=='set_job_failed':p.settings['batch_jobs'][a['job']-1]['items'][a['item']-1].update(status='failed',error='Repaired invalid status')
  elif n=='clear_job_output':p.settings['batch_jobs'][a['job']-1]['items'][a['item']-1].update(file=None,status='failed',error='Output missing')
  elif n=='regenerate_clip_id':p.settings['audio_clips'][a['index']-1]['id']=uuid4().hex
  elif n=='disable_missing_clip':p.settings['audio_clips'][a['index']-1]['enabled']=False
  else:continue
  done.append(n)
 p.settings['last_health_repair']={'at':utc_now(),'actions':done};return done
def issue(sev,code,msg,index):return {'severity':sev,'code':code,'message':msg,'context':{'index':index}}
