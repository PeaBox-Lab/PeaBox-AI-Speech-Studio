# PeaBox Voice Studio v0.04.10

A local-first voice production, transcription, and WAV quality workspace with non-destructive audio processing, A/B Kokoro comparisons, project pronunciation rules, session-cached cloud voices, and resumable multi-provider jobs.

## v0.04.10 Audio Quality Lab

### WAV analysis

For uncompressed 16-bit PCM WAV files, the app reports:

- Duration
- Sample rate
- Channel count
- Frame count
- Peak level in dBFS
- RMS level in dBFS
- Clipped-sample count
- File size

### Non-destructive processing

- Create a normalized copy with a target peak from -30 to 0 dBFS
- Trim leading and trailing silence using a configurable threshold
- Preserve configurable padding around detected audio
- Preview, compare metrics, and download the processed WAV
- Save processed copies into the release output folder without overwriting the source

### A/B Kokoro comparisons

- Generate identical prepared text with two independent language, voice, and speed settings
- Play and download both WAV files
- Compare duration, peak, RMS, and clipping metrics
- Save comparison records in the active project
- Record A, B, Tie, or no preference with review notes
- Keep the latest 20 comparison records per project

## Scope boundary

The Audio Quality Lab supports uncompressed **16-bit PCM WAV** processing. Cloud MP3 output should be converted to WAV before using normalization or silence trimming. This release is not yet a multitrack editor and does not merge tracks.

## Preserved capabilities

- v0.04.01 system and media diagnostics
- Transcript validation, repair, TXT/SRT/VTT export, and saved sessions
- Pronunciation rules and safe pause markers
- Cloud provider catalogs, presets, and resumable jobs
- v0.03.12 UI regression protection

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `PeaBox v0.04.10`.
5. Use **System Check** to verify FFmpeg and storage readiness.

## Tests

```bash
python -m unittest discover -s tests -v
```
