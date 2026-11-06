from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.services.governance import governance, governance_summary
from peabox_voice_studio.ui import section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    if not project:
        st.info("Open a project to review activity and history.")
    else:
        section("Project activity ledger", "Review outputs and production records without changing the underlying project data.")
        tabs = st.tabs(["Renders", "Batch jobs", "Timeline exports", "Comparisons", "Transcripts", "Governance"])
        with tabs[0]:
            if project.render_history: st.dataframe(project.render_history, use_container_width=True, hide_index=True)
            else: st.info("No individual renders have been recorded.")
        with tabs[1]:
            jobs = project.settings.get("batch_jobs", [])
            if jobs:
                rows = [{"Created": job.get("created_at"), "Updated": job.get("updated_at"), "Job": job.get("id", "")[:8], "Status": job.get("status"), "Items": len(job.get("items", [])), "Estimated cost": job.get("summary", {}).get("estimated_cost_usd", 0), "Recorded planning-rate usage": job.get("summary", {}).get("recorded_usage_cost_usd", 0)} for job in jobs]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else: st.info("No batch jobs have been recorded.")
        with tabs[2]:
            exports = project.settings.get("timeline_exports", [])
            if exports:
                rows = [{"Created": item.get("created_at"), "Output": item.get("output"), "Duration": item.get("manifest", {}).get("mix", {}).get("duration_seconds"), "Clips": len(item.get("manifest", {}).get("clips", []))} for item in exports]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else: st.info("No timeline exports have been recorded.")
        with tabs[3]:
            comparisons = project.settings.get("comparison_history", [])
            if comparisons: st.dataframe(comparisons, use_container_width=True, hide_index=True)
            else: st.info("No A/B comparisons have been recorded.")
        with tabs[4]:
            transcripts = project.settings.get("transcript_sessions", [])
            if transcripts:
                rows = [{"Name": item.get("name"), "Source": item.get("source_name"), "Language": item.get("language"), "Created": item.get("created_at"), "Updated": item.get("updated_at"), "Segments": len(item.get("segments", []))} for item in transcripts]
                st.dataframe(rows, use_container_width=True, hide_index=True)
            else: st.info("No transcript sessions have been saved.")
        with tabs[5]:
            gov = governance(project)
            st.subheader("Review and approval summary")
            st.json(governance_summary(project))
            st.subheader("Recent governance audit")
            if gov.get("audit_log"): st.dataframe(list(reversed(gov["audit_log"][-100:])), use_container_width=True, hide_index=True)
            else: st.info("No governance actions have been recorded.")
