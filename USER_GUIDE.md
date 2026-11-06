# v0.09.2 User Guide Update

The interface and workflows are unchanged in this architecture-focused release. Project Workspace, Script Editor, speech generation, batch production, Timeline Studio, transcription, governance, approvals, Operations Center, and support screens remain in their existing navigation locations.

# v0.09.1 User Guide Update

## Operations Center
Open **Overview → Operations Center** to inspect project health, rebuild the metadata index, complete local maintenance plans, and review events. Repairs always appear as a preview and require explicit confirmation.

## Navigation behavior
All screens retain their existing names and workflows. The modular architecture changes internal ownership without changing project files or expected user actions.

# User Guide
## Preserve output history
PeaBox automatically creates numbered filenames when output names repeat. Existing files remain untouched.
## Move a project
- Use Project JSON for scripts, settings, governance, and metadata. Non-portable media paths are removed on import.
- Use a timeline bundle to move validated WAV assets with the project.
## Resolve timeline integrity warnings
- **Audio changed:** refresh metadata only after confirming the current file is correct.
- **Source stale:** regenerate or acknowledge the current script-block version after review.
- **File missing:** relink a replacement WAV.
## Monitor costs
Recorded planning-rate usage is an estimate based on successfully generated characters. It is not the provider invoice.
