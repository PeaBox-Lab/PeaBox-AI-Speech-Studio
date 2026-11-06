import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'peabox_voice_studio/screens';F=ROOT/'peabox_voice_studio/facades'
class FacadeBoundaryTests(unittest.TestCase):
 def test_facaded_screens_do_not_import_hidden_services(self):
  forbidden={'timeline_studio.py':('services.timeline','services.bundles'),'batch_production.py':('services.batch','services.jobs'),'transcription.py':('services.transcripts','services.diagnostics')}
  for name,parts in forbidden.items():
   source=(S/name).read_text()
   for part in parts:self.assertNotIn(part,source,name)
 def test_facade_all_matches_imported_names(self):
  for p in F.glob('*.py'):
   if p.name=='__init__.py':continue
   tree=ast.parse(p.read_text());imports=set();exports=None
   for n in tree.body:
    if isinstance(n,(ast.Import,ast.ImportFrom)):imports.update(a.asname or a.name for a in n.names)
    elif isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='__all__' for t in n.targets):exports={x.value for x in n.value.elts}
   self.assertEqual(imports,exports,p.name)
 def test_facades_do_not_import_streamlit(self):
  for p in F.glob('*.py'):self.assertNotIn('streamlit',p.read_text())
 def test_no_wildcard_imports_in_screens(self):
  for p in S.glob('*.py'):self.assertNotIn(' import *',p.read_text())
if __name__=='__main__':unittest.main()
