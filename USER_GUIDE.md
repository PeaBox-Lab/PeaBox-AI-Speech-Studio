# v0.10.0 User Guide Update

## Storage
Open **Overview → Operations Center → Storage** to review category totals and unreferenced outputs. Quarantine requires confirmation and can be reversed from the same tab.

## Backups
Use **Backups** to create a recovery point for the rebuildable SQLite index. A restore requires confirmation, validates the backup, and retains the previous index as a rollback copy.

## Support
Use **Support** to download a sanitized ZIP. It excludes credentials, project text, transcripts, audio content, and absolute user paths.

## Project snapshots
Download a metadata snapshot from **Project health**. It does not contain external audio; use a timeline bundle when media portability is required.

# v0.09.4 User Guide Update

Use Dashboard, Script, Generate, and Timeline under **Quick Access** as before. The controls now have readable labels. Dashboard and Command Center actions may briefly rerun the interface while applying the destination safely; this is expected.

# v0.09.3 User Guide Update

This architecture release does not change user actions. Timeline Studio, Batch Jobs, and Transcription Studio remain in the same navigation locations and retain their existing controls, saved data, exports, and recovery behavior.

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
