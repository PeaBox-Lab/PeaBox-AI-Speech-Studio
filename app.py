import json
from pathlib import Path
import streamlit as st

from peabox_voice_studio.config import APP_NAME, MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, MAX_UPLOAD_BYTES, VERSION
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES, PROVIDER_RATES
from peabox_voice_studio.services.batch import build_manifest, render_local_blocks, summarize_results
from peabox_voice_studio.services.files import build_render_zip, safe_filename
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.projects import ProjectStore, export_project, move_block, set_all_blocks_enabled, split_script_into_blocks
from peabox_voice_studio.services.subtitles import to_srt

st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎙️", layout="wide")
store = ProjectStore()


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
        block.provider = a.selectbox("Provider", ["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"], index=["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"].index(block.provider) if block.provider in ["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"] else 0, key=f"provider_{block.id}")
        block.language = b.selectbox("Language", list(KOKORO_VOICES), index=list(KOKORO_VOICES).index(block.language) if block.language in KOKORO_VOICES else 0, key=f"lang_{block.id}")
        voices = KOKORO_VOICES[block.language]
        block.voice = c.selectbox("Voice", voices, index=voices.index(block.voice) if block.voice in voices else 0, key=f"voice_{block.id}")
        block.speed = d.slider("Speed", 0.6, 1.6, float(block.speed), 0.05, key=f"speed_{block.id}")
        block.notes = st.text_input("Direction notes", block.notes, placeholder="Optional pacing, pronunciation, or performance note", key=f"notes_{block.id}")
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
st.caption(f"Version {VERSION} · Reliable multi-block voice production")
page = st.sidebar.radio("Studio", ["Projects", "Script Blocks", "Batch Production", "Create Speech", "Transcription", "Render History", "Roadmap & Help"])
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
    if not project: st.info("Open a project first.")
    elif not project.blocks: st.info("Create script blocks before building a batch.")
    else:
        manifest = build_manifest(project, PROVIDER_RATES)
        totals = manifest["totals"]
        a, b, c, d = st.columns(4)
        a.metric("Enabled blocks", totals["enabled_blocks"]); b.metric("Characters", f"{totals['characters']:,}"); c.metric("Est. audio", f"{totals['estimated_minutes']:.1f} min"); d.metric("Est. cost", f"${totals['estimated_cost_usd']:.4f}")
        st.dataframe(manifest["blocks"], use_container_width=True, hide_index=True)
        validation = manifest["validation"]
        if validation["ready"]:
            st.success(f"Batch validation passed with {validation['warnings']} warning(s).")
        else:
            st.error(f"Batch is not ready: {validation['errors']} error(s), {validation['warnings']} warning(s).")
        if validation["issues"]:
            st.dataframe(validation["issues"], use_container_width=True, hide_index=True)
        st.download_button("Download render manifest", json.dumps(manifest, ensure_ascii=False, indent=2), f"{safe_filename(project.name)}_manifest.json", "application/json")
        st.warning("This release batch-renders Kokoro local blocks. Cloud blocks remain in the manifest and are skipped until credential profiles and asynchronous jobs are added.")
        if st.button("Render enabled local blocks", type="primary", disabled=not validation["ready"] or not any(b.enabled and b.provider == "Kokoro local" and b.text.strip() for b in project.blocks)):
            from peabox_voice_studio.providers.kokoro import generate
            def local_generate(text, voice, language, speed, name):
                return generate(text, voice, KOKORO_LANGS.get(language, "en-us"), speed, name)
            with st.spinner("Rendering enabled local blocks..."):
                files, results = render_local_blocks(project, local_generate)
            manifest["results"] = results
            summary = summarize_results(results)
            project.settings["last_batch"] = {"created_at": manifest["created_at"], "summary": summary, "results": results}
            save_project(project)
            if files:
                package = build_render_zip(files, manifest)
                st.success(f"Rendered {summary['rendered']} block(s); skipped {summary['skipped']}; failed {summary['failed']}.")
                st.download_button("Download batch ZIP", package, f"{safe_filename(project.name)}_batch.zip", "application/zip")
            st.dataframe(results, use_container_width=True, hide_index=True)
        last_batch = project.settings.get("last_batch")
        if last_batch:
            with st.expander("Last saved batch result"):
                st.json(last_batch)

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
- Portable project JSON export/import with collision-safe imported identities
- Ordered script blocks with bulk enable/disable, filtering, and append-or-replace paragraph import
- Batch-readiness validation for missing titles, empty enabled text, voices, and unsupported cloud execution
- Versioned render manifests, local Kokoro batch ZIPs, and persistent last-batch results
- Local Faster-Whisper transcription with TXT and standards-compatible SRT export

### Planned next
1. Credential profiles and asynchronous cloud batch jobs
2. Waveform metadata and non-destructive clip timeline
3. Voice library filters, pronunciation dictionary, and reusable presets
4. Optional local diarization and speaker-labelled transcripts
5. SQLite repository and background workers before hosted multi-user use
6. Consent/provenance modules only after authoritative legal and technical validation

### Setup
Run `start_windows.bat`. The launcher accepts installed Python 3.10, 3.11, or 3.12 and creates or reuses `.venv`. Install FFmpeg for compressed media transcription.
""")
