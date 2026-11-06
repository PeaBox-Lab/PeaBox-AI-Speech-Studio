from pathlib import Path
from uuid import uuid4

def check_project(project):
    issues=[];seen=set()
    if not project.name.strip():issues.append({'severity':'Error','code':'missing_name','message':'Project name is empty','repairable':True})
    for index,block in enumerate(project.blocks):
        if not block.id or block.id in seen:issues.append({'severity':'Error','code':'duplicate_block_id','message':f'Block {index+1} needs a unique identity','repairable':True,'index':index})
        seen.add(block.id)
    for clip in project.settings.get('timeline_clips',[]):
        path=Path(clip.get('file',''))
        if not path.exists():issues.append({'severity':'Warning','code':'missing_clip','message':f"Missing timeline asset: {clip.get('file_name','unknown')}",'repairable':False})
    errors=sum(x['severity']=='Error' for x in issues);warnings=sum(x['severity']=='Warning' for x in issues)
    return {'project_id':project.id,'healthy':not issues,'errors':errors,'warnings':warnings,'issues':issues}
def repair_preview(project,report=None):
    report=report or check_project(project);actions=[]
    for issue in report['issues']:
        if issue['code']=='missing_name':actions.append({'action':'set_project_name','description':'Set project name to Untitled Project'})
        elif issue['code']=='duplicate_block_id':actions.append({'action':'replace_block_id','index':issue['index'],'description':f"Assign a new identity to block {issue['index']+1}"})
    return actions
def apply_repairs(project,actions):
    applied=[]
    for action in actions:
        if action['action']=='set_project_name':project.name='Untitled Project';applied.append(action)
        elif action['action']=='replace_block_id':project.blocks[action['index']].id=uuid4().hex;applied.append(action)
    return applied
