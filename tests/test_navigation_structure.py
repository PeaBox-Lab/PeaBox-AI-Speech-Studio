import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class NavigationStructureTests(unittest.TestCase):
 def setUp(self):
  self.app=(ROOT/'app.py').read_text();self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text();self.registry=(ROOT/'peabox_voice_studio/screens/registry.py').read_text();ast.parse(self.app);ast.parse(self.ui);ast.parse(self.registry)
 def test_business_navigation_groups_exist(self):
  for group in ('Overview','Production','Audio & Quality','Administration','Support'):self.assertIn(f'"{group}"',self.ui)
 def test_professional_display_labels_exist(self):
  for label in ('Executive Dashboard','Project Workspace','Command Center','Interface Preferences','Operations Center','Script Editor','Speech Generator','Batch Jobs','Timeline Studio','Transcription Studio','Governance Center','Approval Queue','Activity & History'):self.assertIn(f'"{label}"',self.ui)
 def test_every_navigation_page_is_registered(self):
  for page in ('Dashboard','Projects','Command Center','Preferences','Operations','Governance','Approvals','System Check','Provider Setup','Voice Library','Quality Studio','Audio Quality Lab','Timeline Studio','Script Blocks','Batch Production','Create Speech','Transcription','Render History','Roadmap & Help'):self.assertIn(f"'{page}'",self.registry)
 def test_sidebar_uses_grouped_navigation(self):self.assertIn('selectbox("Workspace area"',self.ui);self.assertIn('radio("Navigation"',self.ui);self.assertNotIn('st.sidebar.radio("Studio"',self.app)
 def test_bootstrap_is_dispatch_only(self):self.assertIn('render_screen(page,ctx)',self.app);self.assertLess(len(self.app.splitlines()),60)
if __name__=='__main__':unittest.main()
