from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.governance import ALLOWED_TRANSITIONS, RISK_LEVELS, WORKFLOW_STATES, add_comment, add_decision, governance, governance_readiness, governance_summary, reopen_comment, resolve_comment, supersede_decision, transition_status, update_project_governance
import json
import streamlit as st
from peabox_voice_studio.services.files import user_safe_error
from peabox_voice_studio.ui import callout, empty_state, kpi_card, section, status_badge

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    if not project:
        empty_state("No active project", "Open a project before managing ownership, reviews, and decisions.", "Open Project Workspace", "Projects")
    else:
        actor = st.text_input("Current local actor label", value=st.session_state.get("governance_actor", "Local User"), key="governance_actor_input")
        st.session_state.governance_actor = actor.strip() or "Local User"
        callout("Actor and reviewer names are local labels, not authenticated identities. Enterprise authentication and permissions remain a future architecture stage.")
        data = governance(project)
        summary = governance_summary(project)
        readiness = governance_readiness(project)
        cols = st.columns(5)
        with cols[0]: kpi_card("Workflow", summary["status"], f"Risk: {summary['risk_level']}")
        with cols[1]: kpi_card("Open comments", str(summary["open_comments"]), f"{summary['blocking_comments']} blocking")
        with cols[2]: kpi_card("Pending approvals", str(summary["pending_approvals"]), f"{summary['approved_requests']} approved")
        with cols[3]: kpi_card("Decisions", str(summary["decisions"]), "Recorded project decisions")
        with cols[4]: kpi_card("Audit entries", str(summary["audit_entries"]), "Append-only action history")
        if readiness["issues"]:
            st.dataframe(readiness["issues"], use_container_width=True, hide_index=True)
        tabs = st.tabs(["Project governance", "Review comments", "Decisions", "Audit log"])
        with tabs[0]:
            section("Ownership and review policy", "These values travel with the portable project and timeline bundle.")
            owner = st.text_input("Project owner", value=data.get("owner", ""))
            contributors_text = st.text_area("Contributors, one per line", value="\n".join(data.get("contributors", [])), height=110)
            g1, g2 = st.columns(2)
            risk = g1.selectbox("Risk level", RISK_LEVELS, index=RISK_LEVELS.index(data.get("risk_level", "Low")))
            due_date = g2.text_input("Target date", value=data.get("due_date", ""), placeholder="YYYY-MM-DD or local planning date")
            r1, r2 = st.columns(2)
            review_required = r1.checkbox("Review required", value=data.get("review_required", True))
            approval_required = r2.checkbox("Approval required", value=data.get("approval_required", True))
            if st.button("Save governance settings", type="primary"):
                update_project_governance(project, st.session_state.governance_actor, owner, contributors_text.splitlines(), risk, due_date, review_required, approval_required); save_project(project); st.success("Governance settings saved")
            section("Workflow status", "Transitions are controlled and recorded in the audit log.")
            current = data.get("status", "Draft")
            allowed = sorted(ALLOWED_TRANSITIONS.get(current, set()), key=WORKFLOW_STATES.index)
            st.markdown(f"Current status: {status_badge(current, 'good' if current in {'Approved','Published'} else 'warn' if current in {'In Review','Changes Requested'} else 'neutral')}", unsafe_allow_html=True)
            if allowed:
                target_status = st.selectbox("Move to", allowed)
                transition_note = st.text_input("Transition note")
                if st.button("Apply workflow transition"):
                    try:
                        transition_status(project, target_status, st.session_state.governance_actor, transition_note); save_project(project); st.rerun()
                    except Exception as exc: st.error("Transition blocked: " + user_safe_error(exc))
        with tabs[1]:
            section("Review thread", "Comments are retained; they can be resolved or reopened rather than deleted.")
            c1, c2 = st.columns(2)
            comment_author = c1.text_input("Comment author", value=st.session_state.governance_actor, key="comment_author")
            priority = c2.selectbox("Priority", ["Low", "Normal", "High", "Blocking"], index=1)
            target_type = st.selectbox("Comment target", ["Project", "Script Block", "Timeline Clip", "Batch Job", "Transcript", "Other"])
            target_id = st.text_input("Target reference", placeholder="Optional block, clip, job, or transcript ID")
            comment_body = st.text_area("Review comment", height=100)
            if st.button("Add review comment", disabled=not (comment_author.strip() and comment_body.strip())):
                add_comment(project, comment_author, comment_body, target_type, target_id, priority); save_project(project); st.rerun()
            comments = data.get("comments", [])
            show_resolved = st.checkbox("Show resolved comments")
            visible_comments = [item for item in comments if show_resolved or item.get("status") == "Open"]
            for item in reversed(visible_comments):
                with st.expander(f"{item.get('priority')} · {item.get('target_type')} · {item.get('author')} · {item.get('status')}"):
                    st.write(item.get("body"))
                    st.caption(f"Created {item.get('created_at')} · Reference {item.get('target_id') or 'Project'}")
                    if item.get("status") == "Open":
                        resolution = st.text_input("Resolution note", key=f"resolution_{item['id']}")
                        if st.button("Resolve comment", key=f"resolve_{item['id']}"):
                            resolve_comment(project, item["id"], st.session_state.governance_actor, resolution); save_project(project); st.rerun()
                    elif st.button("Reopen comment", key=f"reopen_{item['id']}"):
                        reopen_comment(project, item["id"], st.session_state.governance_actor); save_project(project); st.rerun()
        with tabs[2]:
            section("Decision register", "Capture material choices and rationale; superseded decisions remain visible.")
            decision_title = st.text_input("Decision title")
            decision_outcome = st.text_area("Decision or proposed outcome", height=90)
            decision_rationale = st.text_area("Rationale", height=90)
            decision_status = st.selectbox("Decision status", ["Proposed", "Decided"])
            if st.button("Record decision", disabled=not (decision_title.strip() and decision_outcome.strip())):
                add_decision(project, st.session_state.governance_actor, decision_title, decision_outcome, decision_rationale, decision_status); save_project(project); st.rerun()
            decisions = data.get("decisions", [])
            if decisions:
                st.dataframe(decisions, use_container_width=True, hide_index=True)
                active_decisions = [item for item in decisions if item.get("status") != "Superseded"]
                if active_decisions:
                    selected_decision = st.selectbox("Supersede decision", active_decisions, format_func=lambda item: item["title"])
                    supersede_reason = st.text_input("Supersede reason")
                    if st.button("Mark selected decision superseded"):
                        supersede_decision(project, selected_decision["id"], st.session_state.governance_actor, supersede_reason); save_project(project); st.rerun()
        with tabs[3]:
            section("Audit log", "Entries are append-only through the application workflow and included in project exports.")
            audit = list(reversed(data.get("audit_log", [])))
            audit_query = st.text_input("Filter audit entries", placeholder="Actor, action, target, or detail")
            if audit_query:
                audit = [item for item in audit if audit_query.lower() in json.dumps(item, ensure_ascii=False).lower()]
            if audit: st.dataframe(audit, use_container_width=True, hide_index=True)
            else: st.info("No governance actions have been recorded.")
