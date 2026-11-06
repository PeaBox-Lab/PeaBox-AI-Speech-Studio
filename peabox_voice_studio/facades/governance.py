from peabox_voice_studio.services.governance import ALLOWED_TRANSITIONS,APPROVAL_STATES,RISK_LEVELS,WORKFLOW_STATES,add_comment,add_decision,decide_approval,governance,governance_readiness,governance_summary,reopen_comment,request_approval,resolve_comment,supersede_decision,transition_status,update_project_governance
__all__=['ALLOWED_TRANSITIONS','APPROVAL_STATES','RISK_LEVELS','WORKFLOW_STATES','add_comment','add_decision','decide_approval','governance','governance_readiness','governance_summary','reopen_comment','request_approval','resolve_comment','supersede_decision','transition_status','update_project_governance']
def project_governance_row(project):
 summary=governance_summary(project);readiness=governance_readiness(project)
 return {'project_id':project.id,'project':project.name,'owner':summary['owner'] or 'Unassigned','workflow':summary['status'],'risk':summary['risk_level'],'open_comments':summary['open_comments'],'blocking_comments':summary['blocking_comments'],'pending_approvals':summary['pending_approvals'],'approved_requests':summary['approved_requests'],'ready':readiness['ready'],'issues':len(readiness['issues'])}
def approval_queue(project):
 return sorted(governance(project).get('approvals',[]),key=lambda x:(x.get('status')!='Pending',x.get('created_at','')))
def portfolio_governance(projects):return [project_governance_row(p) for p in projects]
__all__ += ['approval_queue','portfolio_governance','project_governance_row']
