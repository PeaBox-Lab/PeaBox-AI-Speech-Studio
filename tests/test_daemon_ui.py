import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DaemonUiTests(unittest.TestCase):
 def setUp(self):self.screen=(ROOT/'peabox_voice_studio/screens/batch_production.py').read_text();self.cli=(ROOT/'worker_local.py').read_text();self.ps=(ROOT/'start_worker_windows.ps1').read_text()
 def test_daemon_controls_exist(self):
  for label in ('Pause daemon','Resume daemon','Drain daemon','Shutdown daemon'):self.assertIn(label,self.screen)
 def test_status_and_command_are_visible(self):self.assertIn('daemon_status()',self.screen);self.assertIn('python worker_local.py --daemon',self.screen)
 def test_cli_modes_exist(self):
  for flag in ('--daemon','--status','--pause','--resume','--drain','--shutdown'):self.assertIn(flag,self.cli)
 def test_windows_launcher_uses_existing_environment(self):self.assertIn('.venv\\Scripts\\python.exe',self.ps);self.assertIn('worker_local.py',self.ps);self.assertIn('--daemon',self.ps);self.assertNotIn('pip install',self.ps)
if __name__=='__main__':unittest.main()
