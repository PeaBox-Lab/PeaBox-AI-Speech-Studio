import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ProviderSandboxUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/provider_setup.py').read_text()
 def test_sandbox_panel_and_button(self):self.assertIn('Offline provider sandbox',self.source);self.assertIn('Run offline provider contract suite',self.source)
 def test_no_network_and_credential_disclosure(self):self.assertIn('without network access or real credentials',self.source);self.assertIn('No live provider call was made',self.source)
 def test_limitations_are_disclosed(self):
  for value in ('live credentials','quotas','billing','regional availability','service status'):self.assertIn(value,self.source)
 def test_results_include_contract_fields(self):
  for value in ('Provider','Passed','Voices','Audio fixture bytes','Issues'):self.assertIn(value,self.source)
if __name__=='__main__':unittest.main()
