import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class OnboardingUiTests(unittest.TestCase):
    def setUp(self):
        self.app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.ui = (ROOT / "peabox_voice_studio" / "ui.py").read_text(encoding="utf-8")
        screens = ROOT / "peabox_voice_studio" / "screens"
        self.command = (screens / "command_center.py").read_text(encoding="utf-8")
        self.dashboard = (screens / "dashboard.py").read_text(encoding="utf-8")
        self.preferences = (screens / "preferences.py").read_text(encoding="utf-8")
        self.registry = (screens / "registry.py").read_text(encoding="utf-8")
        self.all_source = self.app + self.command + self.dashboard + self.preferences
    def test_command_center_is_registered(self):
        self.assertIn('"Command Center", "Command Center"', self.ui)
        self.assertIn('"Command Center":command_center.render', self.registry)
    def test_command_center_is_safe_navigation_only(self):
        self.assertIn("Commands navigate to safe screens", self.command)
        self.assertIn('disabled=not selected_command["available"]', self.command)
        self.assertNotIn("delete_project", self.command)
    def test_onboarding_progress_and_dismissal_exist(self):
        for marker in ("Getting started progress", "Dismiss guide", "onboarding_dismissed", "st.progress"):
            self.assertIn(marker, self.all_source)
    def test_empty_state_component_is_used(self):
        self.assertIn("def empty_state", self.ui)
        for title in ("No active project", "No script blocks", "No command found"):
            self.assertIn(title, self.all_source)
    def test_recent_commands_exist(self):
        self.assertIn("Recent commands", self.command)
        self.assertIn("recent_command_ids", self.command)
    def test_preferences_can_restore_onboarding(self):
        self.assertIn("Show onboarding again", self.preferences)
        self.assertIn("Clear recent commands", self.preferences)
if __name__ == "__main__": unittest.main()