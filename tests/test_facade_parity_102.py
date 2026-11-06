import unittest
from peabox_voice_studio.facades import governance,portfolio
from peabox_voice_studio.services import governance as gs,projects,preferences,bundles
class FacadeParityTests(unittest.TestCase):
 def test_governance_exports_match_services(self):
  for name in governance.__all__:
   if hasattr(gs,name):self.assertIs(getattr(governance,name),getattr(gs,name))
 def test_portfolio_exports_match_services(self):
  expected={'ProjectStore':projects.ProjectStore,'export_project':projects.export_project,'split_script_into_blocks':projects.split_script_into_blocks,'toggle_favorite':preferences.toggle_favorite,'resolve_projects':preferences.resolve_projects,'save_preferences':preferences.save_preferences,'mark_project_opened':preferences.mark_project_opened,'export_timeline_bundle':bundles.export_timeline_bundle,'import_timeline_bundle':bundles.import_timeline_bundle}
  for name,value in expected.items():self.assertIs(getattr(portfolio,name),value)
 def test_exports_unique_and_exist(self):
  for module in (governance,portfolio):self.assertEqual(len(module.__all__),len(set(module.__all__)));self.assertTrue(all(hasattr(module,n) for n in module.__all__))
if __name__=='__main__':unittest.main()
