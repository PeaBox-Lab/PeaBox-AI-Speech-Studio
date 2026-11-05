# PeaBox Voice Studio v0.03.01

A local-first Streamlit workspace for portable projects, multi-block scripts, validated Kokoro batch rendering, and Faster-Whisper transcription.

## v0.03.01 highlights

- Export a complete project—including Master Script, blocks, settings, and history—as JSON
- Import project JSON with a new collision-safe project identity
- Choose whether Master Script paragraph import appends blocks or replaces existing blocks
- Filter blocks by title, text, provider, voice, or direction notes
- Enable or disable all blocks in one action
- Validate batch readiness before rendering
- Block local rendering when enabled blocks have empty text or other errors
- Identify cloud blocks as warnings because the local renderer will skip them
- Save the last batch result summary and per-block outcomes in the project
- Upgrade render manifests to schema version 2 with validation details

## Compatibility

Existing v0.03.00 project JSON files remain readable. Newly exported project bundles use a wrapper with `schema_version`, `exported_at`, and `project`; the importer also accepts a raw project object.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP.
3. Run `start_windows.bat`.
4. Install FFmpeg and add it to PATH for compressed audio/video transcription.

The launcher selects the newest compatible installed Python, creates or reuses `.venv`, installs dependencies, and starts Streamlit.

## Recommended workflow

1. Create or import a project.
2. Maintain the Master Script and export the project JSON as a backup.
3. Create or edit script blocks; use filtering and bulk enable/disable for larger projects.
4. Open Batch Production and resolve validation errors.
5. Download the schema-v2 manifest, render enabled Kokoro blocks, and download the batch ZIP.
6. Review the persistent last-batch result before retrying failed work.

## Tests

```bash
python -m unittest discover -s tests -v
```
