from peabox_voice_studio.context import AppContext
from peabox_voice_studio.screens.dependencies import *

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    all_voices = [{"provider": "Kokoro local", "id": voice, "name": voice, "language": language, "gender": "", "styles": []} for language, voices in KOKORO_VOICES.items() for voice in voices]
    for items in voice_catalogs.values(): all_voices.extend(items)
    facets = catalog_facets(all_voices)
    a, b, c = st.columns(3)
    query = a.text_input("Search voices", placeholder="Name, ID, provider, or language")
    language_filter = b.selectbox("Language", ["All"] + facets["languages"])
    gender_filter = c.selectbox("Gender", ["All"] + facets["genders"])
    visible_voices = filter_voices(all_voices, query, language_filter, gender_filter)
    st.caption(f"Showing {len(visible_voices)} of {len(all_voices)} session voices. Cloud catalogs are cached only for this session.")
    st.dataframe(visible_voices, use_container_width=True, hide_index=True)
    if project:
        presets = list_presets(project)
        st.subheader("Project voice presets")
        if presets:
            st.dataframe(presets, use_container_width=True, hide_index=True)
            preset_to_delete = st.selectbox("Delete preset", presets, format_func=lambda item: item["name"])
            if st.button("Delete selected preset"):
                delete_preset(project, preset_to_delete["id"]); save_project(project); st.rerun()
        else: st.info("Save a preset from any script block to reuse its provider, voice, speed, and direction notes.")
