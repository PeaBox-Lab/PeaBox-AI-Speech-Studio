# PeaBox Voice Studio v0.09.0
A local-first, corporate voice-production workspace with modular screens, project operations, governance, local/cloud speech generation, transcription, quality processing, resumable jobs, and portable timelines.

## v0.09.0 Modular Screen Architecture
- Shared `AppContext` for stable screen dependencies
- Central screen registry and renderer contract
- Dedicated modules for Executive Dashboard, Command Center, Interface Preferences, Operations Center, and Roadmap & Help
- Operations Center with project health, safe repair previews, repository rebuilds, maintenance plans, and event history
- Rebuildable SQLite project metadata index; JSON project files remain authoritative
- Architecture guards for registry uniqueness, renderer availability, context fields, and bootstrap size
- Cumulative reliability, governance, timeline, transcription, and provider functionality retained

## Validation
- 157 automated tests passed
- All Python sources compiled successfully
- Archive contents are verified against the source tree before delivery

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.09.0.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```