import json
from pathlib import Path
import streamlit as st

from peabox_voice_studio.config import APP_NAME, MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, MAX_UPLOAD_BYTES, OUTPUTS_DIR, VERSION
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES, PROVIDER_RATES
from peabox_voice_studio.services.audio import inspect_wav, normalize_wav, save_processed_wav, trim_silence_wav
from peabox_voice_studio.services.batch import build_manifest
from peabox_voice_studio.services.commands import onboarding_status, record_command, resolve_commands, search_commands
from peabox_voice_studio.services.comparisons import create_comparison_record, delete_comparison, set_comparison_preference
from peabox_voice_studio.services.bundles import export_timeline_bundle, import_timeline_bundle
from peabox_voice_studio.services.files import atomic_write_bytes, build_render_zip, safe_filename, user_safe_error
from peabox_voice_studio.services.governance import ALLOWED_TRANSITIONS, APPROVAL_STATES, RISK_LEVELS, WORKFLOW_STATES, add_comment, add_decision, decide_approval, governance, governance_readiness, governance_summary, reopen_comment, request_approval, resolve_comment, supersede_decision, transition_status, update_project_governance
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.catalogs import capability_rows, catalog_facets, filter_voices
from peabox_voice_studio.services.jobs import add_job, create_job, delete_job, duplicate_job, reopen_cancelled, replace_job, request_cancel, retry_failed, run_job
from peabox_voice_studio.services.preferences import load_preferences, mark_project_opened, resolve_projects, save_preferences, toggle_favorite
from peabox_voice_studio.services.presets import apply_preset, create_preset, delete_preset, list_presets
from peabox_voice_studio.services.projects import ProjectStore, export_project, move_block, set_all_blocks_enabled, split_script_into_blocks
from peabox_voice_studio.services.diagnostics import system_diagnostics, transcription_readiness
from peabox_voice_studio.services.quality import add_pronunciation, delete_pronunciation, insert_pause, list_pronunciations, prepare_text, pronunciation_conflicts, pronunciation_preview, validate_pause_markers
from peabox_voice_studio.services.timeline import acknowledge_clip_source, add_clip, arrange_sequential, cleanup_invalid_clips, clip_status, duplicate_timeline, list_clips, mix_timeline, move_clip, refresh_clip, relink_clip, remove_clip, timeline_manifest, validate_timeline
from peabox_voice_studio.services.transcripts import delete_transcript_session, export_transcript_bundle, filter_segments, normalize_segments, repair_segment_timing, save_transcript_session, update_transcript_session, validate_segments
from peabox_voice_studio.services.subtitles import to_srt, to_vtt
from peabox_voice_studio.ui import callout, empty_state, inject_corporate_theme, kpi_card, navigate_to, page_header, section, sidebar_navigation, status_badge, workflow_step

st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎙️", layout="wide", initial_sidebar_state="expanded")
ui_preferences = st.session_state.setdefault("ui_preferences", load_preferences())
inject_corporate_theme(ui_preferences)
store = ProjectStore()
profiles = st.session_state.setdefault("provider_profiles", {})
voice_catalogs = st.session_state.setdefault("voice_catalogs", {})
governance_actor = st.session_state.setdefault("governance_actor", "Local User")

def configured_providers() -> set[str]:
    return {"Kokoro local", *profiles.keys()}


def current_project() -> Project | None:
    return st.session_state.get("project")


def save_project(project: Project) -> None:
    store.save(project); st.session_state.project = project


def open_project(project_id: str) -> None:
    st.session_state.project = store.load(project_id)
    mark_project_opened(ui_preferences, project_id)
    save_preferences(ui_preferences)


def set_active_project(project: Project) -> None:
    st.session_state.project = project
    mark_project_opened(ui_preferences, project.id)
    save_preferences(ui_preferences)


