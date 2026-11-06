import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'peabox_voice_studio/screens'
EXPECTED={'Dashboard','Projects','Command Center','Preferences','Operations','Governance','Approvals','System Check','Provider Setup','Voice Library','Quality Studio','Audio Quality Lab','Timeline Studio','Script Blocks','Batch Production','Create Speech','Transcription','Render History','Roadmap & Help'}
class ScreenArchitectureTests(unittest.TestCase):
 def test_registry_has_every_page_once(self):
  tree=ast.parse((S/'registry.py').read_text());node=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCREEN_RENDERERS' for t in n.targets));keys=[k.value for k in node.keys];self.assertEqual(set(keys),EXPECTED);self.assertEqual(len(keys),len(set(keys)))
 def test_every_screen_exposes_render(self):
  registry=(S/'registry.py').read_text()
  modules={v.split('.')[0] for v in [ast.unparse(x) for n in ast.walk(ast.parse(registry)) if isinstance(n,ast.Dict) for x in n.values]}
  for module in modules:
   tree=ast.parse((S/f'{module}.py').read_text());self.assertIn('render',{n.name for n in tree.body if isinstance(n,ast.FunctionDef)})
 def test_context_contract_is_complete(self):
  from peabox_voice_studio.context import AppContext
  required={'version','store','project','preferences','profiles','voice_catalogs','configured_providers','save_project','open_project','set_active_project'};self.assertTrue(required<=set(AppContext.__annotations__))
 def test_bootstrap_stays_small(self):self.assertLess(len((ROOT/'app.py').read_text().splitlines()),60)
 def test_screens_do_not_import_application(self):
  for path in S.glob('*.py'):
   tree=ast.parse(path.read_text())
   imports=[n for n in ast.walk(tree) if isinstance(n,(ast.Import,ast.ImportFrom))]
   self.assertFalse(any((isinstance(n,ast.Import) and any(x.name=='app' for x in n.names)) or (isinstance(n,ast.ImportFrom) and n.module=='app') for n in imports))
if __name__=='__main__':unittest.main()
