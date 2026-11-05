import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NavigationStructureTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.tree = ast.parse(self.source)

    def test_all_expected_pages_are_registered(self):
        expected = ["Projects", "System Check", "Provider Setup", "Voice Library", "Quality Studio", "Audio Quality Lab", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History", "Roadmap & Help"]
        for page in expected:
            self.assertIn(f'"{page}"', self.source)

    def test_all_primary_page_branches_exist(self):
        branches = ["Projects", "System Check", "Provider Setup", "Voice Library", "Quality Studio", "Audio Quality Lab", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History"]
        for page in branches:
            self.assertIn(f'page == "{page}"', self.source)

    def test_no_top_level_help_or_object_display_calls(self):
        forbidden = ("st.help(", "st.write(st.", "st.write(project)", "st.write(store)")
        for value in forbidden:
            self.assertNotIn(value, self.source)


if __name__ == "__main__":
    unittest.main()