def block_editor(project: Project, index: int, block: ScriptBlock) -> None:
    label = f"{index + 1:02}. {block.title} · {len(block.text):,} chars · {block.provider}"
    with st.expander(label, expanded=st.session_state.get("expand_block") == block.id):
        block.enabled = st.checkbox("Include in batch", block.enabled, key=f"enabled_{block.id}")
        block.title = st.text_input("Block title", block.title, key=f"title_{block.id}")
        block.text = st.text_area("Text", block.text, height=180, max_chars=MAX_BLOCK_CHARS, key=f"text_{block.id}")
        a, b, c, d = st.columns(4)
        providers = ["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"]
        block.provider = a.selectbox("Provider", providers, index=providers.index(block.provider) if block.provider in providers else 0, key=f"provider_{block.id}")
        if block.provider == "Kokoro local":
            block.language = b.selectbox("Language", list(KOKORO_VOICES), index=list(KOKORO_VOICES).index(block.language) if block.language in KOKORO_VOICES else 0, key=f"lang_{block.id}")
            voices = KOKORO_VOICES[block.language]
            block.voice = c.selectbox("Voice", voices, index=voices.index(block.voice) if block.voice in voices else 0, key=f"voice_{block.id}")
        else:
            provider_voices = voice_catalogs.get(block.provider, [])
            if provider_voices:
                language_options = sorted({item["language"] for item in provider_voices if item.get("language")})
                current_language = block.language if block.language in language_options else (language_options[0] if language_options else "")
                block.language = b.selectbox("Language code", language_options or [current_language], index=(language_options or [current_language]).index(current_language), key=f"lang_{block.id}")
                matching = [item for item in provider_voices if not block.language or item.get("language") == block.language]
                voice_ids = [item["id"] for item in matching]
                current_voice = block.voice if block.voice in voice_ids else (voice_ids[0] if voice_ids else block.voice)
                block.voice = c.selectbox("Provider voice", voice_ids or [current_voice], index=(voice_ids or [current_voice]).index(current_voice), key=f"voice_{block.id}")
            else:
                default_language = block.language if block.language not in KOKORO_VOICES else "en-US"
                block.language = b.text_input("Language code", default_language, key=f"lang_{block.id}")
                default_voice = block.voice if block.voice not in sum(KOKORO_VOICES.values(), []) else ""
                block.voice = c.text_input("Provider voice ID", default_voice, key=f"voice_{block.id}")
        block.speed = d.slider("Speed", 0.6, 1.6, float(block.speed), 0.05, key=f"speed_{block.id}")
        block.notes = st.text_input("Direction notes", block.notes, placeholder="Optional pacing, pronunciation, or performance note", key=f"notes_{block.id}")
        pause_seconds = st.slider("Pause marker seconds", 0.1, 5.0, 1.0, 0.1, key=f"pause_seconds_{block.id}")
        if st.button("Append pause marker", key=f"append_pause_{block.id}"):
            block.text = insert_pause(block.text, pause_seconds); save_project(project); st.rerun()
        pause_issues = validate_pause_markers(block.text)
        if pause_issues:
            st.error("; ".join(pause_issues))
        with st.expander("Processed text preview"):
            st.code(prepare_text(block.text, project, block.provider))
        presets = list_presets(project)
        if presets:
            preset = st.selectbox("Apply project preset", [None] + presets, format_func=lambda item: "Choose a preset" if item is None else item["name"], key=f"preset_{block.id}")
            if st.button("Apply selected preset", key=f"apply_preset_{block.id}", disabled=preset is None):
                apply_preset(block, preset); save_project(project); st.rerun()
        preset_name = st.text_input("Save current settings as preset", key=f"preset_name_{block.id}")
        if st.button("Save preset", key=f"save_preset_{block.id}", disabled=not preset_name.strip()):
            create_preset(project, preset_name, block); save_project(project); st.success("Preset saved")
        u, dn, dup, delete = st.columns(4)
        if u.button("Move up", key=f"up_{block.id}", disabled=index == 0):
            move_block(project.blocks, index, -1); save_project(project); st.rerun()
        if dn.button("Move down", key=f"down_{block.id}", disabled=index == len(project.blocks) - 1):
            move_block(project.blocks, index, 1); save_project(project); st.rerun()
        if dup.button("Duplicate", key=f"dup_{block.id}"):
            project.blocks.insert(index + 1, ScriptBlock(title=f"{block.title} copy", text=block.text, provider=block.provider, language=block.language, voice=block.voice, speed=block.speed, notes=block.notes)); save_project(project); st.rerun()
        if delete.button("Delete", key=f"delete_{block.id}"):
            project.blocks.pop(index); save_project(project); st.rerun()


project = current_project()
page = sidebar_navigation(VERSION, project, ui_preferences)
page_header(page, VERSION, project)

if page == "Dashboard":
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

elif page == "Command Center":
    section("Search workspace commands", "Commands navigate to safe screens and never execute destructive project actions.")
    command_query = st.text_input("Search screens and workflows", placeholder="Try: transcript, batch, provider, approval, timeline")
    command_results = search_commands(command_query, project is not None)
    if command_results:
        selected_command = st.selectbox("Command results", command_results, format_func=lambda item: f"{item['group']} · {item['label']}{'' if item['available'] else ' · project required'}")
        st.caption(f"Keywords: {selected_command['keywords']}")
        if st.button("Open selected command", type="primary", disabled=not selected_command["available"]):
            record_command(ui_preferences, selected_command["id"]); save_preferences(ui_preferences); navigate_to(selected_command["page"]); st.rerun()
        if not selected_command["available"]:
            empty_state("Active project required", "Open or create a project before using this command.", "Open Project Workspace", "Projects")
    else:
        empty_state("No command found", "Try a broader term such as audio, script, review, provider, or history.")
    recent_commands = resolve_commands(ui_preferences.get("recent_command_ids", []))
    if recent_commands:
        section("Recent commands", "Reopen frequently used workflows without searching again.")
        recent_columns = st.columns(min(4, len(recent_commands)))
        for index, command in enumerate(recent_commands[:8]):
            column = recent_columns[index % len(recent_columns)]
            if column.button(command["label"], key=f"recent_command_{command['id']}", use_container_width=True):
                record_command(ui_preferences, command["id"]); save_preferences(ui_preferences); navigate_to(command["page"]); st.rerun()

