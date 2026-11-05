# PeaBox Voice Studio v0.05.00

A local-first multi-provider voice production studio with durable audio clips, cached waveform peaks, non-destructive timeline arrangement, overlapping PCM mixing, merged WAV export, transcription, pronunciation controls, quality processing, and resumable jobs.

## v0.05.00 Timeline Studio

### Durable audio clips

- Add existing WAV assets from the release output folder
- Link a clip to an optional script block
- Store title, track, start time, duration, gain, sample rate, channels, waveform peaks, source block ID, and source hash
- Keep clip records inside portable project JSON
- Detect missing audio files
- Detect stale clips when a linked script block changes after rendering

### Non-destructive arrangement

- Reorder clip records without changing source files
- Assign track names
- Set explicit start offsets
- Enable or disable clips
- Apply per-clip gain from -60 to +12 dB
- Automatically arrange enabled clips sequentially with a configurable gap
- Preview individual clips and cached waveform peak charts

### Mix and export

- Mix overlapping enabled clips at their explicit start times
- Validate sample rate and channel compatibility before export
- Report potential clipped samples before final limiting
- Export one uncompressed 16-bit PCM WAV
- Export a timeline manifest containing order, timing, gain, track, source linkage, and readiness state
- Retain the latest 20 timeline export records per project

## Scope boundary

Timeline Studio currently works with uncompressed **16-bit PCM WAV** files that share the same sample rate and channel count. It offers form-based timeline controls in Streamlit; direct waveform dragging and browser-based low-latency playback remain planned for a later React/Web Audio frontend.

## Preserved capabilities

- v0.04.10 WAV analysis, normalization, silence trimming, and A/B comparison
- v0.04.01 system and transcript diagnostics
- Pronunciation dictionaries, safe pause markers, and transcript sessions
- Cloud voice catalogs, project presets, and resumable multi-provider jobs
- v0.03.12 interface regression protection

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `PeaBox v0.05.00`.
5. Generate or process WAV files, then add them in Timeline Studio.

## Tests

```bash
python -m unittest discover -s tests -v
```
