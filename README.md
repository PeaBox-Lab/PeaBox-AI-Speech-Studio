# PeaBox Voice Studio v0.09.2
A local-first corporate voice-production workspace with a fully modular interface, explicit screen dependencies, project operations, governance, local and cloud speech generation, transcription, audio quality workflows, resumable jobs, and portable timelines.

## v0.09.2 Explicit Screen Dependencies
- Removed the shared wildcard dependency module
- Each of the 19 screen modules imports only the services and UI components it uses
- Screen-to-screen and screen-to-application imports are prohibited
- Per-screen dependency budget is capped at 25 imported names
- Unused imports and wildcard imports fail automated validation
- The 31-line bootstrap and complete registry dispatch remain unchanged
- All cumulative operations, governance, production, audio, and transcription workflows remain available

## Validation
- 170 automated tests passed
- All 19 screens smoke-render without an active project
- Every imported screen dependency is verified as used
- All Python sources compile successfully
- Archive entries are verified byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.09.2.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
