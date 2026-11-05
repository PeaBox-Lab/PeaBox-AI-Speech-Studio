# PeaBox Voice Studio v0.02.02

PeaBox Voice Studio is a local-first Streamlit workspace for text-to-speech, transcription, persistent scripts, and render tracking. This release refactors the attached v0.2 prototype into a modular project structure while retaining Kokoro, Azure Speech, Amazon Polly, Google Cloud TTS, and Faster-Whisper support.

## What changed

- Persistent project workspace with create, open, edit, save, export, and protected delete
- Master Script connected to the speech-generation workflow
- Project-specific render history and saved provider settings
- Modular `providers`, `services`, configuration, and data models
- Atomic JSON/audio writes and safer filenames
- Script and upload size limits
- Correct SRT timestamps (`HH:MM:SS,mmm`)
- More actionable user-facing errors without displaying full exception traces
- Cost guide clearly marked as inherited and not web-refreshed
- Automated tests for projects, file safety, and subtitles

## Folder structure

```text
PeaBox_Voice_Studio_v0.02.02/
├── app.py
├── peabox_voice_studio/
│   ├── config.py
│   ├── models.py
│   ├── providers/
│   │   ├── catalog.py
│   │   ├── cloud.py
│   │   └── kokoro.py
│   └── services/
│       ├── files.py
│       ├── history.py
│       ├── projects.py
│       ├── subtitles.py
│       └── transcription.py
├── data/projects/
├── models/
├── outputs/
├── tests/
├── AUDIT.md
├── ROADMAP.md
├── CHANGELOG.md
├── requirements.txt
└── start_windows.bat
```

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12. The launcher prefers the newest compatible installed version.
2. Extract the ZIP.
3. Run `start_windows.bat`. It checks the Python Launcher, `python`, and `python3`, then creates or reuses `.venv`.
4. Install FFmpeg and add it to PATH for compressed audio/video transcription.

The launcher creates a local virtual environment, installs the declared dependencies, and starts Streamlit. It does not silently require Python 3.11 and does not attempt an unattended Python installation. If no compatible version is found, it shows the supported versions and exits without modifying the system.

## Security and privacy

- Cloud credentials remain in Streamlit session state and are not written to project JSON.
- Project filenames are generated from internal IDs rather than user-provided names.
- Keep `data/projects`, `outputs`, downloaded models, and credentials out of source control.
- Verify provider pricing and credential policies before production use.

## Tests

From the project folder:

```bash
python -m unittest discover -s tests -v
```

## Release naming

The requested release folder and package are named `PeaBox_Voice_Studio_v0.02.02`. The user-provided `v99.99.99` string is treated as a future naming placeholder rather than the current semantic release number.
