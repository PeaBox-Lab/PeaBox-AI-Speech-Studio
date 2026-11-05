# Changelog

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
