import json
from pathlib import Path
import streamlit as st

from peabox_voice_studio.config import APP_NAME, MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, MAX_UPLOAD_BYTES, VERSION
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES, PROVIDER_RATES
from peabox_voice_studio.services.batch import build_manifest
from peabox_voice_studio.services.files import build_render_zip, safe_filename
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.catalogs import capability_rows, catalog_facets, filter_voices
from peabox_voice_studio.services.jobs import add_job, create_job, delete_job, duplicate_job, reopen_cancelled, replace_job, request_cancel, retry_failed, run_job
from peabox_voice_studio.services.presets import apply_preset, create_preset, delete_preset, list_presets
from peabox_voice_studio.services.projects import ProjectStore, export_project, move_block, set_all_blocks_enabled, split_script_into_blocks
from peabox_voice_studio.services.subtitles import to_srt

st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎙️", layout="wide")
store = ProjectStore()
profiles = st.session_state.setdefault("provider_profiles", {})
voice_catalogs = st.session_state.setdefault("voice_catalogs", {})

def configured_providers() -> set[str]:
    return {"Kokoro local", *profiles.keys()}


def current_project() -> Project | None:
    return st.session_state.get("project")


def save_project(project: Project) -> None:
    store.save(project); st.session_state.project = project


def open_project(project_id: str) -> None:
    st.session_state.project = store.load(project_id)


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


