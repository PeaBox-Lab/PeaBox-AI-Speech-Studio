from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.batch import add_job, build_manifest, create_job, delete_job, duplicate_job, enqueue, list_queue, load_queue, queue_progress, read_events, recover_stale, reopen_cancelled, replace_job, request_cancel, request_worker_cancel, retry_failed, run_job, sync_to_project
import json
import streamlit as st
from pathlib import Path
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, PROVIDER_RATES
from peabox_voice_studio.services.files import build_render_zip, safe_filename, user_safe_error
from peabox_voice_studio.services.quality import prepare_text
from peabox_voice_studio.ui import empty_state, section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    section("Production jobs", "Validate provider readiness, create resumable jobs, and recover partial or failed work.")
    if not project:
        empty_state("No active project", "Open a project before creating production jobs.", "Open Project Workspace", "Projects")
    elif not project.blocks:
        empty_state("No script blocks", "Create script blocks before validating or running a batch.", "Open Script Editor", "Script Blocks")
    else:
        ready_providers = configured_providers()
        manifest = build_manifest(project, PROVIDER_RATES, ready_providers)
        totals = manifest["totals"]
        a, b, c, d = st.columns(4)
        a.metric("Enabled blocks", totals["enabled_blocks"]); b.metric("Characters", f"{totals['characters']:,}"); c.metric("Est. audio", f"{totals['estimated_minutes']:.1f} min"); d.metric("Est. cost", f"${totals['estimated_cost_usd']:.4f}")
        st.dataframe(manifest["blocks"], use_container_width=True, hide_index=True)
        validation = manifest["validation"]
        if validation["ready"]: st.success(f"Batch validation passed with {validation['warnings']} warning(s).")
        else: st.error(f"Batch is not ready: {validation['errors']} error(s), {validation['warnings']} warning(s).")
        if validation["issues"]: st.dataframe(validation["issues"], use_container_width=True, hide_index=True)
        st.download_button("Download render manifest", json.dumps(manifest, ensure_ascii=False, indent=2), f"{safe_filename(project.name)}_manifest.json", "application/json")
        if st.button("Create resumable job", type="primary", disabled=not validation["ready"]):
            try:
                job = create_job(project, PROVIDER_RATES, ready_providers, lambda text, provider: prepare_text(text, project, provider)); add_job(project, job); save_project(project); st.success("Batch job created")
            except Exception as exc: st.error("Job creation failed: " + user_safe_error(exc))
        jobs = project.settings.get("batch_jobs", [])
        if jobs:
            selected_job = st.selectbox("Saved batch jobs", jobs, format_func=lambda item: f"{item['created_at']} · {item['status']} · {item['id'][:8]}")
            summary = selected_job.get("summary", {})
            st.caption(f"Estimated ${summary.get('estimated_cost_usd', 0):.4f} · Recorded planning-rate usage ${summary.get('recorded_usage_cost_usd', 0):.4f}. Recorded usage cost is calculated from successful characters at the planning rate; it is not a provider invoice.")
            b1, b2, b3, b4, b5, b6 = st.columns(6)
            run_clicked = b1.button("Run/resume", disabled=selected_job.get("status") in {"completed", "cancelled"})
            retry_clicked = b2.button("Retry failed", disabled=not any(i["status"] == "failed" for i in selected_job["items"]))
            cancel_clicked = b3.button("Cancel queued", disabled=selected_job.get("status") in {"completed", "cancelled", "failed"})
            reopen_clicked = b4.button("Reopen cancelled", disabled=not any(i["status"] == "cancelled" for i in selected_job["items"]))
            duplicate_clicked = b5.button("Duplicate job")
            delete_clicked = b6.button("Delete job")
            if retry_clicked:
                retry_failed(selected_job); replace_job(project, selected_job); save_project(project); st.rerun()
            if cancel_clicked:
                request_cancel(selected_job); replace_job(project, selected_job); save_project(project); st.rerun()
            if reopen_clicked:
                reopen_cancelled(selected_job); replace_job(project, selected_job); save_project(project); st.rerun()
            if duplicate_clicked:
                add_job(project, duplicate_job(selected_job)); save_project(project); st.rerun()
            if delete_clicked:
                delete_job(project, selected_job["id"]); save_project(project); st.rerun()
            st.subheader("Local worker queue")
            eligible = all(item.get("provider") == "Kokoro local" for item in selected_job.get("items", []) if item.get("status") == "queued")
            worker_cols = st.columns(4)
            if worker_cols[0].button("Queue for local worker", disabled=not eligible or selected_job.get("status") in {"completed", "cancelled"}):
                try: enqueue(selected_job); st.success("Queued. Run worker_local.py in a separate terminal."); st.rerun()
                except Exception as exc: st.error("Queue failed: " + user_safe_error(exc))
            related = [item for item in list_queue() if item.get("job_id") == selected_job.get("id")]
            worker_item = related[0] if related else None
            if worker_cols[1].button("Recover stale leases"): recover_stale(); st.rerun()
            if worker_item and worker_cols[2].button("Sync worker progress"):
                sync_to_project(project, load_queue(worker_item["queue_id"])); save_project(project); st.rerun()
            if worker_item and worker_cols[3].button("Cancel worker job", disabled=worker_item.get("state") in {"completed", "cancelled"}): request_worker_cancel(worker_item["queue_id"]); st.rerun()
            if worker_item:
                fresh = load_queue(worker_item["queue_id"]); st.progress(queue_progress(fresh)); st.caption(f"Worker state: {fresh['state']} · Queue {fresh['queue_id'][:8]}")
                events = read_events(fresh["queue_id"], 25)
                if events: st.dataframe(list(reversed(events)), use_container_width=True, hide_index=True)
            if run_clicked:
                from peabox_voice_studio.providers.kokoro import generate as kokoro_generate
                from peabox_voice_studio.providers.cloud import generate_azure, generate_google, generate_polly
                renderers = {
                    "Kokoro local": lambda item, name: kokoro_generate(item["text"], item["voice"], KOKORO_LANGS.get(item["language"], "en-us"), item["speed"], name),
                }
                if "Azure Speech" in profiles: renderers["Azure Speech"] = lambda item, name: generate_azure(item["text"], profiles["Azure Speech"], item["voice"], item["speed"], name)
                if "Amazon Polly standard" in profiles: renderers["Amazon Polly standard"] = lambda item, name: generate_polly(item["text"], profiles["Amazon Polly standard"], item["voice"], "standard", name)
                if "Amazon Polly neural" in profiles: renderers["Amazon Polly neural"] = lambda item, name: generate_polly(item["text"], profiles["Amazon Polly neural"], item["voice"], "neural", name)
                if "Google Cloud TTS" in profiles: renderers["Google Cloud TTS"] = lambda item, name: generate_google(item["text"], profiles["Google Cloud TTS"], item["voice"], item["language"], name)
                with st.spinner("Running queued job items..."):
                    files, selected_job = run_job(selected_job, renderers)
                replace_job(project, selected_job); save_project(project); st.rerun()
            st.dataframe(selected_job["items"], use_container_width=True, hide_index=True)
            rendered_files = [Path(item["file"]) for item in selected_job["items"] if item["status"] == "rendered" and item.get("file") and Path(item["file"]).exists()]
            if rendered_files:
                job_manifest = {"project": project.name, "job": selected_job}
                st.download_button("Download job outputs", build_render_zip(rendered_files, job_manifest), f"{safe_filename(project.name)}_{selected_job['id'][:8]}_job.zip", "application/zip")
