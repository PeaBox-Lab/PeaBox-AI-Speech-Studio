from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.services.files import user_safe_error
from peabox_voice_studio.services.quality import add_pronunciation, delete_pronunciation, insert_pause, list_pronunciations, prepare_text, pronunciation_conflicts, pronunciation_preview, validate_pause_markers

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
