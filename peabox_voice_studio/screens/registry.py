from peabox_voice_studio.context import AppContext
from peabox_voice_studio.screens import (
    approvals,audio_quality_lab,batch_production,command_center,create_speech,dashboard,
    governance,help,operations,preferences,projects,provider_setup,quality_studio,
    render_history,script_blocks,system_check,timeline_studio,transcription,voice_library,
)
SCREEN_RENDERERS={
    'Dashboard':dashboard.render,'Command Center':command_center.render,'Preferences':preferences.render,
    'Operations':operations.render,'Projects':projects.render,'Governance':governance.render,
    'Approvals':approvals.render,'System Check':system_check.render,'Provider Setup':provider_setup.render,
    'Voice Library':voice_library.render,'Quality Studio':quality_studio.render,
    'Audio Quality Lab':audio_quality_lab.render,'Timeline Studio':timeline_studio.render,
    'Script Blocks':script_blocks.render,'Batch Production':batch_production.render,
    'Create Speech':create_speech.render,'Transcription':transcription.render,
    'Render History':render_history.render,'Roadmap & Help':help.render,
}
def render_screen(page:str,ctx:AppContext)->None:
    renderer=SCREEN_RENDERERS.get(page)
    if renderer is None:raise KeyError(f'Unknown screen: {page}')
    renderer(ctx)
