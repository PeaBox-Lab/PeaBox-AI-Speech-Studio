from peabox_voice_studio.context import AppContext
import streamlit as st
from pathlib import Path
from peabox_voice_studio.config import MAX_BLOCK_CHARS, OUTPUTS_DIR
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES
from peabox_voice_studio.services.audio import inspect_wav, normalize_wav, save_processed_wav, trim_silence_wav
from peabox_voice_studio.services.comparisons import create_comparison_record, delete_comparison, set_comparison_preference
from peabox_voice_studio.services.files import safe_filename, user_safe_error
from peabox_voice_studio.services.quality import prepare_text

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
