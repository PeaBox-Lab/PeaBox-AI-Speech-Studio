import json
import tempfile
import unittest
from pathlib import Path
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.projects import ProjectStore, export_project
class ProviderSecurityTests(unittest.TestCase):
    def test_project_export_has_no_session_credentials(self):
        project = Project("Secure")
        project.settings["provider_readiness"] = ["Azure Speech"]
        text = export_project(project)
        self.assertNotIn("api_key", text.lower())
        self.assertNotIn("secret_key", text.lower())
        self.assertNotIn("service_account_json", text.lower())
    def test_job_metadata_remains_serializable(self):
        with tempfile.TemporaryDirectory() as folder:
            store = ProjectStore(Path(folder)); project = store.create("Jobs")
            project.settings["batch_jobs"] = [{"id": "1", "status": "queued", "items": []}]
            store.save(project)
            loaded = store.load(project.id)
            self.assertEqual(loaded.settings["batch_jobs"][0]["status"], "queued")
if __name__ == "__main__": unittest.main()