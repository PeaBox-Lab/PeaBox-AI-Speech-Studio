import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'peabox_voice_studio/screens';F=ROOT/'peabox_voice_studio/facades'
class ModularUiTests(unittest.TestCase):
 def test_registry_covers_all_navigation_pages(self):
  registry=(S/'registry.py').read_text()
  for page in ('Dashboard','Projects','Command Center','Preferences','Operations','Governance','Approvals','System Check','Provider Setup','Voice Library','Quality Studio','Audio Quality Lab','Timeline Studio','Script Blocks','Batch Production','Create Speech','Transcription','Render History','Roadmap & Help'):self.assertIn(f"'{page}'",registry)
 def test_all_screens_have_render_contract(self):
  for p in S.glob('*.py'):
   if p.name in {'__init__.py','registry.py'}:continue
   self.assertIn('render',{n.name for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)},p.name)
 def test_bootstrap_is_small(self):self.assertLess(len((ROOT/'app.py').read_text().splitlines()),35)
 def test_corporate_navigation_and_theme_remain(self):
  ui=(ROOT/'peabox_voice_studio/ui.py').read_text()
  for value in ('Executive Dashboard','Operations Center','Script Editor','Timeline Studio','Governance Center','--pb-navy','.pb-card'):self.assertIn(value,ui)
 def test_dashboard_and_history_content_remain(self):
  dashboard=(S/'dashboard.py').read_text();history=(S/'render_history.py').read_text()
  for value in ('Production readiness','Recommended workflow','Quick project access'):self.assertIn(value,dashboard)
  for value in ('Renders','Batch jobs','Timeline exports','Comparisons','Transcripts','Governance'):self.assertIn(value,history)
 def test_complex_screens_use_facades(self):
  mapping={'timeline_studio.py':'peabox_voice_studio.facades.timeline','batch_production.py':'peabox_voice_studio.facades.batch','transcription.py':'peabox_voice_studio.facades.transcription'}
  for screen,module in mapping.items():self.assertIn(f'from {module} import',(S/screen).read_text())
 def test_facade_exports_are_explicit(self):
  for p in F.glob('*.py'):
   if p.name=='__init__.py':continue
   source=p.read_text();self.assertIn('__all__',source);self.assertNotIn(' import *',source)
if __name__=='__main__':unittest.main()
