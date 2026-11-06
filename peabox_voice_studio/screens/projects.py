from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.config import MAX_SCRIPT_CHARS, OUTPUTS_DIR
from peabox_voice_studio.services.bundles import import_timeline_bundle
from peabox_voice_studio.services.files import safe_filename, user_safe_error
from peabox_voice_studio.services.preferences import resolve_projects, save_preferences, toggle_favorite
from peabox_voice_studio.services.projects import export_project, split_script_into_blocks
from peabox_voice_studio.ui import section

def render(ctx: AppContext) -> None:
    store=ctx.store; project=ctx.project; ui_preferences=ctx.preferences
    profiles=ctx.profiles; voice_catalogs=ctx.voice_catalogs
    configured_providers=ctx.configured_providers; save_project=ctx.save_project
    open_project=ctx.open_project; set_active_project=ctx.set_active_project
    section("Project portfolio", "Create, open, import, and maintain the production workspace and master script.")
    left, right = st.columns([1, 2])
    with left:
        name = st.text_input("New project name")
        description = st.text_area("Description", height=90)
        if st.button("Create and open", type="primary", disabled=not name.strip()):
            set_active_project(store.create(name, description)); st.rerun()
        projects = store.list()
        selected = st.selectbox("Saved projects", projects, format_func=lambda p: f"{p.name} · {p.updated_at[:10]}") if projects else None
        p_open, p_fav = st.columns(2)
        if p_open.button("Open selected", disabled=selected is None, use_container_width=True): open_project(selected.id); st.rerun()
        is_favorite = bool(selected and selected.id in ui_preferences.get("favorite_project_ids", []))
        if p_fav.button("Remove favorite" if is_favorite else "Add favorite", disabled=selected is None, use_container_width=True):
            toggle_favorite(ui_preferences, selected.id); save_preferences(ui_preferences); st.rerun()
        favorite_projects = resolve_projects(projects, ui_preferences.get("favorite_project_ids", []))
        recent_projects = resolve_projects(projects, ui_preferences.get("recent_project_ids", []))
        if favorite_projects:
            st.caption("Favorites: " + " · ".join(item.name for item in favorite_projects[:5]))
        if recent_projects:
            st.caption("Recent: " + " · ".join(item.name for item in recent_projects[:5]))
        st.divider()
        st.subheader("Import project")
        imported_file = st.file_uploader("PeaBox project JSON", type="json", key="project_import")
        if st.button("Import and open", disabled=imported_file is None):
            try:
                set_active_project(store.import_project(imported_file.getvalue()))
                st.success("Project imported with a new identity")
                st.rerun()
            except Exception as exc:
                st.error("Import failed: " + user_safe_error(exc))
        st.subheader("Import timeline bundle")
        bundle_file = st.file_uploader("PeaBox timeline bundle ZIP", type="zip", key="timeline_bundle_import")
        if st.button("Import bundle and open", disabled=bundle_file is None):
            try:
                imported_project = import_timeline_bundle(bundle_file.getvalue(), OUTPUTS_DIR)
                set_active_project(store.save(imported_project))
                st.success("Timeline bundle imported with local asset copies")
                st.rerun()
            except Exception as exc:
                st.error("Bundle import failed: " + user_safe_error(exc))
    with right:
        project = ctx.project
        if not project: st.info("Create or open a project to begin.")
        else:
            project.name = st.text_input("Project name", project.name)
            project.description = st.text_area("Description", project.description, height=90)
            project.script = st.text_area("Master Script", project.script, height=330, max_chars=MAX_SCRIPT_CHARS)
            words = len(project.script.split())
            a, b, c, d = st.columns(4)
            a.metric("Characters", f"{len(project.script):,}"); b.metric("Words", f"{words:,}"); c.metric("Est. audio", f"{words/150:.1f} min"); d.metric("Blocks", len(project.blocks))
            x, y, z, q = st.columns(4)
            if x.button("Save project", type="primary"): save_project(project); st.success("Project saved")
            y.download_button("Export script", project.script, f"{safe_filename(project.name)}.txt")
            q.download_button("Export project JSON", export_project(project), f"{safe_filename(project.name)}_project.json", "application/json")
            block_import_mode = st.radio("Master Script block import", ["Append", "Replace existing"], horizontal=True)
            if z.button("Create blocks from paragraphs", disabled=not project.script.strip()):
                new_blocks = split_script_into_blocks(project.script)
                project.blocks = new_blocks if block_import_mode == "Replace existing" else project.blocks + new_blocks
                save_project(project); st.success(f"{'Created' if block_import_mode == 'Replace existing' else 'Added'} {len(new_blocks)} blocks")
            with st.expander("Delete project"):
                confirm = st.checkbox("I understand this permanently deletes the project")
                if st.button("Delete permanently", disabled=not confirm): store.delete(project.id); st.session_state.pop("project", None); st.rerun()
