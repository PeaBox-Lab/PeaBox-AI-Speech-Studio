# PeaBox Voice Studio v0.04.00

A local-first multi-provider voice production and transcription workspace with project pronunciation rules, safe pause controls, editable transcripts, resumable jobs, reusable voice presets, and session-only cloud credentials.

## v0.04.00 highlights

### Quality Studio

- Project pronunciation dictionary with case-sensitive and whole-word matching
- Rule ordering preserved in project JSON and exports
- Safe `[[pause:seconds]]` markers limited to 0.1–10 seconds
- Pause markers compile to SSML breaks for Azure, Polly, and Google
- Kokoro receives a punctuation-based local pause approximation
- Processed-text previews before generation
- Resumable jobs snapshot both original and processed text for repeatability

### Transcription Studio

- Editable timestamped transcript segments
- Optional speaker labels
- Search across transcript text and speakers
- TXT, standards-compatible SRT, and WebVTT export
- Save, reload, and delete project transcript sessions
- Up to 20 transcript sessions retained per project

### Preserved

- Corrected v0.03.12 navigation and Streamlit rendering behavior
- Session-cached provider voice discovery and Voice Library
- Project voice presets
- Resumable cloud and local jobs with retry, cancellation, reopen, duplicate, delete, and downloads
- Portable project JSON import/export

## Pause syntax

Use a marker such as:

```text
Welcome to PeaBox. [[pause:1.5]] Let us begin.
```

Malformed or out-of-range pause markers are reported before use.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat` from that folder.
4. Install FFmpeg and add it to PATH for compressed media transcription.

The sidebar must display `PeaBox v0.04.00`. If it shows an older version, stop older Streamlit terminals and use the Local URL printed by the new launcher.

## Tests

```bash
python -m unittest discover -s tests -v
```
