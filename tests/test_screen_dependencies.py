import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SCREENS=ROOT/'peabox_voice_studio/screens'
SKIP={'__init__.py','registry.py'}
def modules():return [p for p in SCREENS.glob('*.py') if p.name not in SKIP]
class ScreenDependencyTests(unittest.TestCase):
 def test_shared_wildcard_module_is_removed(self):self.assertFalse((SCREENS/'dependencies.py').exists())
 def test_no_wildcard_imports(self):
  for path in modules():
   tree=ast.parse(path.read_text())
   stars=[n for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and any(a.name=='*' for a in n.names)]
   self.assertEqual(stars,[],path.name)
 def test_no_screen_imports_application_or_peer_screens(self):
  for path in modules():
   tree=ast.parse(path.read_text())
   for node in ast.walk(tree):
    if isinstance(node,ast.Import):
     for alias in node.names:self.assertNotEqual(alias.name,'app',path.name);self.assertFalse(alias.name.startswith('peabox_voice_studio.screens.'),path.name)
    elif isinstance(node,ast.ImportFrom):
     self.assertNotEqual(node.module,'app',path.name);self.assertFalse((node.module or '').startswith('peabox_voice_studio.screens.'),path.name)
 def test_screen_import_budget_is_bounded(self):
  for path in modules():
   tree=ast.parse(path.read_text());count=sum(len(n.names) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom)))
   self.assertLessEqual(count,25,f'{path.name} imports {count} names')
 def test_imported_names_are_actually_used(self):
  for path in modules():
   tree=ast.parse(path.read_text());used={n.id for n in ast.walk(tree) if isinstance(n,ast.Name) and isinstance(n.ctx,ast.Load)};imported=[]
   for node in tree.body:
    if isinstance(node,(ast.Import,ast.ImportFrom)):imported.extend(a.asname or a.name.split('.')[0] for a in node.names)
   unused=sorted(set(imported)-used);self.assertEqual(unused,[],f'{path.name}: {unused}')
if __name__=='__main__':unittest.main()
