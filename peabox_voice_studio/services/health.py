from pathlib import Path
from uuid import uuid4
from peabox_voice_studio.models import Project,utc_now
VALID_JOB={'queued','running','rendered','failed','cancelled'}
def check_project(project):
 issues=[];seen=set()
 for i,b in enumerate(project.blocks,1):
  if b.id in seen:issues.append(_issue('error','duplicate_block_id',f'Duplicate block ID at block {i}',{'index':i}))
  seen.add(b.id)
  if not b.title.strip():issues.append(_issue('warning','empty_block_title',f'Block {i} title is empty',{'index':i}))
 for j,job in enumerate(project.settings.get('batch_jobs',[]),1):
  if job.get('project_id')!=project.id:issues.append(_issue('error','job_project_mismatch',f'Job {j} references another project',{'index':j}))
  for k,item in enumerate(job.get('items',[]),1):
   if item.get('status') not in VALID_JOB:issues.append(_issue('error','invalid_job_status',f'Job {j} item {k} has invalid status',{'job':j,'item':k}))
   if item.get('file') and not Path(item['file']).exists():issues.append(_issue('warning','missing_job_output',f'Job {j} item {k} output is missing',{'job':j,'item':k}))
 for i,clip in enumerate(project.settings.get('audio_clips',[]),1):
  if not clip.get('id'):issues.append(_issue('error','missing_clip_id',f'Clip {i} has no ID',{'index':i}))
  if clip.get('file') and not Path(clip['file']).exists():issues.append(_issue('error','missing_clip_file',f'Clip {i} file is missing',{'index':i}))
 gov=project.settings.get('governance',{})
 if gov.get('status') in {'Approved','Published'} and not gov.get('owner'):issues.append(_issue('warning','approved_without_owner','Approved/published project has no owner',{}))
 errors=sum(x['severity']=='error' for x in issues);warnings=sum(x['severity']=='warning' for x in issues)
 return {'project_id':project.id,'checked_at':utc_now(),'healthy':errors==0,'errors':errors,'warnings':warnings,'issues':issues}
def repair_preview(project,report):
 actions=[]
 for issue in report['issues']:
  code=issue['code'];ctx=issue['context']
  if code=='duplicate_block_id':actions.append({'action':'regenerate_block_id','index':ctx['index'],'description':issue['message']})
  elif code=='empty_block_title':actions.append({'action':'set_block_title','index':ctx['index'],'description':issue['message']})
  elif code=='job_project_mismatch':actions.append({'action':'repair_job_project','index':ctx['index'],'description':issue['message']})
  elif code=='invalid_job_status':actions.append({'action':'set_job_failed','job':ctx['job'],'item':ctx['item'],'description':issue['message']})
  elif code=='missing_job_output':actions.append({'action':'clear_job_output','job':ctx['job'],'item':ctx['item'],'description':issue['message']})
  elif code=='missing_clip_id':actions.append({'action':'regenerate_clip_id','index':ctx['index'],'description':issue['message']})
  elif code=='missing_clip_file':actions.append({'action':'disable_missing_clip','index':ctx['index'],'description':issue['message']})
 return actions
def apply_repairs(project,actions):
 applied=[]
 for a in actions:
  if a['action']=='regenerate_block_id':project.blocks[a['index']-1].id=uuid4().hex
  elif a['action']=='set_block_title':project.blocks[a['index']-1].title=f"Block {a['index']}"
  elif a['action']=='repair_job_project':project.settings['batch_jobs'][a['index']-1]['project_id']=project.id
  elif a['action']=='set_job_failed':project.settings['batch_jobs'][a['job']-1]['items'][a['item']-1].update(status='failed',error='Repaired invalid status')
  elif a['action']=='clear_job_output':project.settings['batch_jobs'][a['job']-1]['items'][a['item']-1].update(file=None,status='failed',error='Output file missing')
  elif a['action']=='regenerate_clip_id':project.settings['audio_clips'][a['index']-1]['id']=uuid4().hex
  elif a['action']=='disable_missing_clip':project.settings['audio_clips'][a['index']-1]['enabled']=False
  else:continue
  applied.append(a['action'])
 project.settings['last_health_repair']={'at':utc_now(),'actions':applied};return applied
def _issue(severity,code,message,context):return {'severity':severity,'code':code,'message':message,'context':context}
