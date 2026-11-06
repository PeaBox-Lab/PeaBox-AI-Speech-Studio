import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleaseConsistencyTests(unittest.TestCase):
 def test_launcher_matches_config_version(self):
  self.assertIn('v0.09.0',(ROOT/'start_windows.ps1').read_text())
  self.assertIn('VERSION = "0.09.0"',(ROOT/'peabox_voice_studio/config.py').read_text())
 def test_launcher_uses_constraints(self):
  self.assertIn('-c "constraints.txt"',(ROOT/'start_windows.ps1').read_text())
  self.assertTrue((ROOT/'constraints.txt').exists())
 def test_model_sidecars_are_ignored(self):
  self.assertIn('models/*.sha256',(ROOT/'.gitignore').read_text())
if __name__=='__main__': unittest.main()