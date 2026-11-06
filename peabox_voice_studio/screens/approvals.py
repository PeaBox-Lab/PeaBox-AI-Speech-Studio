from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.governance import approval_queue, decide_approval, governance, governance_summary, request_approval
import streamlit as st
from peabox_voice_studio.ui import callout, empty_state, kpi_card, section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    if not project:
        empty_state("No active project", "Open a project before requesting or deciding approvals.", "Open Project Workspace", "Projects")
    else:
        actor = st.text_input("Current local actor label", value=st.session_state.get("governance_actor", "Local User"), key="approval_actor_input")
        st.session_state.governance_actor = actor.strip() or "Local User"
        callout("Approval records are local attestations. They are not digital signatures and do not verify the identity or authority of the named reviewer.")
        data = governance(project)
        summary = governance_summary(project)
        cols = st.columns(4)
        with cols[0]: kpi_card("Pending", str(summary["pending_approvals"]), "Awaiting local decision")
        with cols[1]: kpi_card("Approved", str(summary["approved_requests"]), "Approved attestations")
        with cols[2]: kpi_card("Workflow", summary["status"], "Current project state")
        with cols[3]: kpi_card("Owner", summary["owner"] or "Unassigned", "Project accountability")
        section("Request approval", "Create a review gate for a defined project scope.")
        a1, a2 = st.columns(2)
        requester = a1.text_input("Requester", value=st.session_state.governance_actor)
        reviewer = a2.text_input("Reviewer label")
        scope = st.text_input("Approval scope", placeholder="Example: Final narration and timeline master")
        attestation = st.text_area("Requester attestation", placeholder="Describe what is ready and what evidence was reviewed", height=90)
        if st.button("Create approval request", type="primary", disabled=not (requester.strip() and reviewer.strip() and scope.strip())):
            request_approval(project, requester, reviewer, scope, attestation); save_project(project); st.rerun()
        approvals = data.get("approvals", [])
        if approvals:
            section("Approval queue", "Pending requests appear first; completed records remain as project history.")
            ordered = approval_queue(project)
            for item in ordered:
                with st.expander(f"{item.get('status')} · {item.get('scope')} · reviewer {item.get('reviewer')}", expanded=item.get("status") == "Pending"):
                    st.caption(f"Requested by {item.get('requester')} at {item.get('created_at')}")
                    if item.get("attestation"): st.write(item.get("attestation"))
                    if item.get("status") == "Pending":
                        decision_note = st.text_area("Decision note", key=f"approval_note_{item['id']}", height=70)
                        b1, b2, b3 = st.columns(3)
                        if b1.button("Approve", key=f"approve_{item['id']}"):
                            decide_approval(project, item["id"], st.session_state.governance_actor, "Approved", decision_note); save_project(project); st.rerun()
                        if b2.button("Reject", key=f"reject_{item['id']}"):
                            decide_approval(project, item["id"], st.session_state.governance_actor, "Rejected", decision_note); save_project(project); st.rerun()
                        if b3.button("Withdraw", key=f"withdraw_{item['id']}"):
                            decide_approval(project, item["id"], st.session_state.governance_actor, "Withdrawn", decision_note); save_project(project); st.rerun()
                    else:
                        st.write(f"Decision by {item.get('decided_by')} at {item.get('decision_at')}: {item.get('decision_note', '')}")
        else:
            st.info("No approval requests have been created.")
