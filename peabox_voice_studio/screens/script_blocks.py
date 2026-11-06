from peabox_voice_studio.context import AppContext
import streamlit as st
from peabox_voice_studio.config import MAX_BLOCK_CHARS
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.providers.catalog import KOKORO_VOICES
from peabox_voice_studio.services.presets import apply_preset, create_preset, list_presets
from peabox_voice_studio.services.projects import move_block, set_all_blocks_enabled, split_script_into_blocks
from peabox_voice_studio.services.quality import insert_pause, prepare_text, validate_pause_markers
from peabox_voice_studio.ui import empty_state, section

def block_editor(ctx: AppContext, project: Project, index: int, block: ScriptBlock) -> None:
    save_project=ctx.save_project; voice_catalogs=ctx.voice_catalogs
    label = f"{index + 1:02}. {block.title} · {len(block.text):,} chars · {block.provider}"
    with st.expander(label, expanded=st.session_state.get("expand_block") == block.id):
        block.enabled = st.checkbox("Include in batch", block.enabled, key=f"enabled_{block.id}")
        block.title = st.text_input("Block title", block.title, key=f"title_{block.id}")
        block.text = st.text_area("Text", block.text, height=180, max_chars=MAX_BLOCK_CHARS, key=f"text_{block.id}")
        a, b, c, d = st.columns(4)
        providers = ["Kokoro local", "Azure Speech", "Amazon Polly standard", "Amazon Polly neural", "Google Cloud TTS"]
        block.provider = a.selectbox("Provider", providers, index=providers.index(block.provider) if block.provider in providers else 0, key=f"provider_{block.id}")
        if block.provider == "Kokoro local":
            block.language = b.selectbox("Language", list(KOKORO_VOICES), index=list(KOKORO_VOICES).index(block.language) if block.language in KOKORO_VOICES else 0, key=f"lang_{block.id}")
            voices = KOKORO_VOICES[block.language]
            block.voice = c.selectbox("Voice", voices, index=voices.index(block.voice) if block.voice in voices else 0, key=f"voice_{block.id}")
        else:
            provider_voices = voice_catalogs.get(block.provider, [])
            if provider_voices:
                language_options = sorted({item["language"] for item in provider_voices if item.get("language")})
                current_language = block.language if block.language in language_options else (language_options[0] if language_options else "")
                block.language = b.selectbox("Language code", language_options or [current_language], index=(language_options or [current_language]).index(current_language), key=f"lang_{block.id}")
                matching = [item for item in provider_voices if not block.language or item.get("language") == block.language]
                voice_ids = [item["id"] for item in matching]
                current_voice = block.voice if block.voice in voice_ids else (voice_ids[0] if voice_ids else block.voice)
                block.voice = c.selectbox("Provider voice", voice_ids or [current_voice], index=(voice_ids or [current_voice]).index(current_voice), key=f"voice_{block.id}")
            else:
                default_language = block.language if block.language not in KOKORO_VOICES else "en-US"
                block.language = b.text_input("Language code", default_language, key=f"lang_{block.id}")
                default_voice = block.voice if block.voice not in sum(KOKORO_VOICES.values(), []) else ""
                block.voice = c.text_input("Provider voice ID", default_voice, key=f"voice_{block.id}")
        block.speed = d.slider("Speed", 0.6, 1.6, float(block.speed), 0.05, key=f"speed_{block.id}")
        block.notes = st.text_input("Direction notes", block.notes, placeholder="Optional pacing, pronunciation, or performance note", key=f"notes_{block.id}")
        pause_seconds = st.slider("Pause marker seconds", 0.1, 5.0, 1.0, 0.1, key=f"pause_seconds_{block.id}")
        if st.button("Append pause marker", key=f"append_pause_{block.id}"):
            block.text = insert_pause(block.text, pause_seconds); save_project(project); st.rerun()
        pause_issues = validate_pause_markers(block.text)
        if pause_issues:
            st.error("; ".join(pause_issues))
        with st.expander("Processed text preview"):
            st.code(prepare_text(block.text, project, block.provider))
        presets = list_presets(project)
        if presets:
            preset = st.selectbox("Apply project preset", [None] + presets, format_func=lambda item: "Choose a preset" if item is None else item["name"], key=f"preset_{block.id}")
            if st.button("Apply selected preset", key=f"apply_preset_{block.id}", disabled=preset is None):
                apply_preset(block, preset); save_project(project); st.rerun()
        preset_name = st.text_input("Save current settings as preset", key=f"preset_name_{block.id}")
        if st.button("Save preset", key=f"save_preset_{block.id}", disabled=not preset_name.strip()):
            create_preset(project, preset_name, block); save_project(project); st.success("Preset saved")
        u, dn, dup, delete = st.columns(4)
        if u.button("Move up", key=f"up_{block.id}", disabled=index == 0):
            move_block(project.blocks, index, -1); save_project(project); st.rerun()
        if dn.button("Move down", key=f"down_{block.id}", disabled=index == len(project.blocks) - 1):
            move_block(project.blocks, index, 1); save_project(project); st.rerun()
        if dup.button("Duplicate", key=f"dup_{block.id}"):
            project.blocks.insert(index + 1, ScriptBlock(title=f"{block.title} copy", text=block.text, provider=block.provider, language=block.language, voice=block.voice, speed=block.speed, notes=block.notes)); save_project(project); st.rerun()
        if delete.button("Delete", key=f"delete_{block.id}"):
            project.blocks.pop(index); save_project(project); st.rerun()

def render(ctx: AppContext) -> None:
    project=ctx.project; save_project=ctx.save_project
    section("Structured script production", "Each block carries independent provider, voice, pacing, pronunciation, and inclusion settings.")
    if not project:
        empty_state("No active project", "Open or create a project before editing script blocks.", "Open Project Workspace", "Projects")
    else:
        st.caption("Divide a script into independently configurable voice blocks. Reorder, duplicate, disable, and batch-plan without changing the Master Script.")
        a, b, c, d, e = st.columns(5)
        if a.button("Add blank block", type="primary"):
            project.blocks.append(ScriptBlock(title=f"Block {len(project.blocks)+1}")); save_project(project); st.rerun()
        if b.button("Import paragraphs", disabled=not project.script.strip()):
            project.blocks.extend(split_script_into_blocks(project.script)); save_project(project); st.rerun()
        if c.button("Enable all", disabled=not project.blocks):
            set_all_blocks_enabled(project.blocks, True); save_project(project); st.rerun()
        if d.button("Disable all", disabled=not project.blocks):
            set_all_blocks_enabled(project.blocks, False); save_project(project); st.rerun()
        if e.button("Save all", disabled=not project.blocks): save_project(project); st.success("Blocks saved")
        filter_text = st.text_input("Filter blocks", placeholder="Title, text, provider, or voice").strip().lower()
        visible = [(index, block) for index, block in enumerate(project.blocks) if not filter_text or filter_text in " ".join([block.title, block.text, block.provider, block.voice, block.notes]).lower()]
        if not project.blocks: st.info("Add a block or import paragraphs from the Master Script.")
        elif not visible: st.info("No blocks match the filter.")
        for index, block in visible: block_editor(ctx, project, index, block)
