import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CorporateUiTests(unittest.TestCase):
    def setUp(self):
        self.ui = (ROOT / "peabox_voice_studio" / "ui.py").read_text(encoding="utf-8")
        self.app = (ROOT / "app.py").read_text(encoding="utf-8")

    def test_theme_has_corporate_tokens_and_components(self):
        for token in ("--pb-navy", "--pb-blue", "--pb-border", ".pb-topbar", ".pb-card", ".pb-status", ".pb-step"):
            self.assertIn(token, self.ui)

    def test_theme_is_applied_before_navigation(self):
        self.assertLess(self.app.index("inject_corporate_theme()"), self.app.index("page = sidebar_navigation"))

    def test_page_header_is_global(self):
        self.assertIn("page_header(page, VERSION, project)", self.app)
        self.assertIn("PAGE_META", self.ui)

    def test_dashboard_has_kpis_readiness_and_workflow(self):
        for marker in ("Production readiness", "Recommended workflow", "Recent project activity", "kpi_card"):
            self.assertIn(marker, self.app)

    def test_activity_screen_consolidates_histories(self):
        for label in ("Renders", "Batch jobs", "Timeline exports", "Comparisons", "Transcripts"):
            self.assertIn(f'"{label}"', self.app)

    def test_streamlit_magic_leak_remains_absent(self):
        tree = ast.parse(self.app)
        leaks=[]
        for node in ast.walk(tree):
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.IfExp):
                text=ast.get_source_segment(self.app,node) or ""
                if "st." in text: leaks.append(text)
        self.assertEqual(leaks, [])


if __name__ == "__main__": unittest.main()
