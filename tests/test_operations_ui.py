import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class OperationsUiTests(unittest.TestCase):
 def setUp(self):self.app=(ROOT/'app.py').read_text();self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text()
 def test_screen(self):self.assertIn('"Operations Center", "Operations"',self.ui);self.assertIn('page == "Operations"',self.app)
 def test_repairs_are_preview_and_confirmed(self):self.assertIn('previewed safe repairs',self.app);self.assertIn('Apply repair plan',self.app)
 def test_plans(self):self.assertIn('Create maintenance plan',self.app);self.assertIn('Complete plan',self.app)
if __name__=='__main__':unittest.main()
