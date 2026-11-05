# Changelog

## v0.02.01 — 2026-11-05

### Added

- Persistent project workspace with create, open, save, rename, export, and protected delete
- Master Script with character, word, and estimated-duration metrics
- Project-linked render history and provider settings
- Modular provider and service packages
- Atomic file writes, upload limits, and project path validation
- Standards-compatible SRT formatting
- Automated unit tests
- Code audit and staged roadmap

### Changed

- Replaced single-file provider/service implementation with separated modules
- Replaced full UI exception display with concise contextual errors
- Marked inherited cost values as unrefreshed planning estimates
- Connected generated audio back to the active project

### Preserved

- Kokoro local TTS
- Azure Speech, Amazon Polly, and Google Cloud TTS
- Faster-Whisper transcription
- Windows launcher and Python 3.11 guidance
