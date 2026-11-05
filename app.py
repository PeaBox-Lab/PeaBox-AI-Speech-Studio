from pathlib import Path

import streamlit as st

from peabox_voice_studio.config import APP_NAME, MAX_SCRIPT_CHARS, MAX_UPLOAD_BYTES, OUTPUTS_DIR, VERSION
from peabox_voice_studio.models import Project
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES, PRICE_GUIDE
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.projects import ProjectStore
from peabox_voice_studio.services.subtitles import to_srt

st.set_page_config(page_title=f"{APP_NAME} {VERSION}", page_icon="🎙️", layout="wide")
store = ProjectStore()


def load_project(project_id: str) -> None:
    st.session_state.project = store.load(project_id)


def current_project() -> Project | None:
    return st.session_state.get("project")


def save_project(project: Project) -> None:
    store.save(project)
    st.session_state.project = project


st.title(f"🎙️ {APP_NAME}")
st.caption(f"Version {VERSION} · Project-based speech creation and transcription")
page = st.sidebar.radio("Workspace", ["Projects", "Create Speech", "Transcription", "Render History", "Cost Guide", "Help"])
project = current_project()
if project:
    st.sidebar.success(f"Active: {project.name}")
else:
    st.sidebar.info("No active project")

if page == "Projects":
    st.header("Project Workspace")
    left, right = st.columns([1, 2])
    with left:
        st.subheader("Create project")
        new_name = st.text_input("Project name", key="new_project_name")
        new_description = st.text_area("Description", key="new_project_description", height=100)
        if st.button("Create and open", type="primary", disabled=not new_name.strip()):
            st.session_state.project = store.create(new_name, new_description)
            st.rerun()
        st.subheader("Open project")
        projects = store.list()
        chosen = st.selectbox("Saved projects", projects, format_func=lambda item: f"{item.name} · {item.updated_at[:10]}") if projects else None
        if st.button("Open selected", disabled=chosen is None):
            load_project(chosen.id)
            st.rerun()
    with right:
        project = current_project()
        if not project:
            st.info("Create or open a project to edit its master script.")
        else:
            st.subheader("Project details")
            project.name = st.text_input("Name", project.name)
            project.description = st.text_area("Description", project.description, height=90)
            project.script = st.text_area("Master Script", project.script, height=360, max_chars=MAX_SCRIPT_CHARS)
            words = len(project.script.split())
            a, b, c = st.columns(3)
            a.metric("Characters", f"{len(project.script):,}")
            b.metric("Words", f"{words:,}")
            c.metric("Estimated audio", f"{words / 150:.1f} min")
            save_col, export_col = st.columns(2)
            if save_col.button("Save project", type="primary"):
                save_project(project)
                st.success("Project saved")
            export_col.download_button("Export script", project.script, f"{safe_filename(project.name)}.txt")
            with st.expander("Delete project"):
                confirm = st.checkbox("I understand this permanently deletes the project file")
                if st.button("Delete permanently", disabled=not confirm):
                    store.delete(project.id)
                    st.session_state.pop("project", None)
                    st.rerun()

