import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class MaintenanceUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_maintenance_tab_and_disclosure(self):self.assertIn("'Maintenance'",self.source);self.assertIn('no background scheduler runs',self.source)
 def test_retention_is_preview_first(self):self.assertLess(self.source.index("st.subheader('Retention preview')"),self.source.index("st.button('Apply retention preview'"))
 def test_retention_requires_confirmation(self):self.assertIn('Permanently remove every file in this retention preview',self.source);self.assertIn('disabled=not retention_confirm',self.source)
 def test_plan_actions_are_available(self):
  for label in ('Create maintenance plan','Complete maintenance plan','Pause plan','Resume plan'):self.assertIn(label,self.source)
if __name__=='__main__':unittest.main()
