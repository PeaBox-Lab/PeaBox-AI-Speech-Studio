from peabox_voice_studio.context import AppContext
from peabox_voice_studio.screens.dependencies import *

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
