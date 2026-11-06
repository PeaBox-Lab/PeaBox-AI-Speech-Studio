import re
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "peabox_voice_studio" / "ui.py"
class VisualContractTests(unittest.TestCase):
    def setUp(self):
        self.source = UI.read_text(encoding="utf-8")
    def test_no_global_sidebar_wildcard_color_override(self):
        self.assertNotIn('[data-testid="stSidebar"] * { color:', self.source)
    def test_sidebar_select_has_explicit_dark_surface_and_white_text(self):
        self.assertIn('div[data-baseweb="select"] > div', self.source)
        self.assertIn('background:var(--pb-sidebar-control)!important', self.source)
        self.assertIn('-webkit-text-fill-color:#ffffff!important', self.source)
    def test_popover_restores_dark_text(self):
        self.assertIn('div[data-baseweb="popover"] li[role="option"]', self.source)
        self.assertIn('color:var(--pb-ink)!important', self.source)
    def test_selected_navigation_has_strong_active_state(self):
        self.assertIn('label:has(input:checked)', self.source)
        self.assertIn('box-shadow:inset 3px 0 0', self.source)
    def test_content_has_header_clearance(self):
        match = re.search(r'\.block-container\s*\{[^}]*padding:([^;]+)!important', self.source, flags=re.S)
        self.assertIsNotNone(match)
        self.assertIn('3.35rem', match.group(1))
    def test_banner_is_width_safe_and_not_clipped(self):
        match = re.search(r'\.pb-topbar\s*\{([^}]+)\}', self.source, flags=re.S)
        self.assertIsNotNone(match)
        topbar = match.group(1)
        for property_text in ('width:100%', 'max-width:100%', 'box-sizing:border-box', 'overflow:hidden'):
            self.assertIn(property_text, topbar)
    def test_responsive_breakpoints_exist(self):
        self.assertIn('@media (max-width:1100px)', self.source)
        self.assertIn('@media (max-width:760px)', self.source)
    def test_sidebar_labels_are_visible_and_controls_collapsed(self):
        self.assertIn('WORKSPACE AREA', self.source)
        self.assertIn('SCREENS', self.source)
        self.assertGreaterEqual(self.source.count('label_visibility="collapsed"'), 2)
if __name__ == "__main__": unittest.main()