st.title(f"🎙️ {APP_NAME}")
st.caption(f"Version {VERSION} · Discoverable multi-provider voice production")
page = st.sidebar.radio("Studio", ["Projects", "Provider Setup", "Voice Library", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History", "Roadmap & Help"])
project = current_project()
st.sidebar.success(f"Active: {project.name}") if project else st.sidebar.info("No active project")

if page == "Projects":
    st.header("Project Workspace")
    left, right = st.columns([1, 2])
    with left:
        name = st.text_input("New project name")
        description = st.text_area("Description", height=90)
        if st.button("Create and open", type="primary", disabled=not name.strip()):
            st.session_state.project = store.create(name, description); st.rerun()
        projects = store.list()
        selected = st.selectbox("Saved projects", projects, format_func=lambda p: f"{p.name} · {p.updated_at[:10]}") if projects else None
        if st.button("Open selected", disabled=selected is None): open_project(selected.id); st.rerun()
        st.divider()
        st.subheader("Import project")
        imported_file = st.file_uploader("PeaBox project JSON", type="json", key="project_import")
        if st.button("Import and open", disabled=imported_file is None):
            try:
                st.session_state.project = store.import_project(imported_file.getvalue())
                st.success("Project imported with a new identity")
                st.rerun()
            except Exception as exc:
                st.error(f"Import failed: {exc}")
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


elif page == "Provider Setup":
    st.header("Provider Setup")
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
            except Exception as exc: st.error(f"Voice discovery failed: {exc}")
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
            except Exception as exc: st.error(f"Voice discovery failed: {exc}")
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
            except Exception as exc: st.error(f"Voice discovery failed: {exc}")
        if st.button("Clear Google session profile"):
            profiles.pop("Google Cloud TTS", None); voice_catalogs.pop("Google Cloud TTS", None); st.rerun()
    counts = {name: len(items) for name, items in voice_catalogs.items()}
    st.subheader("Provider capabilities and readiness")
    st.dataframe(capability_rows(configured_providers(), counts), use_container_width=True, hide_index=True)

elif page == "Voice Library":
    st.header("Voice Library")
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

elif page == "Script Blocks":
    st.header("Script Blocks")
    if not project: st.info("Open a project first.")
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
    st.header("Batch Production")
    if not project:
        st.info("Open a project first.")
    elif not project.blocks:
        st.info("Create script blocks before building a batch.")
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
                job = create_job(project, PROVIDER_RATES, ready_providers); add_job(project, job); save_project(project); st.success("Batch job created")
            except Exception as exc: st.error(f"Job creation failed: {exc}")
        jobs = project.settings.get("batch_jobs", [])
        if jobs:
            selected_job = st.selectbox("Saved batch jobs", jobs, format_func=lambda item: f"{item['created_at']} · {item['status']} · {item['id'][:8]}")
            summary = selected_job.get("summary", {})
            st.caption(f"Estimated ${summary.get('estimated_cost_usd', 0):.4f} · Recorded usage cost ${summary.get('actual_cost_usd', 0):.4f}. Recorded usage cost is calculated from successful characters at the planning rate; it is not a provider invoice.")
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
    st.header("Create Speech")
    text = st.text_area("Text", project.script if project else "", height=280, max_chars=MAX_SCRIPT_CHARS)
    output_name = st.text_input("Output name", safe_filename(project.name if project else "narration"))
    a, b, c = st.columns(3)
    language = a.selectbox("Language", KOKORO_VOICES)
    voice = b.selectbox("Voice", KOKORO_VOICES[language])
    speed = c.slider("Speed", 0.6, 1.6, 1.0, 0.05)
    if st.button("Generate local speech", type="primary", disabled=not text.strip()):
        try:
            from peabox_voice_studio.providers.kokoro import generate
            with st.spinner("Generating speech..."): path = generate(text, voice, KOKORO_LANGS[language], speed, output_name)
            data = path.read_bytes(); st.audio(data); st.download_button("Download WAV", data, path.name)
            if project:
                record_render(project, "Kokoro local", path, len(text), {"language": language, "voice": voice, "speed": speed}); save_project(project)
        except Exception as exc: st.error(f"Generation failed: {exc}")

elif page == "Transcription":
    st.header("Local Transcription")
    upload = st.file_uploader("Audio or video", type=["wav", "mp3", "m4a", "flac", "ogg", "mp4", "mov", "mkv", "webm"])
    a, b = st.columns(2)
    model_size = a.selectbox("Model", ["tiny", "base", "small", "medium", "large-v3"], index=1)
    language = b.selectbox("Language", ["Auto", "en", "hi", "de", "fr", "es", "it", "pt", "ja", "zh"])
    if upload and upload.size > MAX_UPLOAD_BYTES: st.error("File exceeds the 500 MB limit")
    if st.button("Transcribe", type="primary", disabled=not upload or (upload and upload.size > MAX_UPLOAD_BYTES)):
        try:
            from peabox_voice_studio.services.transcription import transcribe
            with st.spinner("Transcribing locally..."): rows, detected = transcribe(upload.getvalue(), upload.name, model_size, language)
            transcript = " ".join(row["text"] for row in rows); srt = to_srt(rows); stem = safe_filename(Path(upload.name).stem)
            st.success(f"Detected language: {detected}"); st.text_area("Transcript", transcript, height=260)
            st.download_button("Download TXT", transcript, f"{stem}.txt"); st.download_button("Download SRT", srt, f"{stem}.srt"); st.dataframe(rows, use_container_width=True)
        except Exception as exc: st.error(f"Transcription failed: {exc}")

elif page == "Render History":
    st.header("Render History")
    if not project: st.info("Open a project first.")
    elif not project.render_history: st.info("No single renders recorded for this project.")
    else: st.dataframe(project.render_history, use_container_width=True)

else:
    st.header("Roadmap & Help")
    st.markdown("""
### Current release
- Session-cached voice discovery for Azure, Polly, and Google with a searchable cross-provider library
- Provider capability/readiness matrix and catalog-aware block voice selection
- Reusable project voice presets with provider, language, voice, speed, and direction notes
- Persistent jobs with resume, retry, cancellation, reopen, duplicate, delete, and output download controls
- Session-only credentials excluded from project files and exports

### Planned next
1. Pronunciation dictionary and provider-aware SSML controls
2. Transcript editing, VTT export, and optional diarization
3. Audio normalization, silence controls, and A/B renders
4. Waveform metadata and non-destructive clip timeline
5. Separate worker process and SQLite repository before hosted multi-user use

### Setup
Run `start_windows.bat`. The launcher accepts installed Python 3.10, 3.11, or 3.12 and creates or reuses `.venv`. Install FFmpeg for compressed media transcription.
""")
