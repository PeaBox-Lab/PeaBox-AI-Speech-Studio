# Changelog

## v0.05.00 — 2026-11-05

### Added

- Durable project audio-clip records
- Cached normalized waveform peaks
- Source-block hashes and stale-render detection
- Missing-file and audio-format validation
- Clip track, order, enable, start-time, and gain controls
- Automatic sequential arrangement with configurable gaps
- Overlapping multitrack PCM mixing
- Merged WAV and timeline manifest export
- Timeline export history
- Timeline, mixing, stale-state, navigation, and UI regression tests

### Scope

- Timeline controls are form-based in Streamlit; drag-and-drop waveforms remain planned for the React/Web Audio phase

## v0.04.10 — 2026-11-05

### Added

- Audio Quality Lab for uncompressed 16-bit PCM WAV files
- Duration, channel, sample-rate, peak, RMS, clipping, and size metrics
- Non-destructive peak normalization
- Leading/trailing silence trimming with threshold and padding controls
- A/B Kokoro voice and speed comparisons
- Project comparison history, preference, notes, and deletion controls
- Audio processing, comparison, navigation, and UI regression tests

### Scope

- Processing is WAV-first; multitrack mixing and timeline editing remain planned for v0.05.00

## v0.04.01 — 2026-11-05

### Added

- System Check for Python, FFmpeg, storage, and Kokoro model readiness
- Media-format readiness checks before transcription
- Transcript overlap, duration, and empty-text validation
- Automatic sequential timing repair
- Saved transcript update and schema-v2 session support
- Pronunciation duplicate and overlap diagnostics
- Pronunciation match preview status
- Tests for diagnostics, timing repair, invalid-export blocking, and rule conflicts

### Changed

- Invalid transcript timing now blocks SRT/VTT export and project saving
- Older invalid transcript sessions are repaired when loaded

### Preserved

- v0.04.00 quality and transcription features
- v0.03.12 UI rendering regression protection

## v0.04.00 — 2026-11-05

### Added

- Project pronunciation dictionary with whole-word and case controls
- Safe pause markers and processed-text previews
- Cloud SSML break compilation and local Kokoro pause approximations
- Original and processed text snapshots in batch jobs
- Editable transcript segments with speaker fields and search
- TXT, SRT, and WebVTT exports
- Saved project transcript sessions
- Quality, transcript, cloud-SSML, migration, navigation, and UI regression tests

### Preserved

- v0.03.12 Streamlit navigation fix and visible version diagnostics
- v0.03.11 voice catalogs and presets
- v0.03.10 multi-provider resumable jobs

## v0.03.12 — 2026-11-05

### Fixed

- Replaced a conditional Streamlit UI expression that leaked a `DeltaGenerator` object into page content
- Restored the normal Projects interface and unobstructed sidebar navigation
- Added a visible sidebar version marker to identify stale running releases
- Added launcher output showing the exact release folder and version

### Added

- Regression tests for Streamlit magic-expression leaks
- Navigation structure tests covering all registered application pages
- Troubleshooting guidance for stopping older Streamlit processes and opening the correct local URL

## v0.03.11 — 2026-11-05

### Added

- Azure, Polly, and Google voice discovery
- Session-cached normalized voice catalogs
- Searchable cross-provider Voice Library and capability matrix
- Catalog-backed cloud voice selection in script blocks
- Reusable project voice/direction presets
- Job duplication, cancelled-item reopening, and job deletion
- Catalog, preset, normalization, and job-recovery tests

### Security

- Credentials and discovered catalogs remain session-only
- Presets store only non-secret generation settings

### Compatibility

- v0.03.10 projects and saved jobs remain readable

## v0.03.10 — 2026-11-05

### Added

- Session-only Azure Speech, Amazon Polly, and Google Cloud TTS profiles
- Provider-specific cloud voice and language identifiers
- Provider-readiness validation before job creation
- Persistent resumable batch jobs and per-item state
- Retry failed items and cancel queued work
- Job output ZIPs and a 20-job project history
- Estimated-versus-recorded usage cost tracking
- Tests covering jobs, retries, cancellation, job persistence, and credential exclusion

### Security

- API keys, AWS secrets, tokens, and Google service-account contents remain only in Streamlit session state
- Project exports and job records contain no credential values

### Limitation

- Jobs execute in the Streamlit process when the user runs them; a separate background worker is not yet included

## v0.03.01 — 2026-11-05

### Added

- Complete project JSON export and collision-safe import
- Append-or-replace paragraph import mode
- Block filtering and bulk enable/disable controls
- Batch-readiness validation with errors and warnings
- Schema-v2 render manifests with validation details
- Persistent last-batch summary and per-block results
- Tests for project portability, validation failures, bulk controls, and result summaries

### Fixed

- Empty enabled blocks are rejected before local generation
- Render results now retain block titles for easier diagnosis
- Project imports no longer risk overwriting an existing identity

### Compatibility

- Existing v0.03.00 raw project files remain readable
- Imported bundles accept both wrapped exports and raw project objects

## v0.03.00 — 2026-11-05

### Added

- Ordered Script Blocks workspace
- Per-block provider, language, voice, speed, direction notes, and batch inclusion
- Paragraph-to-block import, reordering, duplication, and deletion
- Batch Production dashboard with estimates and JSON manifest
- Kokoro local multi-block rendering and packaged batch download
- Migration-safe block schema and batch services
- Evidence-based roadmap derived from the supplied development plan
- Automated tests for block lifecycle, ordering, manifests, batch behavior, ZIP output, launcher, subtitles, and file safety

### Preserved

- Persistent projects and Master Script
- Single local Kokoro generation and render history
- Local Faster-Whisper transcription with TXT/SRT output
- Flexible Python 3.10–3.12 Windows launcher
