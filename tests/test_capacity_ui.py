import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CapacityUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_capacity_tab_and_categories_exist(self):
  for value in ("'Capacity'",'Generated outputs','Downloaded models','Backups and recovery','Worker queue and events'):self.assertIn(value,self.source)
 def test_policy_controls_exist(self):
  for value in ('Enable local storage quotas','Warning threshold percent','Save storage policy'):self.assertIn(value,self.source)
 def test_reservation_controls_exist(self):
  for value in ('Create capacity reservation','Release selected reservation','Reservation purpose'):self.assertIn(value,self.source)
 def test_project_json_exclusion_is_disclosed(self):self.assertIn('Project JSON is excluded',self.source)
if __name__=='__main__':unittest.main()
