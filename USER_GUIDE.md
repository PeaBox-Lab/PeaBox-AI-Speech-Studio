# v0.09.0 User Guide Update

## Operations Center
Open **Overview → Operations Center** to review project health, repository status, maintenance plans, and operational events. Repairs are previewed first and require explicit confirmation. Rebuilding the project index does not replace or modify project JSON files.

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