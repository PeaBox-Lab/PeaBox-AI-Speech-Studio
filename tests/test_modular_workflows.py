import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'peabox_voice_studio/screens';F=ROOT/'peabox_voice_studio/facades'
class ModularWorkflowTests(unittest.TestCase):
 def test_registry_covers_19_pages(self):
  source=(S/'registry.py').read_text();tree=ast.parse(source);node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCREEN_RENDERERS' for t in n.targets));self.assertEqual(len(node.keys),19)
 def test_all_screens_have_render(self):
  for p in S.glob('*.py'):
   if p.name in {'__init__.py','registry.py'}:continue
   self.assertIn('render',{n.name for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef)},p.name)
 def test_portfolio_and_governance_screens_use_facades(self):
  self.assertIn('facades.portfolio',(S/'projects.py').read_text())
  for name in ('governance.py','approvals.py','render_history.py'):self.assertIn('facades.governance',(S/name).read_text())
 def test_hidden_services_are_not_imported_by_facaded_screens(self):
  self.assertNotIn('services.projects',(S/'projects.py').read_text());self.assertNotIn('services.governance',(S/'governance.py').read_text());self.assertNotIn('services.governance',(S/'approvals.py').read_text())
 def test_operations_has_portfolio_metrics(self):
  source=(S/'operations.py').read_text()
  for text in ('Open reviews','Pending approvals','Unassigned','portfolio_governance'):self.assertIn(text,source)
 def test_bootstrap_is_small(self):self.assertLess(len((ROOT/'app.py').read_text().splitlines()),25)
 def test_facades_have_explicit_exports(self):
  for p in F.glob('*.py'):
   if p.name=='__init__.py':continue
   self.assertIn('__all__',p.read_text());self.assertNotIn(' import *',p.read_text())
if __name__=='__main__':unittest.main()
