import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WorkerUiTests(unittest.TestCase):
 def setUp(self):self.source=(ROOT/'peabox_voice_studio/screens/batch_production.py').read_text();self.cli=(ROOT/'worker_local.py').read_text()
 def test_worker_controls_exist(self):
  for label in ('Queue for local worker','Recover stale leases','Sync worker progress','Cancel worker job'):self.assertIn(label,self.source)
 def test_progress_and_events_are_visible(self):self.assertIn('st.progress(queue_progress(fresh))',self.source);self.assertIn('read_events',self.source)
 def test_cloud_queue_is_ineligible(self):self.assertIn('provider") == "Kokoro local"',self.source)
 def test_worker_cli_is_local_kokoro_only(self):self.assertIn("{'Kokoro local':local_renderer}",self.cli);self.assertNotIn('Azure',self.cli);self.assertNotIn('secret',self.cli.lower())
if __name__=='__main__':unittest.main()
