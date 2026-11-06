# PeaBox Voice Studio v0.09.4
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, project operations, governance, multi-provider speech generation, transcription, audio quality tools, resumable jobs, and portable timelines.

## v0.09.4 UI & Navigation Reliability
- Fixed four low-contrast Quick Access buttons in the sidebar
- Added explicit readable styles for normal, hover, focus, and disabled sidebar button states
- Replaced unsafe same-run navigation-key mutation with deferred navigation applied before widget creation
- Fixed Project Workspace `current_project` NameError after modular extraction
- Preserved all 19 registry-driven screens and three bounded production facades
- Added screenshot-driven UI, navigation lifecycle, and modular dependency regression tests

## Validation
- 151 automated tests passed
- All Python sources compile successfully
- Every navigation page smoke-renders without an active project
- Project Workspace and programmatic navigation regressions are explicitly covered
- Archive contents are verified byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.09.4.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
