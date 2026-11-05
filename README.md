# PeaBox Voice Studio v0.03.12

A local-first Streamlit workspace for discoverable multi-provider voices, reusable voice presets, resumable production jobs, Kokoro generation, and Faster-Whisper transcription.

## v0.03.12 critical UI fix

- Fixed internal `DeltaGenerator` documentation replacing the normal project screen
- Restored unobstructed sidebar navigation and page content
- Added a visible sidebar version marker
- Added launcher output identifying the exact version and folder being started
- Added regression tests for Streamlit expression leaks and every navigation page

## Preserved v0.03.11 features

- Discover Azure, Amazon Polly, and Google voices from configured session profiles
- Cache normalized cloud voice catalogs only for the current Streamlit session
- Search the combined Kokoro and cloud catalog by name, ID, provider, language, or gender
- Filter the library by language and gender
- View provider readiness, cached voice counts, output types, supported controls, and credential requirements
- Select cached provider voices directly while editing cloud script blocks
- Save reusable project presets containing provider, language, voice, speed, and direction notes
- Apply or delete project presets without changing block text
- Duplicate jobs as clean queued copies
- Reopen cancelled job items, delete obsolete jobs, retry failures, and cancel queued work

## Credential and catalog safety

Cloud credentials and discovered voice catalogs exist only in Streamlit session state. They are not saved in project JSON, project exports, manifests, presets, or job history. Presets contain only non-secret generation choices.

A saved cloud job can be reopened later, but the provider must be configured again for the new session before it can run.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP.
3. Run `start_windows.bat`.
4. Install FFmpeg and add it to PATH for compressed audio/video transcription.

## Recommended workflow

1. Configure the required provider for the current session.
2. Discover its voices and inspect them in Voice Library.
3. Assign catalog voices to script blocks.
4. Save frequently used combinations as project presets.
5. Validate and create a resumable batch job.
6. Run, retry, cancel, reopen, duplicate, clean up, or download job results.

## Tests

```bash
python -m unittest discover -s tests -v
```


See `TROUBLESHOOTING.md` if an older process or browser tab is still showing the broken screen.