elif page == "Create Speech":
    st.header("Create Speech")
    initial = project.script if project else ""
    text = st.text_area("Text", initial, height=280, max_chars=MAX_SCRIPT_CHARS)
    output_name = st.text_input("Output name", safe_filename(project.name if project else "narration"))
    provider = st.selectbox("Provider", ["Kokoro local", "Azure Speech", "Amazon Polly", "Google Cloud TTS"])
    characters = len(text)
    generated_path = None
    settings = {}
    if provider == "Kokoro local":
        st.info("Free local neural TTS. The first generation downloads model files. Python 3.11 or 3.12 is recommended.")
        a, b, c = st.columns(3)
        language = a.selectbox("Language", KOKORO_VOICES)
        voice = b.selectbox("Voice", KOKORO_VOICES[language])
        speed = c.slider("Speed", 0.6, 1.6, 1.0, 0.05)
        settings = {"language": language, "voice": voice, "speed": speed}
        if st.button("Generate", type="primary", disabled=not text.strip()):
            try:
                from peabox_voice_studio.providers.kokoro import generate
                with st.spinner("Generating speech..."):
                    generated_path = generate(text, voice, KOKORO_LANGS[language], speed, output_name)
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
    elif provider == "Azure Speech":
        key = st.text_input("API key", type="password")
        region = st.text_input("Region", "centralindia")
        a, b = st.columns(2)
        rate = a.slider("Rate %", -50, 100, 0)
        pitch = b.slider("Pitch %", -50, 50, 0)
        if st.button("Discover voices", disabled=not key):
            try:
                from peabox_voice_studio.providers.cloud import azure_list
                st.session_state.azure_voices = azure_list(key, region)
            except Exception as exc:
                st.error(f"Voice discovery failed: {exc}")
        voices = st.session_state.get("azure_voices", [])
        locale = st.selectbox("Locale", ["All"] + sorted({v["Locale"] for v in voices}))
        filtered = [v for v in voices if locale == "All" or v["Locale"] == locale]
        selected = st.selectbox("Voice", filtered, format_func=lambda item: f"{item['DisplayName']} | {item['Locale']} | {item['ShortName']}") if filtered else None
        st.caption(f"Indicative cost: ${characters / 1_000_000 * 15:.4f} at $15 per 1M characters.")
        settings = {"region": region, "rate": rate, "pitch": pitch, "voice": selected["ShortName"] if selected else None}
        if st.button("Generate Azure", type="primary", disabled=not (text.strip() and key and selected)):
            try:
                from peabox_voice_studio.providers.cloud import azure_generate
                data = azure_generate(text, key, region, selected["ShortName"], rate, pitch)
                generated_path = atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", data)
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
    elif provider == "Amazon Polly":
        access = st.text_input("Access key ID")
        secret = st.text_input("Secret access key", type="password")
        token = st.text_input("Session token, optional", type="password")
        region = st.text_input("Region", "ap-south-1")
        engine = st.selectbox("Engine", ["standard", "neural", "generative", "long-form"])
        rates = {"standard": 4, "neural": 16, "generative": 30, "long-form": 100}
        if st.button("Discover voices", disabled=not (access and secret)):
            try:
                from peabox_voice_studio.providers.cloud import aws_client
                st.session_state.polly_voices = aws_client(access, secret, region, token).describe_voices(Engine=engine, IncludeAdditionalLanguageCodes=True)["Voices"]
            except Exception as exc:
                st.error(f"Voice discovery failed: {exc}")
        voices = st.session_state.get("polly_voices", [])
        selected = st.selectbox("Voice", voices, format_func=lambda item: f"{item['Name']} | {item['LanguageCode']} | {item['Id']}") if voices else None
        st.caption(f"Indicative cost: ${characters / 1_000_000 * rates[engine]:.4f} at ${rates[engine]} per 1M characters.")
        settings = {"region": region, "engine": engine, "voice": selected["Id"] if selected else None}
        if st.button("Generate Polly", type="primary", disabled=not (text.strip() and access and secret and selected)):
            try:
                from peabox_voice_studio.providers.cloud import aws_client
                client = aws_client(access, secret, region, token)
                data = client.synthesize_speech(Text=text, OutputFormat="mp3", VoiceId=selected["Id"], Engine=engine)["AudioStream"].read()
                generated_path = atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", data)
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
    else:
        credentials = st.file_uploader("Service-account JSON", type="json")
        language_code = st.text_input("Language code", "en-IN")
        family = st.selectbox("Pricing family", ["Standard/WaveNet", "Neural2/Polyglot", "Chirp 3 HD", "Studio"])
        rates = {"Standard/WaveNet": 4, "Neural2/Polyglot": 16, "Chirp 3 HD": 30, "Studio": 160}
        if credentials:
            st.session_state.google_credentials = credentials.getvalue().decode("utf-8")
        if st.button("Discover voices", disabled=not st.session_state.get("google_credentials")):
            try:
                from peabox_voice_studio.providers.cloud import google_client
                st.session_state.google_voices = list(google_client(st.session_state.google_credentials).list_voices(language_code=language_code).voices)
            except Exception as exc:
                st.error(f"Voice discovery failed: {exc}")
        voices = st.session_state.get("google_voices", [])
        selected = st.selectbox("Voice", voices, format_func=lambda item: f"{item.name} | {','.join(item.language_codes)} | {item.natural_sample_rate_hertz}Hz") if voices else None
        st.caption(f"Indicative cost: ${characters / 1_000_000 * rates[family]:.4f} at ${rates[family]} per 1M characters.")
        settings = {"language": language_code, "family": family, "voice": selected.name if selected else None}
        if st.button("Generate Google", type="primary", disabled=not (text.strip() and selected and st.session_state.get("google_credentials"))):
            try:
                from google.cloud import texttospeech
                from peabox_voice_studio.providers.cloud import google_client
                client = google_client(st.session_state.google_credentials)
                data = client.synthesize_speech(
                    input=texttospeech.SynthesisInput(text=text),
                    voice=texttospeech.VoiceSelectionParams(language_code=selected.language_codes[0], name=selected.name),
                    audio_config=texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3),
                ).audio_content
                generated_path = atomic_write_bytes(OUTPUTS_DIR / f"{safe_filename(output_name)}.mp3", data)
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
    if generated_path:
        data = generated_path.read_bytes()
        st.success(f"Created {generated_path.name}")
        st.audio(data)
        st.download_button("Download audio", data, generated_path.name)
        if project:
            record_render(project, provider, generated_path, characters, settings)
            project.script = text
            project.settings = {"provider": provider, **settings}
            save_project(project)
    st.divider()
    words = len(text.split())
    a, b, c = st.columns(3)
    a.metric("Characters", f"{characters:,}")
    b.metric("Words", f"{words:,}")
    c.metric("Estimated duration", f"{words / 150:.1f} min")

