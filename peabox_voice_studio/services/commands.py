from typing import Any
COMMANDS = [
    {"id": "open-dashboard", "label": "Open Executive Dashboard", "page": "Dashboard", "group": "Overview", "keywords": "overview status kpi readiness home"},
    {"id": "manage-projects", "label": "Open Project Workspace", "page": "Projects", "group": "Overview", "keywords": "project create open import export favorite recent"},
    {"id": "interface-preferences", "label": "Open Interface Preferences", "page": "Preferences", "group": "Overview", "keywords": "settings compact motion dashboard startup personalize"},
    {"id": "edit-script", "label": "Edit Script Blocks", "page": "Script Blocks", "group": "Production", "keywords": "script block text dialogue provider voice"},
    {"id": "generate-speech", "label": "Generate Speech", "page": "Create Speech", "group": "Production", "keywords": "tts kokoro narration wav speech"},
    {"id": "batch-jobs", "label": "Open Batch Jobs", "page": "Batch Production", "group": "Production", "keywords": "batch queue retry cancel cloud cost"},
    {"id": "timeline", "label": "Open Timeline Studio", "page": "Timeline Studio", "group": "Production", "keywords": "timeline clips mix wav export assemble"},
    {"id": "voice-library", "label": "Search Voice Library", "page": "Voice Library", "group": "Audio & Quality", "keywords": "voices provider language catalog preset"},
    {"id": "quality", "label": "Open Quality Studio", "page": "Quality Studio", "group": "Audio & Quality", "keywords": "pronunciation pauses ssml dictionary"},
    {"id": "audio-lab", "label": "Open Audio Quality Lab", "page": "Audio Quality Lab", "group": "Audio & Quality", "keywords": "normalize trim silence compare metrics wav"},
    {"id": "transcription", "label": "Open Transcription Studio", "page": "Transcription", "group": "Audio & Quality", "keywords": "stt whisper subtitles srt vtt transcript"},
    {"id": "governance", "label": "Open Governance Center", "page": "Governance", "group": "Administration", "keywords": "owner risk review comments decisions workflow"},
    {"id": "approvals", "label": "Open Approval Queue", "page": "Approvals", "group": "Administration", "keywords": "approve reject attestation reviewer"},
    {"id": "providers", "label": "Configure Providers", "page": "Provider Setup", "group": "Administration", "keywords": "azure aws polly google credentials api"},
    {"id": "system-check", "label": "Run System Check", "page": "System Check", "group": "Administration", "keywords": "python ffmpeg model storage diagnostics"},
    {"id": "activity", "label": "Open Activity & History", "page": "Render History", "group": "Administration", "keywords": "history audit renders jobs transcripts exports"},
    {"id": "help", "label": "Open Roadmap & Help", "page": "Roadmap & Help", "group": "Support", "keywords": "help roadmap guide documentation next"},
]
def search_commands(query: str, project_active: bool = False) -> list[dict[str, Any]]:
    query = query.strip().lower()
    results = []
    for command in COMMANDS:
        haystack = " ".join(str(command.get(key, "")) for key in ("label", "page", "group", "keywords")).lower()
        if query and all(token not in haystack for token in query.split()):
            continue
        item = dict(command)
        item["project_active"] = project_active
        item["requires_project"] = command["page"] in {"Script Blocks", "Batch Production", "Timeline Studio", "Governance", "Approvals", "Render History"}
        item["available"] = project_active or not item["requires_project"]
        results.append(item)
    return results
def record_command(preferences: dict, command_id: str, limit: int = 10) -> dict:
    recent = [item for item in preferences.get("recent_command_ids", []) if item != command_id]
    preferences["recent_command_ids"] = ([command_id] + recent)[:limit]
    return preferences
def resolve_commands(command_ids: list[str]) -> list[dict]:
    mapping = {command["id"]: command for command in COMMANDS}
    return [mapping[command_id] for command_id in command_ids if command_id in mapping]
def onboarding_status(project: Any = None, providers_ready: int = 1) -> dict:
    steps = [
        {"id": "project", "label": "Create or open a project", "complete": project is not None, "page": "Projects"},
        {"id": "script", "label": "Add master script or script blocks", "complete": bool(project and (project.script.strip() or project.blocks)), "page": "Script Blocks"},
        {"id": "provider", "label": "Confirm a generation provider", "complete": providers_ready > 0, "page": "Provider Setup"},
        {"id": "render", "label": "Generate the first audio output", "complete": bool(project and project.render_history), "page": "Create Speech"},
        {"id": "timeline", "label": "Add audio to the timeline", "complete": bool(project and project.settings.get("audio_clips")), "page": "Timeline Studio"},
    ]
    completed = sum(step["complete"] for step in steps)
    return {"steps": steps, "completed": completed, "total": len(steps), "percent": round(completed / len(steps) * 100)}
