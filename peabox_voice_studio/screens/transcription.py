from peabox_voice_studio.context import AppContext
import streamlit as st
from pathlib import Path
from peabox_voice_studio.config import MAX_UPLOAD_BYTES
from peabox_voice_studio.services.diagnostics import transcription_readiness
from peabox_voice_studio.services.files import safe_filename, user_safe_error
from peabox_voice_studio.services.transcripts import delete_transcript_session, export_transcript_bundle, filter_segments, normalize_segments, repair_segment_timing, save_transcript_session, update_transcript_session, validate_segments
from peabox_voice_studio.ui import section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
