import json
from pathlib import Path
import streamlit as st
from peabox_voice_studio.config import APP_NAME, MAX_BLOCK_CHARS, MAX_SCRIPT_CHARS, MAX_UPLOAD_BYTES, OUTPUTS_DIR, VERSION
from peabox_voice_studio.models import Project, ScriptBlock
from peabox_voice_studio.providers.catalog import KOKORO_LANGS, KOKORO_VOICES, PROVIDER_RATES
from peabox_voice_studio.services.audio import inspect_wav, normalize_wav, save_processed_wav, trim_silence_wav
from peabox_voice_studio.services.batch import build_manifest
from peabox_voice_studio.services.commands import onboarding_status, record_command, resolve_commands, search_commands
from peabox_voice_studio.services.comparisons import create_comparison_record, delete_comparison, set_comparison_preference
from peabox_voice_studio.services.bundles import export_timeline_bundle, import_timeline_bundle
from peabox_voice_studio.services.files import atomic_write_bytes, build_render_zip, safe_filename, user_safe_error
from peabox_voice_studio.services.governance import ALLOWED_TRANSITIONS, APPROVAL_STATES, RISK_LEVELS, WORKFLOW_STATES, add_comment, add_decision, decide_approval, governance, governance_readiness, governance_summary, reopen_comment, request_approval, resolve_comment, supersede_decision, transition_status, update_project_governance
from peabox_voice_studio.services.history import record_render
from peabox_voice_studio.services.catalogs import capability_rows, catalog_facets, filter_voices
from peabox_voice_studio.services.jobs import add_job, create_job, delete_job, duplicate_job, reopen_cancelled, replace_job, request_cancel, retry_failed, run_job
from peabox_voice_studio.services.preferences import load_preferences, mark_project_opened, resolve_projects, save_preferences, toggle_favorite
from peabox_voice_studio.services.presets import apply_preset, create_preset, delete_preset, list_presets
from peabox_voice_studio.services.projects import ProjectStore, export_project, move_block, set_all_blocks_enabled, split_script_into_blocks
from peabox_voice_studio.services.diagnostics import system_diagnostics, transcription_readiness
from peabox_voice_studio.services.quality import add_pronunciation, delete_pronunciation, insert_pause, list_pronunciations, prepare_text, pronunciation_conflicts, pronunciation_preview, validate_pause_markers
from peabox_voice_studio.services.timeline import acknowledge_clip_source, add_clip, arrange_sequential, cleanup_invalid_clips, clip_status, duplicate_timeline, list_clips, mix_timeline, move_clip, refresh_clip, relink_clip, remove_clip, timeline_manifest, validate_timeline
from peabox_voice_studio.services.transcripts import delete_transcript_session, export_transcript_bundle, filter_segments, normalize_segments, repair_segment_timing, save_transcript_session, update_transcript_session, validate_segments
from peabox_voice_studio.services.subtitles import to_srt, to_vtt
from peabox_voice_studio.ui import callout, empty_state, inject_corporate_theme, kpi_card, navigate_to, page_header, section, sidebar_navigation, status_badge, workflow_step
