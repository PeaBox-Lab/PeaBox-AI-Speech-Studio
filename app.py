import streamlit as st
from peabox_voice_studio.config import APP_NAME,VERSION
from peabox_voice_studio.context import AppContext
from peabox_voice_studio.models import Project
from peabox_voice_studio.screens.registry import SCREEN_RENDERERS,render_screen
from peabox_voice_studio.services.preferences import load_preferences,mark_project_opened,save_preferences
from peabox_voice_studio.services.projects import ProjectStore
from peabox_voice_studio.ui import inject_corporate_theme,page_header,sidebar_navigation

st.set_page_config(page_title=f'{APP_NAME} {VERSION}',page_icon='🎙️',layout='wide',initial_sidebar_state='expanded')
ui_preferences=st.session_state.setdefault('ui_preferences',load_preferences())
inject_corporate_theme(ui_preferences)
store=ProjectStore()
profiles=st.session_state.setdefault('provider_profiles',{})
voice_catalogs=st.session_state.setdefault('voice_catalogs',{})
st.session_state.setdefault('governance_actor','Local User')

def configured_providers()->set[str]:return {'Kokoro local',*profiles.keys()}
def current_project()->Project|None:return st.session_state.get('project')
def save_project(project:Project)->None:store.save(project);st.session_state.project=project
def open_project(project_id:str)->None:
    st.session_state.project=store.load(project_id);mark_project_opened(ui_preferences,project_id);save_preferences(ui_preferences)
def set_active_project(project:Project)->None:
    st.session_state.project=project;mark_project_opened(ui_preferences,project.id);save_preferences(ui_preferences)

project=current_project()
ctx=AppContext(VERSION,store,project,ui_preferences,profiles,voice_catalogs,configured_providers,save_project,open_project,set_active_project)
page=sidebar_navigation(VERSION,project,ui_preferences)
page_header(page,VERSION,project)
if page not in SCREEN_RENDERERS:st.error(f'Unknown screen: {page}')
else:render_screen(page,ctx)
