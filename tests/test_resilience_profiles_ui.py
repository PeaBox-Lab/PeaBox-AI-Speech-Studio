import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ResilienceProfilesUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_profiles_tab_and_disclosure(self):self.assertIn("'Profiles'",self.source);self.assertIn('without credentials',self.source);self.assertIn('not authenticated identities',self.source)
 def test_profile_actions_exist(self):
  for value in ('Create Draft resilience profile','Advance profile','Request changes','Archive profile','Clone profile','Delete Draft','Probe Active profile'):self.assertIn(value,self.source)
 def test_profile_identity_and_review_fields(self):
  for value in ('Profile actor label','Creator','Reviewer','Review or transition note'):self.assertIn(value,self.source)
 def test_audit_history_is_visible(self):self.assertIn('Resilience profile audit history',self.source)
if __name__=='__main__':unittest.main()
