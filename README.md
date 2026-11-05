# PeaBox Voice Studio v0.03.00

A local-first Streamlit workspace for project-based voice production, multi-block scripts, Kokoro batch rendering, and Faster-Whisper transcription.

## v0.03.00 highlights

- Convert the Master Script into ordered paragraph blocks
- Assign provider, language, voice, speed, direction notes, and enabled state per block
- Add, edit, reorder, duplicate, disable, and delete blocks
- Produce live block-level and batch-level character, duration, and inherited cost estimates
- Export a portable JSON render manifest
- Render enabled Kokoro blocks and download audio plus manifest as one ZIP
- Preserve projects and blocks in migration-safe JSON
- Retain local transcription, TXT/SRT export, render history, resource limits, and flexible Python 3.10–3.12 startup

## Important scope boundary

The attached research describes a long-term React/FastAPI digital audio workstation, cloud aggregation, cloning, diarization, provenance, and consent architecture. This release deliberately implements the production model that can be delivered safely in the current local application: script blocks and local batch rendering. Cloud batch jobs, cloning, diarization, watermarking, and legal compliance enforcement remain roadmap items until their dependencies and authoritative requirements are validated.

## Windows

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP.
3. Run `start_windows.bat`.
4. Install FFmpeg and add it to PATH for compressed audio/video transcription.

The launcher selects the newest compatible installed Python, creates or reuses `.venv`, installs dependencies, and starts Streamlit.

## Workflow

1. Create or open a project.
2. Write a Master Script.
3. Create blocks from blank paragraphs or add them manually.
4. Configure each block and save.
5. Open Batch Production to review totals and download a manifest.
6. Render enabled Kokoro local blocks and download the batch ZIP.

## Tests

```bash
python -m unittest discover -s tests -v
```
