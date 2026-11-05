# PeaBox Voice Studio v0.05.01

A hardened local-first voice production workspace with portable timeline bundles, safe asset relinking, non-destructive PCM timeline mixing, WAV quality processing, transcription, pronunciation controls, cloud voice catalogs, and resumable jobs.

## v0.05.01 Timeline Hardening

### Portable timeline bundles

- Export project data and referenced WAV assets into one ZIP
- Use content hashes and controlled `audio/` archive names
- Import with a new project identity
- Extract WAV assets using collision-safe filenames
- Rewrite clip paths to the newly extracted local files
- Preserve unbundled missing clips as unlinked records for later recovery

### Bundle security

- Reject absolute paths and parent-directory traversal
- Reject Windows drive-style or backslash paths
- Reject symbolic links and encrypted members
- Enforce file-count and total-uncompressed-size limits
- Accept referenced timeline assets only when they are valid WAV files
- Never trust or restore the original machine's absolute paths

### Clip recovery

- Upload and relink a missing WAV
- Refresh waveform peaks, duration, sample rate, channels, and asset hash after a file changes
- Acknowledge a linked block's current source version after review
- Repair duplicate clip IDs and clamp invalid timing/gain values
- Optionally remove confirmed missing records
- Duplicate the current clip set for alternate sequencing experiments

## Preserved capabilities

- v0.05.00 Timeline Studio mixing, waveform peaks, stale detection, and merged WAV export
- v0.04.10 Audio Quality Lab and A/B comparisons
- Transcript validation, repair, and TXT/SRT/VTT exports
- Pronunciation rules and safe pause markers
- Cloud voice discovery, presets, and resumable jobs
- Streamlit UI regression protection

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `PeaBox v0.05.01`.
5. Use project JSON for lightweight backups or timeline bundles when WAV portability is required.

## Tests

```bash
python -m unittest discover -s tests -v
```
