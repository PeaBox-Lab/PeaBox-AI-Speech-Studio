from peabox_voice_studio.context import AppContext
from peabox_voice_studio.screens import command_center,dashboard,help,operations,preferences
SCREEN_RENDERERS={"Dashboard":dashboard.render,"Command Center":command_center.render,"Preferences":preferences.render,"Operations":operations.render,"Roadmap & Help":help.render}
def render_screen(page:str,ctx:AppContext)->None:SCREEN_RENDERERS[page](ctx)