elif page == "Transcription":
    st.header("Transcription")
    upload = st.file_uploader("Audio or video", type=["wav", "mp3", "m4a", "flac", "ogg", "mp4", "mov", "mkv", "webm"])
    a, b = st.columns(2)
    model_size = a.selectbox("Model", ["tiny", "base", "small", "medium", "large-v3"], index=1)
    language = b.selectbox("Language", ["Auto", "en", "hi", "de", "fr", "es", "it", "pt", "ja", "zh"])
    if upload and upload.size > MAX_UPLOAD_BYTES:
        st.error(f"File exceeds the {MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit")
    if st.button("Transcribe", type="primary", disabled=not upload or (upload and upload.size > MAX_UPLOAD_BYTES)):
        try:
            from peabox_voice_studio.services.transcription import transcribe
            with st.spinner("Transcribing..."):
                rows, detected = transcribe(upload.getvalue(), upload.name, model_size, language)
            transcript = " ".join(row["text"] for row in rows)
            srt = to_srt(rows)
            stem = safe_filename(Path(upload.name).stem)
            st.success(f"Detected language: {detected}")
            st.text_area("Transcript", transcript, height=260)
            st.download_button("Download TXT", transcript, f"{stem}.txt")
            st.download_button("Download SRT", srt, f"{stem}.srt")
            st.dataframe(rows, use_container_width=True)
        except Exception as exc:
            st.error(f"Transcription failed: {exc}")

elif page == "Render History":
    st.header("Render History")
    if not project:
        st.info("Open a project to view its render history.")
    elif not project.render_history:
        st.info("No renders have been recorded for this project.")
    else:
        st.dataframe(project.render_history, use_container_width=True)

elif page == "Cost Guide":
    st.header("Indicative planning guide")
    st.dataframe(PRICE_GUIDE, column_config={0: "Provider/model", 1: "USD/1M characters", 2: "Note"}, hide_index=True, use_container_width=True)
    st.warning("These values were carried forward from the attached v0.2 project and were not refreshed from the web. Verify current provider pricing before making purchasing decisions.")

else:
    st.header("Help")
    st.markdown("""
- Use 64-bit Python 3.11 or 3.12.
- Install FFmpeg and add it to PATH for compressed audio and video transcription.
- Cloud credentials remain in the Streamlit session and are not written to project files.
- Keep API keys and service-account JSON out of source control.
- Projects are stored locally under `data/projects`; generated audio is written to `outputs`.
""")
