import json
from pathlib import Path
import streamlit as st
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.ui import callout, empty_state, kpi_card, navigate_to, section, workflow_step
from peabox_voice_studio.services.commands import record_command, resolve_commands, search_commands
from peabox_voice_studio.services.preferences import save_preferences

def render(ctx: AppContext) -> None:
    project=ctx.project; ui_preferences=ctx.preferences
    section("Search workspace commands", "Commands navigate to safe screens and never execute destructive project actions.")
    command_query = st.text_input("Search screens and workflows", placeholder="Try: transcript, batch, provider, approval, timeline")
    command_results = search_commands(command_query, project is not None)
    if command_results:
        selected_command = st.selectbox("Command results", command_results, format_func=lambda item: f"{item['group']} · {item['label']}{'' if item['available'] else ' · project required'}")
        st.caption(f"Keywords: {selected_command['keywords']}")
        if st.button("Open selected command", type="primary", disabled=not selected_command["available"]):
            record_command(ui_preferences, selected_command["id"]); save_preferences(ui_preferences); navigate_to(selected_command["page"]); st.rerun()
        if not selected_command["available"]:
            empty_state("Active project required", "Open or create a project before using this command.", "Open Project Workspace", "Projects")
    else:
        empty_state("No command found", "Try a broader term such as audio, script, review, provider, or history.")
    recent_commands = resolve_commands(ui_preferences.get("recent_command_ids", []))
    if recent_commands:
        section("Recent commands", "Reopen frequently used workflows without searching again.")
        recent_columns = st.columns(min(4, len(recent_commands)))
        for index, command in enumerate(recent_commands[:8]):
            column = recent_columns[index % len(recent_columns)]
            if column.button(command["label"], key=f"recent_command_{command['id']}", use_container_width=True):
                record_command(ui_preferences, command["id"]); save_preferences(ui_preferences); navigate_to(command["page"]); st.rerun()
