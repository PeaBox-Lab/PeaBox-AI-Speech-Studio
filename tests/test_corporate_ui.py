import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SCREENS=ROOT/'peabox_voice_studio/screens'
class CorporateUiTests(unittest.TestCase):
 def setUp(self):
  self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text();self.app=(ROOT/'app.py').read_text();self.dashboard=(SCREENS/'dashboard.py').read_text();self.history=(SCREENS/'render_history.py').read_text()
 def test_theme_has_corporate_tokens_and_components(self):
  for token in ('--pb-navy','--pb-blue','--pb-border','.pb-topbar','.pb-card','.pb-status','.pb-step'):self.assertIn(token,self.ui)
 def test_theme_is_applied_before_navigation(self):self.assertLess(self.app.index('inject_corporate_theme(ui_preferences)'),self.app.index('page=sidebar_navigation'))
 def test_page_header_is_global(self):self.assertIn('page_header(page,VERSION,project)',self.app);self.assertIn('PAGE_META',self.ui)
 def test_dashboard_has_kpis_readiness_and_workflow(self):
  for marker in ('Production readiness','Recommended workflow','Recent project activity','kpi_card'):self.assertIn(marker,self.dashboard)
 def test_activity_screen_consolidates_histories(self):
  for label in ('Renders','Batch jobs','Timeline exports','Comparisons','Transcripts','Governance'):self.assertIn(f'"{label}"',self.history)
 def test_streamlit_magic_leak_remains_absent(self):
  leaks=[]
  for path in [ROOT/'app.py',*SCREENS.glob('*.py')]:
   source=path.read_text();tree=ast.parse(source)
   for node in ast.walk(tree):
    if isinstance(node,ast.Expr) and isinstance(node.value,ast.IfExp) and 'st.' in (ast.get_source_segment(source,node) or ''):leaks.append((path.name,node.lineno))
  self.assertEqual(leaks,[])
if __name__=='__main__':unittest.main()
