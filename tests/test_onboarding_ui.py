import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OnboardingUiTests(unittest.TestCase):
    def setUp(self):
        self.app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.ui = (ROOT / "peabox_voice_studio" / "ui.py").read_text(encoding="utf-8")

    def test_command_center_is_registered(self):
        self.assertIn('"Command Center", "Command Center"', self.ui)
        self.assertIn('page == "Command Center"', self.app)

    def test_command_center_is_safe_navigation_only(self):
        self.assertIn("Commands navigate to safe screens", self.app)
        self.assertIn('disabled=not selected_command["available"]', self.app)
        self.assertNotIn("delete_project", self.app[self.app.index('page == "Command Center"'):self.app.index('page == "Preferences"')])

    def test_onboarding_progress_and_dismissal_exist(self):
        for marker in ("Getting started progress", "Dismiss guide", "onboarding_dismissed", "st.progress"):
            self.assertIn(marker, self.app)

    def test_empty_state_component_is_used(self):
        self.assertIn("def empty_state", self.ui)
        for title in ("No active project", "No script blocks", "No command found"):
            self.assertIn(title, self.app)

    def test_recent_commands_exist(self):
        self.assertIn("Recent commands", self.app)
        self.assertIn("recent_command_ids", self.app)

    def test_preferences_can_restore_onboarding(self):
        self.assertIn("Show onboarding again", self.app)
        self.assertIn("Clear recent commands", self.app)


if __name__ == "__main__": unittest.main()
