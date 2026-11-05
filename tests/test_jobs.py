import tempfile
import unittest
from pathlib import Path

from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.services.jobs import add_job, create_job, request_cancel, retry_failed, run_job


class JobTests(unittest.TestCase):
    def project(self):
        return Project("Demo", blocks=[
            ScriptBlock("Local", text="hello", provider="Kokoro local"),
            ScriptBlock("Cloud", text="world", provider="Azure Speech", language="en-US", voice="en-US-JennyNeural"),
        ])

    def test_create_job_snapshots_enabled_blocks(self):
        job = create_job(self.project(), {"Kokoro local": 0, "Azure Speech": 15}, {"Kokoro local", "Azure Speech"})
        self.assertEqual(job["status"], "queued")
        self.assertEqual(len(job["items"]), 2)
        self.assertNotIn("key", str(job))

    def test_run_job_and_record_cost(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            def renderer(item, name):
                path = root / f"{name}.wav"; path.write_bytes(item["text"].encode()); return path
            job = create_job(self.project(), {"Kokoro local": 0, "Azure Speech": 15}, {"Kokoro local", "Azure Speech"})
            files, job = run_job(job, {"Kokoro local": renderer, "Azure Speech": renderer})
            self.assertEqual(len(files), 2); self.assertEqual(job["status"], "completed")
            self.assertGreater(job["summary"]["actual_cost_usd"], 0)

    def test_failed_item_can_retry(self):
        job = create_job(self.project(), {"Kokoro local": 0, "Azure Speech": 15}, {"Kokoro local", "Azure Speech"})
        _, job = run_job(job, {})
        self.assertEqual(job["status"], "failed")
        retry_failed(job)
        self.assertTrue(all(item["status"] == "queued" for item in job["items"]))

    def test_cancel_marks_queued_items(self):
        job = create_job(self.project(), {"Kokoro local": 0, "Azure Speech": 15}, {"Kokoro local", "Azure Speech"})
        request_cancel(job)
        self.assertEqual(job["status"], "cancelled")
        self.assertTrue(all(item["status"] == "cancelled" for item in job["items"]))

    def test_add_job_limits_history(self):
        project = self.project()
        for index in range(25): add_job(project, {"id": str(index)}, keep=20)
        self.assertEqual(len(project.settings["batch_jobs"]), 20)


if __name__ == "__main__": unittest.main()
