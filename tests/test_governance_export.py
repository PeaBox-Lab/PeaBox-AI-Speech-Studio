import json
import unittest
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.governance import add_comment, request_approval, update_project_governance
from peabox_voice_studio.services.projects import export_project
class GovernanceExportTests(unittest.TestCase):
    def test_governance_records_are_portable(self):
        project = Project("Demo")
        update_project_governance(project, "Owner", "Owner", ["Reviewer"], "Medium", "2026-12-01", True, True)
        add_comment(project, "Reviewer", "Review note")
        request_approval(project, "Owner", "Reviewer", "Final output")
        payload = json.loads(export_project(project))
        governance = payload["project"]["settings"]["governance"]
        self.assertEqual(governance["owner"], "Owner")
        self.assertEqual(len(governance["comments"]), 1)
        self.assertGreaterEqual(len(governance["audit_log"]), 3)
    def test_export_contains_no_authentication_claim(self):
        text = export_project(Project("Demo"))
        self.assertNotIn("authenticated_identity", text)
        self.assertNotIn("digital_signature", text)
if __name__ == "__main__": unittest.main()