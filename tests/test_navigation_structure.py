import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NavigationStructureTests(unittest.TestCase):
    def setUp(self):
        self.app_source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.ui_source = (ROOT / "peabox_voice_studio" / "ui.py").read_text(encoding="utf-8")
        ast.parse(self.app_source); ast.parse(self.ui_source)

    def test_business_navigation_groups_exist(self):
        for group in ("Overview", "Production", "Audio & Quality", "Administration", "Support"):
            self.assertIn(f'"{group}"', self.ui_source)

    def test_professional_display_labels_exist(self):
        labels = ["Executive Dashboard", "Project Workspace", "Script Editor", "Speech Generator", "Batch Jobs", "Timeline Studio", "Transcription Studio", "Activity & History"]
        for label in labels: self.assertIn(f'"{label}"', self.ui_source)

    def test_all_internal_page_branches_exist(self):
        branches = ["Dashboard", "Projects", "System Check", "Provider Setup", "Voice Library", "Quality Studio", "Audio Quality Lab", "Timeline Studio", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History"]
        for page in branches: self.assertIn(f'page == "{page}"', self.app_source)

    def test_sidebar_uses_grouped_navigation(self):
        self.assertIn('selectbox("Workspace area"', self.ui_source)
        self.assertIn('radio("Navigation"', self.ui_source)
        self.assertNotIn('st.sidebar.radio("Studio"', self.app_source)

    def test_no_top_level_help_or_object_display_calls(self):
        for value in ("st.help(", "st.write(st.", "st.write(project)", "st.write(store)"):
            self.assertNotIn(value, self.app_source)


if __name__ == "__main__": unittest.main()
