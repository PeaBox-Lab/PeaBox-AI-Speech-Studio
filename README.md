# PeaBox Voice Studio v0.04.01

A hardened local-first multi-provider voice production and transcription workspace with system diagnostics, transcript timing validation and repair, pronunciation conflict checks, safe pause controls, reusable presets, and resumable jobs.

## v0.04.01 highlights

### System Check

- Reports the running Python version and supported range
- Detects whether FFmpeg is available
- Checks project and output storage write access
- Shows whether Kokoro model and voice files are ready or will download on first use
- Explains which compressed media formats require FFmpeg

### Transcript safety

- Detects overlapping segments
- Detects zero-duration or reversed timing
- Warns about empty segment text
- Blocks SRT/VTT export and project saving while timing errors remain
- Automatically repairs overlaps and minimum duration
- Safely repairs older invalid sessions when they are loaded
- Supports updating an existing saved transcript session
- Saves new sessions with schema version 2 and an updated timestamp

### Quality-rule diagnostics

- Detects duplicate pronunciation rules
- Identifies overlapping rule sources where rule order can change output
- Shows whether pronunciation rules changed preview text
- Preserves the existing safe pause-marker workflow

### Preserved

- v0.04.00 Quality and Transcription Studio
- v0.03.12 UI rendering fix and navigation smoke tests
- Session-cached provider voice catalogs and presets
- Resumable cloud and local production jobs
- Portable project import and export

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat` from that folder.
4. Open **System Check** after startup.
5. Install FFmpeg and add it to PATH if compressed audio/video transcription is required.

The sidebar must display `PeaBox v0.04.01`.

## Tests

```bash
python -m unittest discover -s tests -v
```
