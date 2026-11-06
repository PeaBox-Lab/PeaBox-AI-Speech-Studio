import unittest
from peabox_voice_studio.facades.governance import approval_queue,portfolio_governance,project_governance_row
from peabox_voice_studio.facades.portfolio import portfolio_summary,project_access_rows
from peabox_voice_studio.models import Project,ScriptBlock
from peabox_voice_studio.services.governance import request_approval,update_project_governance
class WorkflowFacadeTests(unittest.TestCase):
 def test_portfolio_summary(self):
  a=Project(name='A',script='abc',blocks=[ScriptBlock(title='One')]);b=Project(name='B',script='xy');b.render_history=[{'x':1}];self.assertEqual(portfolio_summary([a,b]),{'projects':2,'blocks':1,'characters':5,'renders':1})
 def test_project_access_deduplicates_favorites_and_recents(self):
  a=Project(name='A');b=Project(name='B');rows=project_access_rows([a,b],{'favorite_project_ids':[a.id],'recent_project_ids':[a.id,b.id]});self.assertEqual([x['id'] for x in rows],[a.id,b.id]);self.assertTrue(rows[0]['favorite'])
 def test_governance_row_and_portfolio(self):
  p=Project(name='Governed');update_project_governance(p,'actor','Owner',[],'High','',True,True);row=project_governance_row(p);self.assertEqual(row['owner'],'Owner');self.assertEqual(row['risk'],'High');self.assertEqual(portfolio_governance([p]),[row])
 def test_approval_queue_puts_pending_first(self):
  p=Project(name='Approval');first=request_approval(p,'A','R','First','');second=request_approval(p,'A','R','Second','');next(x for x in p.settings['governance']['approvals'] if x['id']==first['id'])['status']='Approved';queue=approval_queue(p);self.assertEqual(queue[0]['id'],second['id']);self.assertEqual(queue[-1]['id'],first['id'])
if __name__=='__main__':unittest.main()
