from pathlib import Path
from uuid import uuid4
def check_project(p):
 issues=[];seen=set()
 if not p.name.strip():issues.append({'severity':'Error','code':'missing_name','repairable':True})
 for i,b in enumerate(p.blocks):
  if not b.id or b.id in seen:issues.append({'severity':'Error','code':'duplicate_block_id','index':i,'repairable':True})
  seen.add(b.id)
 for c in p.settings.get('timeline_clips',[]):
  if not Path(c.get('file','')).exists():issues.append({'severity':'Warning','code':'missing_clip','repairable':False})
 return {'project_id':p.id,'healthy':not issues,'errors':sum(x['severity']=='Error' for x in issues),'warnings':sum(x['severity']=='Warning' for x in issues),'issues':issues}
def repair_preview(p,r=None):
 return [{'action':'set_project_name'} if x['code']=='missing_name' else {'action':'replace_block_id','index':x['index']} for x in (r or check_project(p))['issues'] if x.get('repairable')]
def apply_repairs(p,actions):
 for a in actions:
  if a['action']=='set_project_name':p.name='Untitled Project'
  else:p.blocks[a['index']].id=uuid4().hex
 return actions