elif page == "Preferences":
    section("Personal workspace preferences", "These preferences are stored locally on this device and are not included in project exports.")
    area_options = ["Overview", "Production", "Audio & Quality", "Administration", "Support"]
    default_area = st.selectbox("Default workspace area", area_options, index=area_options.index(ui_preferences.get("default_area", "Overview")) if ui_preferences.get("default_area") in area_options else 0)
    dashboard_detail = st.radio("Dashboard detail", ["Compact", "Standard", "Detailed"], index=["Compact", "Standard", "Detailed"].index(ui_preferences.get("dashboard_detail", "Standard")), horizontal=True)
    p1, p2 = st.columns(2)
    compact_navigation = p1.checkbox("Compact sidebar navigation", value=ui_preferences.get("compact_navigation", False))
    reduced_motion = p2.checkbox("Reduce interface motion", value=ui_preferences.get("reduced_motion", False))
    if st.button("Save interface preferences", type="primary"):
        ui_preferences.update({"default_area": default_area, "dashboard_detail": dashboard_detail, "compact_navigation": compact_navigation, "reduced_motion": reduced_motion})
        save_preferences(ui_preferences)
        st.success("Preferences saved. Layout preferences apply immediately after refresh.")
    section("Local preference data", "Favorites and recent-project history can be cleared without modifying project files.")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Clear recent projects", disabled=not ui_preferences.get("recent_project_ids")):
        ui_preferences["recent_project_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c2.button("Clear favorites", disabled=not ui_preferences.get("favorite_project_ids")):
        ui_preferences["favorite_project_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c3.button("Clear recent commands", disabled=not ui_preferences.get("recent_command_ids")):
        ui_preferences["recent_command_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c4.button("Show onboarding again", disabled=not ui_preferences.get("onboarding_dismissed", False)):
        ui_preferences["onboarding_dismissed"] = False; save_preferences(ui_preferences); st.rerun()
    st.json({"default_area": ui_preferences.get("default_area"), "dashboard_detail": ui_preferences.get("dashboard_detail"), "compact_navigation": ui_preferences.get("compact_navigation"), "reduced_motion": ui_preferences.get("reduced_motion"), "recent_projects": len(ui_preferences.get("recent_project_ids", [])), "favorites": len(ui_preferences.get("favorite_project_ids", [])), "recent_commands": len(ui_preferences.get("recent_command_ids", [])), "onboarding_dismissed": ui_preferences.get("onboarding_dismissed", False)})

elif page == "Projects":
    section("Project portfolio", "Create, open, import, and maintain the production workspace and master script.")
    left, right = st.columns([1, 2])
    with left:
        name = st.text_input("New project name")
        description = st.text_area("Description", height=90)
        if st.button("Create and open", type="primary", disabled=not name.strip()):
            set_active_project(store.create(name, description)); st.rerun()
        projects = store.list()
        selected = st.selectbox("Saved projects", projects, format_func=lambda p: f"{p.name} · {p.updated_at[:10]}") if projects else None
        p_open, p_fav = st.columns(2)
        if p_open.button("Open selected", disabled=selected is None, use_container_width=True): open_project(selected.id); st.rerun()
        is_favorite = bool(selected and selected.id in ui_preferences.get("favorite_project_ids", []))
        if p_fav.button("Remove favorite" if is_favorite else "Add favorite", disabled=selected is None, use_container_width=True):
            toggle_favorite(ui_preferences, selected.id); save_preferences(ui_preferences); st.rerun()
        favorite_projects = resolve_projects(projects, ui_preferences.get("favorite_project_ids", []))
        recent_projects = resolve_projects(projects, ui_preferences.get("recent_project_ids", []))
        if favorite_projects:
            st.caption("Favorites: " + " · ".join(item.name for item in favorite_projects[:5]))
        if recent_projects:
            st.caption("Recent: " + " · ".join(item.name for item in recent_projects[:5]))
        st.divider()
        st.subheader("Import project")
        imported_file = st.file_uploader("PeaBox project JSON", type="json", key="project_import")
        if st.button("Import and open", disabled=imported_file is None):
            try:
                set_active_project(store.import_project(imported_file.getvalue()))
                st.success("Project imported with a new identity")
                st.rerun()
            except Exception as exc:
                st.error("Import failed: " + user_safe_error(exc))
        st.subheader("Import timeline bundle")
        bundle_file = st.file_uploader("PeaBox timeline bundle ZIP", type="zip", key="timeline_bundle_import")
        if st.button("Import bundle and open", disabled=bundle_file is None):
            try:
                imported_project = import_timeline_bundle(bundle_file.getvalue(), OUTPUTS_DIR)
                set_active_project(store.save(imported_project))
                st.success("Timeline bundle imported with local asset copies")
                st.rerun()
            except Exception as exc:
                st.error("Bundle import failed: " + user_safe_error(exc))
    with right:
        project = current_project()
        if not project: st.info("Create or open a project to begin.")
        else:
            project.name = st.text_input("Project name", project.name)
            project.description = st.text_area("Description", project.description, height=90)
            project.script = st.text_area("Master Script", project.script, height=330, max_chars=MAX_SCRIPT_CHARS)
            words = len(project.script.split())
            a, b, c, d = st.columns(4)
            a.metric("Characters", f"{len(project.script):,}"); b.metric("Words", f"{words:,}"); c.metric("Est. audio", f"{words/150:.1f} min"); d.metric("Blocks", len(project.blocks))
            x, y, z, q = st.columns(4)
            if x.button("Save project", type="primary"): save_project(project); st.success("Project saved")
            y.download_button("Export script", project.script, f"{safe_filename(project.name)}.txt")
            q.download_button("Export project JSON", export_project(project), f"{safe_filename(project.name)}_project.json", "application/json")
            block_import_mode = st.radio("Master Script block import", ["Append", "Replace existing"], horizontal=True)
            if z.button("Create blocks from paragraphs", disabled=not project.script.strip()):
                new_blocks = split_script_into_blocks(project.script)
                project.blocks = new_blocks if block_import_mode == "Replace existing" else project.blocks + new_blocks
                save_project(project); st.success(f"{'Created' if block_import_mode == 'Replace existing' else 'Added'} {len(new_blocks)} blocks")
            with st.expander("Delete project"):
                confirm = st.checkbox("I understand this permanently deletes the project")
                if st.button("Delete permanently", disabled=not confirm): store.delete(project.id); st.session_state.pop("project", None); st.rerun()


elif page == "Governance":
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

elif page == "Approvals":
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
            ordered = sorted(approvals, key=lambda item: (item.get("status") != "Pending", item.get("created_at", "")))
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

elif page == "System Check":
    diagnostics = system_diagnostics()
    st.dataframe(diagnostics, use_container_width=True, hide_index=True)
    blocking = [row for row in diagnostics if row["Status"] in {"Unsupported", "Missing", "Not writable"}]
    if blocking:
        st.warning("Resolve the listed setup items before using affected features. WAV transcription can work without FFmpeg; compressed media cannot.")
    else:
        st.success("Core local requirements are ready.")
    st.subheader("Quick guidance")
    st.markdown("""
- **Python:** Use 64-bit Python 3.10, 3.11, or 3.12.
- **FFmpeg:** Required for MP3, M4A, OGG, MP4, MOV, MKV, and WebM transcription.
- **Kokoro files:** Download automatically during the first local generation.
- **Storage:** Projects and generated audio must remain writable.
""")

elif page == "Provider Setup":
    st.warning("Credentials are held only in this Streamlit session. They are not saved in projects, exports, manifests, or logs.")
    tabs = st.tabs(["Azure Speech", "Amazon Polly", "Google Cloud TTS"])
    with tabs[0]:
        azure_key = st.text_input("Azure API key", type="password", key="azure_key")
        azure_region = st.text_input("Azure region", profiles.get("Azure Speech", {}).get("region", "centralindia"), key="azure_region")
        if st.button("Use Azure for this session"):
            if azure_key.strip() and azure_region.strip():
                profiles["Azure Speech"] = {"key": azure_key.strip(), "region": azure_region.strip()}; st.success("Azure session profile is ready")
            else: st.error("API key and region are required")
        if st.button("Discover Azure voices", disabled="Azure Speech" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_azure_voices
                with st.spinner("Discovering Azure voices..."): voice_catalogs["Azure Speech"] = discover_azure_voices(profiles["Azure Speech"])
                st.success(f"Cached {len(voice_catalogs['Azure Speech'])} Azure voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Azure session profile"):
            profiles.pop("Azure Speech", None); voice_catalogs.pop("Azure Speech", None); st.rerun()
    with tabs[1]:
        aws_access = st.text_input("AWS access key ID", type="password", key="aws_access")
        aws_secret = st.text_input("AWS secret access key", type="password", key="aws_secret")
        aws_token = st.text_input("AWS session token, optional", type="password", key="aws_token")
        aws_region = st.text_input("AWS region", profiles.get("Amazon Polly standard", {}).get("region", "ap-south-1"), key="aws_region")
        if st.button("Use Polly for this session"):
            if aws_access.strip() and aws_secret.strip() and aws_region.strip():
                profile = {"access_key": aws_access.strip(), "secret_key": aws_secret.strip(), "session_token": aws_token.strip(), "region": aws_region.strip()}
                profiles["Amazon Polly standard"] = profile; profiles["Amazon Polly neural"] = profile
                st.success("Polly session profiles are ready")
            else: st.error("Access key, secret key, and region are required")
        polly_engine = st.radio("Polly catalog engine", ["standard", "neural"], horizontal=True)
        if st.button("Discover Polly voices", disabled="Amazon Polly standard" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_polly_voices
                provider_name = "Amazon Polly neural" if polly_engine == "neural" else "Amazon Polly standard"
                with st.spinner("Discovering Polly voices..."): voice_catalogs[provider_name] = discover_polly_voices(profiles[provider_name], polly_engine)
                st.success(f"Cached {len(voice_catalogs[provider_name])} {provider_name} voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Polly session profiles"):
            profiles.pop("Amazon Polly standard", None); profiles.pop("Amazon Polly neural", None); voice_catalogs.pop("Amazon Polly standard", None); voice_catalogs.pop("Amazon Polly neural", None); st.rerun()
    with tabs[2]:
        google_file = st.file_uploader("Google service-account JSON", type="json", key="google_profile")
        if st.button("Use Google for this session", disabled=google_file is None):
            try:
                json.loads(google_file.getvalue().decode("utf-8"))
                profiles["Google Cloud TTS"] = {"service_account_json": google_file.getvalue().decode("utf-8")}
                st.success("Google session profile is ready")
            except Exception: st.error("The uploaded file is not valid JSON")
        google_language = st.text_input("Optional Google language filter", value="", key="google_language_filter")
        if st.button("Discover Google voices", disabled="Google Cloud TTS" not in profiles):
            try:
                from peabox_voice_studio.providers.cloud import discover_google_voices
                with st.spinner("Discovering Google voices..."): voice_catalogs["Google Cloud TTS"] = discover_google_voices(profiles["Google Cloud TTS"], google_language)
                st.success(f"Cached {len(voice_catalogs['Google Cloud TTS'])} Google voices for this session")
            except Exception as exc: st.error("Voice discovery failed: " + user_safe_error(exc))
        if st.button("Clear Google session profile"):
            profiles.pop("Google Cloud TTS", None); voice_catalogs.pop("Google Cloud TTS", None); st.rerun()
    counts = {name: len(items) for name, items in voice_catalogs.items()}
    st.subheader("Provider capabilities and readiness")
    st.dataframe(capability_rows(configured_providers(), counts), use_container_width=True, hide_index=True)

elif page == "Voice Library":
    all_voices = [{"provider": "Kokoro local", "id": voice, "name": voice, "language": language, "gender": "", "styles": []} for language, voices in KOKORO_VOICES.items() for voice in voices]
    for items in voice_catalogs.values(): all_voices.extend(items)
    facets = catalog_facets(all_voices)
    a, b, c = st.columns(3)
    query = a.text_input("Search voices", placeholder="Name, ID, provider, or language")
    language_filter = b.selectbox("Language", ["All"] + facets["languages"])
    gender_filter = c.selectbox("Gender", ["All"] + facets["genders"])
    visible_voices = filter_voices(all_voices, query, language_filter, gender_filter)
    st.caption(f"Showing {len(visible_voices)} of {len(all_voices)} session voices. Cloud catalogs are cached only for this session.")
    st.dataframe(visible_voices, use_container_width=True, hide_index=True)
    if project:
        presets = list_presets(project)
        st.subheader("Project voice presets")
        if presets:
            st.dataframe(presets, use_container_width=True, hide_index=True)
            preset_to_delete = st.selectbox("Delete preset", presets, format_func=lambda item: item["name"])
            if st.button("Delete selected preset"):
                delete_preset(project, preset_to_delete["id"]); save_project(project); st.rerun()
        else: st.info("Save a preset from any script block to reuse its provider, voice, speed, and direction notes.")

elif page == "Quality Studio":
    if not project:
        st.info("Open a project to manage pronunciation and direction rules.")
    else:
        st.subheader("Project pronunciation dictionary")
        st.caption("Rules are applied in order before a job is created. They are stored with the project and contain no credentials.")
        a, b = st.columns(2)
        source_word = a.text_input("Written text", placeholder="Example: PeaBox")
        spoken_form = b.text_input("Spoken replacement", placeholder="Example: pea box")
        c, d = st.columns(2)
        case_sensitive = c.checkbox("Case-sensitive match")
        whole_word = d.checkbox("Whole-word match", value=True)
        if st.button("Add pronunciation rule", type="primary", disabled=not (source_word.strip() and spoken_form.strip())):
            try:
                add_pronunciation(project, source_word, spoken_form, case_sensitive, whole_word); save_project(project); st.rerun()
            except Exception as exc: st.error("Could not add rule: " + user_safe_error(exc))
        entries = list_pronunciations(project)
        if entries:
            st.dataframe(entries, use_container_width=True, hide_index=True)
            conflicts = pronunciation_conflicts(entries)
            if conflicts:
                st.warning("Pronunciation rules contain duplicates or overlaps; review rule order.")
                st.dataframe(conflicts, use_container_width=True, hide_index=True)
            selected_rule = st.selectbox("Delete pronunciation rule", entries, format_func=lambda item: f"{item['source']} → {item['replacement']}")
            if st.button("Delete selected rule"):
                delete_pronunciation(project, selected_rule["id"]); save_project(project); st.rerun()
        else:
            st.info("No pronunciation rules have been added.")
        st.subheader("Text preparation preview")
        preview_provider = st.selectbox("Preview provider", ["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"])
        preview_text = st.text_area("Preview text", project.script, height=180)
        pause_seconds = st.slider("Pause duration", 0.1, 5.0, 1.0, 0.1, key="quality_pause")
        if st.button("Append pause to preview"):
            st.session_state.quality_preview_text = insert_pause(preview_text, pause_seconds); st.rerun()
        preview_text = st.session_state.get("quality_preview_text", preview_text)
        issues = validate_pause_markers(preview_text)
        if issues: st.error("; ".join(issues))
        preview = pronunciation_preview(preview_text, entries)
        prepared_preview = prepare_text(preview_text, project, preview_provider)
        if preview["changed"]: st.success("Pronunciation rules changed the preview text.")
        else: st.info("No pronunciation rule matched the preview text.")
        st.code(prepared_preview)
        st.caption("Cloud providers compile valid pause markers to SSML breaks. Kokoro receives punctuation-based pause approximations.")

elif page == "Audio Quality Lab":
    mode = st.radio("Workflow", ["Analyze and process WAV", "A/B Kokoro comparison"], horizontal=True)
    if mode == "Analyze and process WAV":
        wav_upload = st.file_uploader("16-bit PCM WAV file", type=["wav"], key="quality_wav")
        if wav_upload:
            raw_wav = wav_upload.getvalue()
            try:
                metrics = inspect_wav(raw_wav)
                st.subheader("Source metrics")
                st.dataframe([metrics], use_container_width=True, hide_index=True)
                st.audio(raw_wav, format="audio/wav")
                a, b, c = st.columns(3)
                target_peak = a.slider("Normalize peak dBFS", -12.0, -0.1, -1.0, 0.1)
                silence_threshold = b.slider("Silence threshold dBFS", -80.0, -10.0, -40.0, 1.0)
                padding_ms = c.slider("Trim padding ms", 0, 1000, 100, 10)
                n1, n2 = st.columns(2)
                if n1.button("Create normalized copy"):
                    processed, details = normalize_wav(raw_wav, target_peak)
                    path = save_processed_wav(processed, Path(wav_upload.name).stem, "normalized", OUTPUTS_DIR)
                    st.session_state.audio_processed = {"label": "Normalized", "data": processed, "path": str(path), "details": details, "metrics": inspect_wav(processed)}
                if n2.button("Create trimmed copy"):
                    processed, details = trim_silence_wav(raw_wav, silence_threshold, padding_ms)
                    path = save_processed_wav(processed, Path(wav_upload.name).stem, "trimmed", OUTPUTS_DIR)
                    st.session_state.audio_processed = {"label": "Trimmed", "data": processed, "path": str(path), "details": details, "metrics": inspect_wav(processed)}
                processed_result = st.session_state.get("audio_processed")
                if processed_result:
                    st.subheader(f"{processed_result['label']} result")
                    st.json(processed_result["details"])
                    st.dataframe([processed_result["metrics"]], use_container_width=True, hide_index=True)
                    st.audio(processed_result["data"], format="audio/wav")
                    st.download_button(f"Download {processed_result['label'].lower()} WAV", processed_result["data"], Path(processed_result["path"]).name, "audio/wav")
            except Exception as exc:
                st.error("WAV processing failed: " + user_safe_error(exc))
    else:
        st.caption("Generate the same prepared text twice with independent Kokoro voice and speed settings.")
        comparison_text = st.text_area("Comparison text", project.script if project else "", height=200, max_chars=MAX_BLOCK_CHARS)
        left, right = st.columns(2)
        with left:
            st.subheader("Variant A")
            lang_a = st.selectbox("Language A", KOKORO_VOICES, key="compare_lang_a")
            voice_a = st.selectbox("Voice A", KOKORO_VOICES[lang_a], key="compare_voice_a")
            speed_a = st.slider("Speed A", 0.6, 1.6, 1.0, 0.05, key="compare_speed_a")
        with right:
            st.subheader("Variant B")
            lang_b = st.selectbox("Language B", KOKORO_VOICES, key="compare_lang_b")
            voice_b = st.selectbox("Voice B", KOKORO_VOICES[lang_b], key="compare_voice_b")
            speed_b = st.slider("Speed B", 0.6, 1.6, 1.1, 0.05, key="compare_speed_b")
        if st.button("Generate A/B comparison", type="primary", disabled=not comparison_text.strip()):
            try:
                from peabox_voice_studio.providers.kokoro import generate
                prepared = prepare_text(comparison_text, project, "Kokoro local") if project else comparison_text
                base = safe_filename(project.name if project else "comparison")
                with st.spinner("Generating both variants..."):
                    path_a = generate(prepared, voice_a, KOKORO_LANGS[lang_a], speed_a, f"{base}_A")
                    path_b = generate(prepared, voice_b, KOKORO_LANGS[lang_b], speed_b, f"{base}_B")
                metrics_a = inspect_wav(path_a.read_bytes()); metrics_b = inspect_wav(path_b.read_bytes())
                result = {"text": comparison_text, "paths": [str(path_a), str(path_b)], "variants": [{"label": "A", "language": lang_a, "voice": voice_a, "speed": speed_a}, {"label": "B", "language": lang_b, "voice": voice_b, "speed": speed_b}], "metrics": [metrics_a, metrics_b]}
                st.session_state.comparison_result = result
                if project:
                    create_comparison_record(project, comparison_text, result["variants"], [path_a, path_b], result["metrics"]); save_project(project)
            except Exception as exc:
                st.error("Comparison generation failed: " + user_safe_error(exc))
        result = st.session_state.get("comparison_result")
        if result:
            a, b = st.columns(2)
            for column, label, path_value, variant, metrics in zip((a, b), ("A", "B"), result["paths"], result["variants"], result["metrics"]):
                path = Path(path_value)
                with column:
                    st.subheader(f"Variant {label}")
                    st.caption(f"{variant['voice']} · {variant['language']} · speed {variant['speed']}")
                    if path.exists():
                        data = path.read_bytes(); st.audio(data, format="audio/wav"); st.download_button(f"Download {label}", data, path.name, "audio/wav", key=f"download_compare_{label}")
                    st.dataframe([metrics], use_container_width=True, hide_index=True)
        if project and project.settings.get("comparison_history"):
            st.subheader("Project comparison history")
            history = project.settings["comparison_history"]
            selected_comparison = st.selectbox("Saved comparison", history, format_func=lambda item: f"{item['created_at']} · {item['variants'][0]['voice']} vs {item['variants'][1]['voice']}")
            preference = st.radio("Preferred result", ["", "A", "B", "Tie"], index=["", "A", "B", "Tie"].index(selected_comparison.get("preferred") or ""), horizontal=True)
            comparison_notes = st.text_area("Comparison notes", selected_comparison.get("notes", ""), height=80)
            h1, h2 = st.columns(2)
            if h1.button("Save preference"):
                set_comparison_preference(project, selected_comparison["id"], preference, comparison_notes); save_project(project); st.success("Comparison preference saved")
            if h2.button("Delete comparison record"):
                delete_comparison(project, selected_comparison["id"]); save_project(project); st.rerun()

elif page == "Timeline Studio":
    section("Non-destructive audio assembly", "Arrange compatible WAV assets, inspect readiness, and export a mixed production master.")
    if not project:
        empty_state("No active project", "Open a project before assembling timeline clips.", "Open Project Workspace", "Projects")
    else:
        st.caption("Arrange existing 16-bit PCM WAV assets non-destructively. Original files are never modified.")
        available_wavs = sorted(OUTPUTS_DIR.glob("*.wav"), key=lambda path: path.stat().st_mtime, reverse=True)
        if available_wavs:
            a, b, c, d = st.columns(4)
            selected_wav = a.selectbox("Available WAV", available_wavs, format_func=lambda path: path.name)
            clip_title = b.text_input("Clip title", value=selected_wav.stem if selected_wav else "")
            clip_track = c.text_input("Track", value="Voiceover")
            block_options = [None] + project.blocks
            source_block = d.selectbox("Source block, optional", block_options, format_func=lambda item: "No block link" if item is None else item.title)
            if st.button("Add WAV to timeline", type="primary"):
                try:
                    add_clip(project, selected_wav, clip_title, clip_track, block=source_block); save_project(project); st.rerun()
                except Exception as exc: st.error("Could not add clip: " + user_safe_error(exc))
        else:
            st.info("No WAV files are available yet. Generate Kokoro audio or create a processed WAV in Audio Quality Lab.")
        clips = list_clips(project)
        if clips:
            st.subheader("Timeline controls")
            gap = st.slider("Sequential gap seconds", 0.0, 5.0, 0.25, 0.05)
            t1, t2, t3, t4 = st.columns(4)
            if t1.button("Arrange sequentially"):
                arrange_sequential(project, gap); save_project(project); st.rerun()
            if t2.button("Repair clip records"):
                result = cleanup_invalid_clips(project, remove_missing=False); save_project(project); st.success(f"Kept {result['kept']} clips; repaired {result['repaired_ids']} duplicate IDs")
            if t3.button("Duplicate all clips", disabled=not clips):
                duplicate_timeline(project); save_project(project); st.rerun()
            manifest_json = json.dumps(timeline_manifest(project), ensure_ascii=False, indent=2)
            t4.download_button("Download manifest", manifest_json, f"{safe_filename(project.name)}_timeline_manifest.json", "application/json")
            st.download_button("Download portable timeline bundle", export_timeline_bundle(project), f"{safe_filename(project.name)}_timeline_bundle.zip", "application/zip")
            remove_missing = st.checkbox("Allow removal of missing clip records")
            if st.button("Clean invalid and missing clips", disabled=not remove_missing):
                result = cleanup_invalid_clips(project, remove_missing=True); save_project(project); st.success(f"Removed {result['removed']} missing clips"); st.rerun()
            validation = validate_timeline(project)
            v1, v2, v3 = st.columns(3)
            v1.metric("Enabled clips", validation["enabled_clips"]); v2.metric("Errors", validation["errors"]); v3.metric("Warnings", validation["warnings"])
            if validation["issues"]: st.dataframe(validation["issues"], use_container_width=True, hide_index=True)
            for index, clip in enumerate(clips):
                status = clip_status(project, clip)
                label = f"{index + 1:02}. {clip['title']} · {clip['track']} · {clip['start_seconds']:.2f}s · {'missing' if status['missing'] else 'stale' if status['stale'] else 'ready'}"
                with st.expander(label):
                    clip["enabled"] = st.checkbox("Include in export", clip.get("enabled", True), key=f"clip_enabled_{clip['id']}")
                    x1, x2, x3, x4 = st.columns(4)
                    clip["title"] = x1.text_input("Title", clip["title"], key=f"clip_title_{clip['id']}")
                    clip["track"] = x2.text_input("Track", clip.get("track", "Voiceover"), key=f"clip_track_{clip['id']}")
                    clip["start_seconds"] = x3.number_input("Start seconds", min_value=0.0, value=float(clip.get("start_seconds", 0)), step=0.05, key=f"clip_start_{clip['id']}")
                    clip["gain_db"] = x4.slider("Gain dB", -60.0, 12.0, float(clip.get("gain_db", 0)), 0.5, key=f"clip_gain_{clip['id']}")
                    st.caption(f"{clip['file_name']} · {clip['duration_seconds']:.3f}s · {clip['sample_rate_hz']} Hz · {clip['channels']} channel(s)")
                    if status["missing"]: st.error("The referenced audio file is missing. Upload a replacement WAV below.")
                    elif status["stale"]: st.warning("The linked script block changed after this clip was rendered.")
                    replacement = st.file_uploader("Relink replacement WAV", type=["wav"], key=f"relink_{clip['id']}")
                    r1, r2 = st.columns(2)
                    if r1.button("Relink uploaded WAV", key=f"do_relink_{clip['id']}", disabled=replacement is None):
                        try:
                            base = safe_filename(Path(replacement.name).stem)
                            destination = OUTPUTS_DIR / f"{base}.wav"
                            counter = 2
                            while destination.exists():
                                destination = OUTPUTS_DIR / f"{base}_{counter}.wav"; counter += 1
                            atomic_write_bytes(destination, replacement.getvalue())
                            relink_clip(clip, destination); save_project(project); st.rerun()
                        except Exception as exc: st.error("Relink failed: " + user_safe_error(exc))
                    if r2.button("Refresh audio metadata", key=f"refresh_clip_{clip['id']}", disabled=status["missing"]):
                        try:
                            refresh_clip(clip); save_project(project); st.rerun()
                        except Exception as exc: st.error("Refresh failed: " + user_safe_error(exc))
                    if status["stale"] and st.button("Acknowledge current block version", key=f"ack_stale_{clip['id']}"):
                        acknowledge_clip_source(project, clip); save_project(project); st.rerun()
                    peaks = clip.get("peaks", [])
                    if peaks: st.bar_chart({"peak": peaks}, height=120)
                    if not status["missing"]:
                        clip_path = Path(clip["file"])
                        st.audio(clip_path.read_bytes(), format="audio/wav")
                    c1, c2, c3, c4 = st.columns(4)
                    if c1.button("Save clip", key=f"save_clip_{clip['id']}"): save_project(project); st.success("Clip saved")
                    if c2.button("Move up", key=f"clip_up_{clip['id']}", disabled=index == 0): move_clip(project, index, -1); save_project(project); st.rerun()
                    if c3.button("Move down", key=f"clip_down_{clip['id']}", disabled=index == len(clips)-1): move_clip(project, index, 1); save_project(project); st.rerun()
                    if c4.button("Remove clip", key=f"remove_clip_{clip['id']}"): remove_clip(project, clip["id"]); save_project(project); st.rerun()
            st.subheader("Timeline export")
            export_name = st.text_input("Timeline output name", value=safe_filename(project.name))
            if st.button("Build merged WAV", type="primary", disabled=not validation["valid"]):
                try:
                    with st.spinner("Mixing timeline..."):
                        output_path, export_manifest = mix_timeline(project, export_name, OUTPUTS_DIR)
                    save_project(project)
                    data = output_path.read_bytes(); st.audio(data, format="audio/wav")
                    st.download_button("Download merged WAV", data, output_path.name, "audio/wav")
                    st.download_button("Download export manifest", json.dumps(export_manifest, ensure_ascii=False, indent=2), f"{safe_filename(export_name)}_manifest.json", "application/json")
                    st.success(f"Created {output_path.name}")
                except Exception as exc: st.error("Timeline export failed: " + user_safe_error(exc))
        else:
            st.info("Add at least one WAV clip to begin arranging the timeline.")

elif page == "Script Blocks":
    section("Structured script production", "Each block carries independent provider, voice, pacing, pronunciation, and inclusion settings.")
    if not project:
        empty_state("No active project", "Open or create a project before editing script blocks.", "Open Project Workspace", "Projects")
    else:
        st.caption("Divide a script into independently configurable voice blocks. Reorder, duplicate, disable, and batch-plan without changing the Master Script.")
        a, b, c, d, e = st.columns(5)
        if a.button("Add blank block", type="primary"):
            project.blocks.append(ScriptBlock(title=f"Block {len(project.blocks)+1}")); save_project(project); st.rerun()
        if b.button("Import paragraphs", disabled=not project.script.strip()):
            project.blocks.extend(split_script_into_blocks(project.script)); save_project(project); st.rerun()
        if c.button("Enable all", disabled=not project.blocks):
            set_all_blocks_enabled(project.blocks, True); save_project(project); st.rerun()
        if d.button("Disable all", disabled=not project.blocks):
            set_all_blocks_enabled(project.blocks, False); save_project(project); st.rerun()
        if e.button("Save all", disabled=not project.blocks): save_project(project); st.success("Blocks saved")
        filter_text = st.text_input("Filter blocks", placeholder="Title, text, provider, or voice").strip().lower()
        visible = [(index, block) for index, block in enumerate(project.blocks) if not filter_text or filter_text in " ".join([block.title, block.text, block.provider, block.voice, block.notes]).lower()]
        if not project.blocks: st.info("Add a block or import paragraphs from the Master Script.")
        elif not visible: st.info("No blocks match the filter.")
        for index, block in visible: block_editor(project, index, block)

elif page == "Batch Production":
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

elif page == "Create Speech":
    text = st.text_area("Text", project.script if project else "", height=280, max_chars=MAX_SCRIPT_CHARS)
    output_name = st.text_input("Output name", safe_filename(project.name if project else "narration"))
    a, b, c = st.columns(3)
    language = a.selectbox("Language", KOKORO_VOICES)
    voice = b.selectbox("Voice", KOKORO_VOICES[language])
    speed = c.slider("Speed", 0.6, 1.6, 1.0, 0.05)
    if st.button("Generate local speech", type="primary", disabled=not text.strip()):
        try:
            from peabox_voice_studio.providers.kokoro import generate
            generation_text = prepare_text(text, project, "Kokoro local") if project else text
            with st.spinner("Generating speech..."): path = generate(generation_text, voice, KOKORO_LANGS[language], speed, output_name)
            data = path.read_bytes(); st.audio(data); st.download_button("Download WAV", data, path.name)
            if project:
                record_render(project, "Kokoro local", path, len(text), {"language": language, "voice": voice, "speed": speed}); save_project(project)
        except Exception as exc: st.error("Generation failed: " + user_safe_error(exc))

elif page == "Transcription":
    section("Local media transcription", "Transcribe privately, edit timestamped segments, validate timing, and export TXT, SRT, or VTT.")
    upload = st.file_uploader("Audio or video", type=["wav", "mp3", "m4a", "flac", "ogg", "mp4", "mov", "mkv", "webm"])
    a, b = st.columns(2)
    model_size = a.selectbox("Model", ["tiny", "base", "small", "medium", "large-v3"], index=1)
    language = b.selectbox("Language", ["Auto", "en", "hi", "de", "fr", "es", "it", "pt", "ja", "zh"])
    media_ready = transcription_readiness(upload.name if upload else "")
    if upload and upload.size > MAX_UPLOAD_BYTES: st.error("File exceeds the 500 MB limit")
    if upload and not media_ready["ready"]: st.error(media_ready["message"] + ". Open System Check for setup guidance.")
    if st.button("Transcribe locally", type="primary", disabled=not upload or (upload and upload.size > MAX_UPLOAD_BYTES) or not media_ready["ready"]):
        try:
            from peabox_voice_studio.services.transcription import transcribe
            with st.spinner("Transcribing locally..."):
                rows, detected = transcribe(upload.getvalue(), upload.name, model_size, language)
            st.session_state.transcript_working = {"source_name": upload.name, "language": detected, "segments": normalize_segments(rows)}
            st.success(f"Detected language: {detected}")
        except Exception as exc: st.error("Transcription failed: " + user_safe_error(exc))
    working = st.session_state.get("transcript_working")
    if working:
        st.subheader("Edit transcript segments")
        search = st.text_input("Search current transcript", placeholder="Text or speaker")
        if search:
            st.dataframe(filter_segments(working["segments"], search), use_container_width=True, hide_index=True)
        edited = st.data_editor(working["segments"], use_container_width=True, hide_index=True, num_rows="dynamic", disabled=["index"], key="transcript_editor")
        if edited is not None:
            working["segments"] = normalize_segments(edited.to_dict("records") if hasattr(edited, "to_dict") else edited)
        validation = validate_segments(working["segments"])
        v1, v2, v3 = st.columns(3)
        v1.metric("Timing errors", validation["errors"])
        v2.metric("Warnings", validation["warnings"])
        v3.metric("Segments", len(validation["segments"]))
        if validation["issues"]:
            st.dataframe(validation["issues"], use_container_width=True, hide_index=True)
        if st.button("Repair timing automatically", disabled=validation["valid"]):
            working["segments"] = repair_segment_timing(working["segments"]); st.rerun()
        stem = safe_filename(Path(working.get("source_name") or "transcript").stem)
        if validation["valid"]:
            bundle = export_transcript_bundle(working["segments"])
            x, y, z = st.columns(3)
            x.download_button("Download TXT", bundle["txt"], f"{stem}.txt")
            y.download_button("Download SRT", bundle["srt"], f"{stem}.srt")
            z.download_button("Download VTT", bundle["vtt"], f"{stem}.vtt")
        else:
            st.error("Repair transcript timing before export or saving.")
        if project:
            session_name = st.text_input("Saved transcript name", value=stem)
            if st.button("Save transcript to project", disabled=not validation["valid"]):
                try:
                    save_transcript_session(project, session_name, working["segments"], working.get("source_name", ""), working.get("language", "")); save_project(project); st.success("Transcript saved to project")
                except Exception as exc: st.error("Could not save transcript: " + user_safe_error(exc))
            sessions = project.settings.get("transcript_sessions", [])
            if sessions:
                st.subheader("Saved transcript sessions")
                selected_session = st.selectbox("Saved transcript", sessions, format_func=lambda item: f"{item['name']} · {item.get('updated_at', item['created_at'])}")
                l1, l2, l3 = st.columns(3)
                if l1.button("Load selected transcript"):
                    loaded_validation = validate_segments(selected_session.get("segments", []))
                    loaded_segments = loaded_validation["segments"] if loaded_validation["valid"] else repair_segment_timing(selected_session.get("segments", []))
                    st.session_state.transcript_working = {"source_name": selected_session.get("source_name", ""), "language": selected_session.get("language", ""), "segments": loaded_segments, "session_id": selected_session["id"]}; st.rerun()
                if l2.button("Update selected transcript", disabled=not validation["valid"]):
                    update_transcript_session(project, selected_session["id"], working["segments"]); save_project(project); st.success("Saved transcript updated")
                if l3.button("Delete selected transcript"):
                    delete_transcript_session(project, selected_session["id"]); save_project(project); st.rerun()

elif page == "Render History":
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

else:
    section("Product roadmap and operating guidance", "Delivered capabilities, planned architecture, and setup notes for this release.")
    st.markdown("""
### Current release
- Governance Center with ownership, contributors, risk, due dates, and controlled workflow status
- Persistent review comments with priority, targets, resolution, and reopening
- Decision register with rationale and supersession history
- Approval Queue with local attestations and workflow gates
- Append-only application audit entries included in project exports
- Corporate dashboard governance readiness and consolidated activity history

### Planned next
1. Authenticated identity, role-based permissions, and shared projects
2. SQLite repository and background worker process
3. Interactive waveform dragging in a React/Web Audio frontend
4. Optional speaker diarization and speaker alignment

### Setup
Run `start_windows.bat`. The launcher accepts installed Python 3.10, 3.11, or 3.12 and creates or reuses `.venv`. Install FFmpeg for compressed media transcription.
""")
