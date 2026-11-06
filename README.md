# PeaBox Voice Studio v0.09.1
A local-first corporate voice-production workspace with a fully registry-driven interface, project operations, governance, local and cloud speech generation, transcription, audio quality workflows, resumable jobs, and portable timelines.

## v0.09.1 Full Screen Modularization
- All 19 navigation pages render through dedicated screen modules
- The application bootstrap is reduced to 31 lines of initialization and dispatch
- Shared `AppContext` carries runtime state and service callbacks
- Central registry guarantees one renderer per navigation identity
- Screen modules cannot import the application bootstrap
- Operations Center includes health checks, confirmed repair plans, repository rebuilds, maintenance plans, and event history
- JSON project files remain authoritative; SQLite remains disposable and rebuildable

## Validation
- 165 automated tests passed
- Every navigation page smoke-renders without an active project
- All Python sources compile successfully
- Archive entries are verified byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.09.1.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
