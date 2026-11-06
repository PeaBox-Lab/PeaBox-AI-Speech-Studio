# PeaBox Voice Studio v0.09.3
A local-first corporate voice-production workspace with registry-driven screens, bounded production workflow APIs, project operations, governance, multi-provider speech generation, transcription, audio quality tools, resumable jobs, and portable timelines.

## v0.09.3 Production Service Facades
- Added bounded workflow facades for Timeline, Batch Production, and Transcription
- Complex screens no longer import their underlying service modules directly
- Facade exports are explicit, unique, callable, and parity-tested against the real services
- Facades contain no Streamlit dependency and remain reusable outside the UI
- Screen-to-service boundary violations fail automated tests
- All 19 navigation pages remain registry-driven
- Operations Center health, repair, and repository workflows remain cumulative

## Validation
- 145 automated tests passed
- All Python sources compile successfully
- All 19 navigation pages smoke-render without an active project
- Facade isolation and behavioral parity are verified
- Archive contents are checked byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.09.3.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
