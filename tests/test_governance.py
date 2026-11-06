import unittest
from peabox_voice_studio.models import Project
from peabox_voice_studio.services.governance import add_comment, add_decision, decide_approval, governance, governance_readiness, governance_summary, reopen_comment, request_approval, resolve_comment, supersede_decision, transition_status, update_project_governance
class GovernanceTests(unittest.TestCase):
    def test_default_governance_shape(self):
        data = governance(Project("Demo"))
        self.assertEqual(data["status"], "Draft")
        self.assertEqual(data["risk_level"], "Low")
        self.assertEqual(data["comments"], [])
    def test_update_metadata_and_audit(self):
        project = Project("Demo")
        data = update_project_governance(project, "Raj", "Owner", ["A", "A", " B "], "High", "2026-12-01", True, True)
        self.assertEqual(data["contributors"], ["A", "B"])
        self.assertEqual(data["risk_level"], "High")
        self.assertEqual(data["audit_log"][-1]["action"], "governance.updated")
    def test_comments_resolve_and_reopen(self):
        project = Project("Demo")
        comment = add_comment(project, "Reviewer", "Fix pronunciation", "Script Block", "block-1", "Blocking")
        self.assertEqual(governance_summary(project)["blocking_comments"], 1)
        self.assertTrue(resolve_comment(project, comment["id"], "Owner", "Fixed"))
        self.assertEqual(governance_summary(project)["open_comments"], 0)
        self.assertTrue(reopen_comment(project, comment["id"], "Reviewer"))
        self.assertEqual(governance_summary(project)["open_comments"], 1)
    def test_decision_and_supersession(self):
        project = Project("Demo")
        decision = add_decision(project, "Owner", "Voice", "Use Kokoro", "Local privacy", "Decided")
        self.assertTrue(supersede_decision(project, decision["id"], "Owner", "Cloud quality chosen"))
        self.assertEqual(governance(project)["decisions"][0]["status"], "Superseded")
    def test_approval_gate_controls_approved_transition(self):
        project = Project("Demo")
        transition_status(project, "In Review", "Owner")
        with self.assertRaises(ValueError): transition_status(project, "Approved", "Owner")
        approval = request_approval(project, "Owner", "Reviewer", "Final master", "Checked")
        with self.assertRaises(ValueError): transition_status(project, "Approved", "Owner")
        self.assertTrue(decide_approval(project, approval["id"], "Reviewer", "Approved", "Accepted"))
        self.assertEqual(transition_status(project, "Approved", "Owner"), "Approved")
        self.assertEqual(governance(project)["status"], "Approved")
    def test_invalid_transition_is_rejected(self):
        with self.assertRaises(ValueError): transition_status(Project("Demo"), "Published", "Owner")
    def test_readiness_detects_blocking_comment(self):
        project = Project("Demo")
        add_comment(project, "Reviewer", "Cannot publish", priority="Blocking")
        readiness = governance_readiness(project)
        self.assertFalse(readiness["ready"])
        self.assertEqual(readiness["errors"], 1)
    def test_approval_decisions_are_audited(self):
        project = Project("Demo")
        approval = request_approval(project, "A", "B", "Scope")
        decide_approval(project, approval["id"], "B", "Rejected", "Needs work")
        actions = [item["action"] for item in governance(project)["audit_log"]]
        self.assertEqual(actions, ["approval.requested", "approval.rejected"])
if __name__ == "__main__": unittest.main()
