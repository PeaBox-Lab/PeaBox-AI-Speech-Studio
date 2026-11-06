import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=ROOT/'peabox_voice_studio/screens'
class OnboardingUiTests(unittest.TestCase):
 def setUp(self):
  self.ui=(ROOT/'peabox_voice_studio/ui.py').read_text();self.registry=(S/'registry.py').read_text();self.command=(S/'command_center.py').read_text();self.dashboard=(S/'dashboard.py').read_text();self.preferences=(S/'preferences.py').read_text();self.all=''.join(p.read_text() for p in S.glob('*.py'))
 def test_command_center_is_registered(self):self.assertIn('"Command Center", "Command Center"',self.ui);self.assertIn("'Command Center':command_center.render",self.registry)
 def test_command_center_is_safe_navigation_only(self):self.assertIn('Commands navigate to safe screens',self.command);self.assertIn('disabled=not selected_command["available"]',self.command);self.assertNotIn('delete_project',self.command)
 def test_onboarding_progress_and_dismissal_exist(self):
  for marker in ('Getting started progress','Dismiss guide','onboarding_dismissed','st.progress'):self.assertIn(marker,self.dashboard)
 def test_empty_state_component_is_used(self):
  self.assertIn('def empty_state',self.ui)
  for title in ('No active project','No script blocks','No command found'):self.assertIn(title,self.all)
 def test_recent_commands_exist(self):self.assertIn('Recent commands',self.command);self.assertIn('recent_command_ids',self.command)
 def test_preferences_can_restore_onboarding(self):self.assertIn('Show onboarding again',self.preferences);self.assertIn('Clear recent commands',self.preferences)
if __name__=='__main__':unittest.main()
