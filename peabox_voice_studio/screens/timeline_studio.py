from peabox_voice_studio.context import AppContext
from peabox_voice_studio.facades.timeline import acknowledge_clip_source, add_clip, arrange_sequential, cleanup_invalid_clips, clip_status, duplicate_timeline, export_timeline_bundle, list_clips, mix_timeline, move_clip, refresh_clip, relink_clip, remove_clip, timeline_manifest, validate_timeline
import json
import streamlit as st
from pathlib import Path
from peabox_voice_studio.config import OUTPUTS_DIR
from peabox_voice_studio.services.files import atomic_write_bytes, safe_filename, user_safe_error
from peabox_voice_studio.ui import empty_state, section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
