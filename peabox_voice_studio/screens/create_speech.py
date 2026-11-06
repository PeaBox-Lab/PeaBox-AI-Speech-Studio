from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.config import MAX_SCRIPT_CHARS
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES
from peabox_voice_studio.services.files import safe_filename, user_safe_error
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.quality import prepare_text

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
