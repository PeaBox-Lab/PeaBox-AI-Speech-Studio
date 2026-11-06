from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.services.commands import onboarding_status
from peabox_voice_studio.services.diagnostics import system_diagnostics
from peabox_voice_studio.services.governance import governance, governance_readiness, governance_summary
from peabox_voice_studio.services.preferences import resolve_projects, save_preferences
from peabox_voice_studio.services.timeline import list_clips, validate_timeline
from peabox_voice_studio.ui import callout, kpi_card, navigate_to, section, workflow_step

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    projects = store.list()
    diagnostics = system_diagnostics()
    ready_checks = sum(row["Status"] == "Ready" for row in diagnostics)
    total_checks = len(diagnostics)
    onboarding = onboarding_status(project, len(configured_providers()))
    if not ui_preferences.get("onboarding_dismissed", False) and onboarding["completed"] < onboarding["total"]:
        section("Getting started progress", f"{onboarding['completed']} of {onboarding['total']} setup steps complete")
        st.progress(onboarding["percent"] / 100)
        onboarding_columns = st.columns([4, 1])
        with onboarding_columns[0]:
            for step in onboarding["steps"]:
                marker = "✓" if step["complete"] else "○"
                st.markdown(f"**{marker} {step['label']}**")
        if onboarding_columns[1].button("Dismiss guide", use_container_width=True):
            ui_preferences["onboarding_dismissed"] = True; save_preferences(ui_preferences); st.rerun()
    if project:
        clips = list_clips(project)
        jobs = project.settings.get("batch_jobs", [])
        transcript_sessions = project.settings.get("transcript_sessions", [])
        comparison_history = project.settings.get("comparison_history", [])
        gov_summary = governance_summary(project)
        section("Quick actions", "Jump directly to the next production task for the active project.")
        quick_actions = [("Edit script", "Script Blocks"), ("Generate speech", "Create Speech"), ("Run batch", "Batch Production"), ("Open timeline", "Timeline Studio"), ("Review governance", "Governance")]
        quick_columns = st.columns(5)
        for index, (label, target) in enumerate(quick_actions):
            if quick_columns[index].button(label, key=f"dashboard_quick_{target}", use_container_width=True):
                navigate_to(target); st.rerun()
        cols = st.columns(5)
        with cols[0]: kpi_card("Workflow", gov_summary["status"], f"Risk: {gov_summary['risk_level']}")
        with cols[1]: kpi_card("Script blocks", str(len(project.blocks)), "Structured production units")
        with cols[2]: kpi_card("Timeline clips", str(len(clips)), "Durable WAV assets")
        with cols[3]: kpi_card("Open reviews", str(gov_summary["open_comments"]), f"{gov_summary['blocking_comments']} blocking")
        with cols[4]: kpi_card("Approvals", str(gov_summary["pending_approvals"]), "Pending local attestations")
        section("Production readiness", "Current project health across script, providers, timeline, and system dependencies.")
        validation = validate_timeline(project) if clips else {"valid": False, "errors": 0, "warnings": 0, "enabled_clips": 0}
        readiness_rows = [
            {"Area": "Project", "Status": "Ready", "Detail": f"{len(project.blocks)} blocks and {len(project.script):,} master-script characters"},
            {"Area": "Providers", "Status": "Ready" if configured_providers() else "Needs setup", "Detail": f"{len(configured_providers())} provider paths available"},
            {"Area": "Timeline", "Status": "Ready" if validation.get("valid") else "Needs review", "Detail": f"{validation.get('enabled_clips', 0)} enabled clips; {validation.get('errors', 0)} errors"},
            {"Area": "Governance", "Status": "Ready" if governance_readiness(project)["ready"] else "Needs review", "Detail": f"{gov_summary['open_comments']} open comments; {gov_summary['pending_approvals']} pending approvals"},
            {"Area": "System", "Status": f"{ready_checks}/{total_checks} ready", "Detail": "Open System Check for details"},
        ]
        st.dataframe(readiness_rows, use_container_width=True, hide_index=True)
        dashboard_detail = ui_preferences.get("dashboard_detail", "Standard")
        if dashboard_detail in {"Standard", "Detailed"}:
            section("Recommended workflow", "Use the grouped navigation to move from content preparation to production and review.")
            steps = st.columns(4)
            with steps[0]: workflow_step(1, "Prepare", "Build the master script, script blocks, pronunciation rules, and voice presets.")
            with steps[1]: workflow_step(2, "Generate", "Create a single render or validate and run a resumable batch job.")
            with steps[2]: workflow_step(3, "Assemble", "Review WAV quality, add clips to Timeline Studio, and build a production master.")
            with steps[3]: workflow_step(4, "Review", "Inspect activity, transcripts, comparisons, costs, and export history.")
        if dashboard_detail == "Detailed":
            section("Recent project activity")
            activity = []
            for item in project.render_history[:5]: activity.append({"Type": "Render", "When": item.get("created_at"), "Item": item.get("output"), "Status": item.get("provider")})
            for item in project.settings.get("timeline_exports", [])[:5]: activity.append({"Type": "Timeline export", "When": item.get("created_at"), "Item": item.get("output"), "Status": "Completed"})
            for item in jobs[:5]: activity.append({"Type": "Batch job", "When": item.get("updated_at", item.get("created_at")), "Item": item.get("id", "")[:8], "Status": item.get("status")})
            for item in governance(project)["audit_log"][-5:]: activity.append({"Type": "Governance", "When": item.get("timestamp"), "Item": item.get("action"), "Status": item.get("actor")})
            activity = sorted(activity, key=lambda row: row.get("When") or "", reverse=True)[:10]
            if activity: st.dataframe(activity, use_container_width=True, hide_index=True)
            else: callout("No production activity has been recorded yet. Start with Script Editor or Speech Generator.")
    else:
        cols = st.columns(3)
        with cols[0]: kpi_card("Saved projects", str(len(projects)), "Available local workspaces")
        with cols[1]: kpi_card("System readiness", f"{ready_checks}/{total_checks}", "Core diagnostic checks ready")
        with cols[2]: kpi_card("Active project", "None", "Open or create a project to begin")
        section("Getting started", "PeaBox separates project management, production, audio quality, transcription, and administration into dedicated screens.")
        callout("Open Project Workspace from the Overview area to create a new project or import an existing project or timeline bundle.")
        favorite_projects = resolve_projects(projects, ui_preferences.get("favorite_project_ids", []))
        recent_projects = resolve_projects(projects, ui_preferences.get("recent_project_ids", []))
        if favorite_projects or recent_projects:
            section("Quick project access", "Favorites are shown first, followed by recently opened projects.")
            access_projects = favorite_projects + [item for item in recent_projects if item.id not in {fav.id for fav in favorite_projects}]
            for item in access_projects[:6]:
                cols_access = st.columns([4, 1])
                cols_access[0].markdown(f"**{'★ ' if item.id in ui_preferences.get('favorite_project_ids', []) else ''}{item.name}**  \nUpdated {item.updated_at}")
                if cols_access[1].button("Open", key=f"dashboard_open_{item.id}", use_container_width=True):
                    open_project(item.id); st.rerun()
        c1, c2, c3 = st.columns(3)
        with c1: workflow_step(1, "Create a project", "Name the production and write or import its master script.")
        with c2: workflow_step(2, "Configure production", "Prepare script blocks, providers, voices, pronunciation, and presets.")
        with c3: workflow_step(3, "Generate and assemble", "Render audio, validate quality, and create a timeline master.")
