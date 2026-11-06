from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.ui import section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
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
