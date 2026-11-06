import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class ProductivityUiTests(unittest.TestCase):
    def setUp(self):
        self.app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.ui = (ROOT / "peabox_voice_studio" / "ui.py").read_text(encoding="utf-8")
    def test_preferences_screen_is_registered(self):
        self.assertIn('"Interface Preferences", "Preferences"', self.ui)
        self.assertIn('page == "Preferences"', self.app)
    def test_sidebar_has_quick_access(self):
        self.assertIn("QUICK ACCESS", self.ui)
        for target in ("Dashboard", "Script Blocks", "Create Speech", "Timeline Studio"):
            self.assertIn(f'("{target.split()[0] if target != "Create Speech" else "Generate"}', self.ui)
    def test_programmatic_navigation_is_supported(self):
        self.assertIn("def navigate_to(page: str)", self.ui)
        self.assertIn("st.session_state.nav_group", self.ui)
        self.assertIn('st.session_state[f"nav_page_{group}"]', self.ui)
    def test_dashboard_has_project_quick_actions(self):
        for label in ("Edit script", "Generate speech", "Run batch", "Open timeline", "Review governance"):
            self.assertIn(label, self.app)
    def test_favorites_and_recents_exist(self):
        for marker in ("favorite_project_ids", "recent_project_ids", "Quick project access", "Add favorite", "Remove favorite"):
            self.assertIn(marker, self.app)
    def test_preferences_affect_theme(self):
        for marker in ("compact_navigation", "reduced_motion", "density_css", "motion_css"):
            self.assertIn(marker, self.ui)
    def test_dashboard_detail_modes_exist(self):
        self.assertIn('["Compact", "Standard", "Detailed"]', self.app)
        self.assertIn('dashboard_detail == "Detailed"', self.app)
if __name__ == "__main__": unittest.main()