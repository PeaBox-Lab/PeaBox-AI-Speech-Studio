import json
from pathlib import Path
import streamlit as st
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.ui import callout, empty_state, kpi_card, navigate_to, section, workflow_step
from peabox_voice_studio.services.preferences import save_preferences

def render(ctx: AppContext) -> None:
    ui_preferences=ctx.preferences
    section("Personal workspace preferences", "These preferences are stored locally on this device and are not included in project exports.")
    area_options = ["Overview", "Production", "Audio & Quality", "Administration", "Support"]
    default_area = st.selectbox("Default workspace area", area_options, index=area_options.index(ui_preferences.get("default_area", "Overview")) if ui_preferences.get("default_area") in area_options else 0)
    dashboard_detail = st.radio("Dashboard detail", ["Compact", "Standard", "Detailed"], index=["Compact", "Standard", "Detailed"].index(ui_preferences.get("dashboard_detail", "Standard")), horizontal=True)
    p1, p2 = st.columns(2)
    compact_navigation = p1.checkbox("Compact sidebar navigation", value=ui_preferences.get("compact_navigation", False))
    reduced_motion = p2.checkbox("Reduce interface motion", value=ui_preferences.get("reduced_motion", False))
    if st.button("Save interface preferences", type="primary"):
        ui_preferences.update({"default_area": default_area, "dashboard_detail": dashboard_detail, "compact_navigation": compact_navigation, "reduced_motion": reduced_motion})
        save_preferences(ui_preferences)
        st.success("Preferences saved. Layout preferences apply immediately after refresh.")
    section("Local preference data", "Favorites and recent-project history can be cleared without modifying project files.")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Clear recent projects", disabled=not ui_preferences.get("recent_project_ids")):
        ui_preferences["recent_project_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c2.button("Clear favorites", disabled=not ui_preferences.get("favorite_project_ids")):
        ui_preferences["favorite_project_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c3.button("Clear recent commands", disabled=not ui_preferences.get("recent_command_ids")):
        ui_preferences["recent_command_ids"] = []; save_preferences(ui_preferences); st.rerun()
    if c4.button("Show onboarding again", disabled=not ui_preferences.get("onboarding_dismissed", False)):
        ui_preferences["onboarding_dismissed"] = False; save_preferences(ui_preferences); st.rerun()
    st.json({"default_area": ui_preferences.get("default_area"), "dashboard_detail": ui_preferences.get("dashboard_detail"), "compact_navigation": ui_preferences.get("compact_navigation"), "reduced_motion": ui_preferences.get("reduced_motion"), "recent_projects": len(ui_preferences.get("recent_project_ids", [])), "favorites": len(ui_preferences.get("favorite_project_ids", [])), "recent_commands": len(ui_preferences.get("recent_command_ids", [])), "onboarding_dismissed": ui_preferences.get("onboarding_dismissed", False)})
