import ast
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app.py"
UI = ROOT / "peabox_voice_studio" / "ui.py"
class StreamlitMagicTests(unittest.TestCase):
    def test_no_conditional_expression_returns_streamlit_element(self):
        source = APP.read_text(encoding="utf-8")
        tree = ast.parse(source)
        leaks = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Expr) or not isinstance(node.value, ast.IfExp):
                continue
            text = ast.get_source_segment(source, node) or ""
            if "st." in text:
                leaks.append((node.lineno, text))
        self.assertEqual(leaks, [], f"Streamlit magic would render internal objects: {leaks}")
    def test_sidebar_status_uses_statement_if(self):
        source = UI.read_text(encoding="utf-8")
        self.assertIn("if project:", source)
        self.assertIn("else:", source)
        self.assertIn("ACTIVE PROJECT", source)
        self.assertIn("NO ACTIVE PROJECT", source)
    def test_visible_version_marker(self):
        source = UI.read_text(encoding="utf-8")
        self.assertIn('st.sidebar.caption(f"Enterprise workspace · v{version}")', source)
        self.assertIn("sidebar_navigation(VERSION,project,ui_preferences)", APP.read_text(encoding="utf-8"))
if __name__ == "__main__":
    unittest.main()
