import sys,types,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class State(dict):
 def __getattr__(self,n):return self[n]
 def __setattr__(self,n,v):self[n]=v
class UiRegressionTests(unittest.TestCase):
 def setUp(self):
  self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text();self.projects=(ROOT/'peabox_voice_studio/screens/projects.py').read_text()
 def test_quick_access_buttons_have_explicit_contrast(self):
  for marker in ('[data-testid="stSidebar"] .stButton > button','background:#203b64!important','color:#ffffff!important','-webkit-text-fill-color:#ffffff!important','opacity:1!important'):self.assertIn(marker,self.ui)
 def test_sidebar_button_hover_focus_and_disabled_are_styled(self):
  for state in ('button:hover','button:focus','button:disabled'):self.assertIn(state,self.ui)
 def test_navigation_is_deferred_not_widget_mutation(self):
  start=self.ui.index('def navigate_to');end=self.ui.index('def sidebar_navigation');body=self.ui[start:end]
  self.assertIn('pending_navigation',body);self.assertNotIn('nav_group =',body);self.assertNotIn('nav_page_',body)
 def test_pending_navigation_applied_before_selectbox(self):
  pending=self.ui.index('pending_page = st.session_state.pop');widget=self.ui.index('st.sidebar.selectbox("Workspace area"');self.assertLess(pending,widget)
 def test_project_screen_uses_context_project(self):
  self.assertIn('project = ctx.project',self.projects);self.assertNotIn('current_project()',self.projects)
 def test_navigate_to_only_writes_unowned_pending_key(self):
  fake=types.ModuleType('streamlit');fake.session_state=State();original=sys.modules.get('streamlit');sys.modules['streamlit']=fake
  try:
   sys.modules.pop('peabox_voice_studio.ui',None);from peabox_voice_studio.ui import navigate_to
   fake.session_state['nav_group']='Overview';navigate_to('Timeline Studio');self.assertEqual(fake.session_state['nav_group'],'Overview');self.assertEqual(fake.session_state['pending_navigation'],'Timeline Studio')
  finally:
   sys.modules.pop('peabox_voice_studio.ui',None)
   if original is None:sys.modules.pop('streamlit',None)
   else:sys.modules['streamlit']=original
if __name__=='__main__':unittest.main()
