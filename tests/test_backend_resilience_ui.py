import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class BackendResilienceUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/operations.py').read_text()
 def test_resilience_tab_and_controls(self):
  for value in ("'Resilience'",'Retry attempts','Initial retry delay seconds','Operation timeout seconds','Circuit failure threshold','Circuit recovery seconds'):self.assertIn(value,self.source)
 def test_health_probe_and_metrics(self):
  for value in ('Run backend health probes','Circuit','Retries','Timeouts','Last error'):self.assertIn(value,self.source)
 def test_runtime_only_disclosure(self):self.assertIn('wrap a backend at runtime',self.source);self.assertIn('before any future remote backend is approved',self.source)
if __name__=='__main__':unittest.main()
