import ast
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ScreenArchitectureTests(unittest.TestCase):
    def test_registry_has_unique_modular_screens(self):
        source=(ROOT/'peabox_voice_studio/screens/registry.py').read_text()
        tree=ast.parse(source)
        registry=next(n.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SCREEN_RENDERERS' for t in n.targets))
        keys=[k.value for k in registry.keys]
        self.assertEqual(len(keys),len(set(keys)))
        self.assertEqual(set(keys),{'Dashboard','Command Center','Preferences','Operations','Roadmap & Help'})
    def test_every_screen_exposes_renderer(self):
        for name in ('dashboard','command_center','preferences','operations','help'):
            tree=ast.parse((ROOT/f'peabox_voice_studio/screens/{name}.py').read_text())
            functions={n.name for n in tree.body if isinstance(n,ast.FunctionDef)}
            self.assertIn('render',functions)
    def test_bootstrap_dispatches_registry(self):
        source=(ROOT/'app.py').read_text()
        self.assertIn('if page in SCREEN_RENDERERS:',source)
        self.assertIn('render_screen(page, app_context)',source)
        self.assertLess(len(source.splitlines()),900)
    def test_context_has_required_services(self):
        annotations=__import__('peabox_voice_studio.context',fromlist=['AppContext']).AppContext.__annotations__
        self.assertTrue({'version','store','project','preferences','configured_providers','open_project','save_project','set_active_project'}<=set(annotations))
if __name__=='__main__':unittest.main()
