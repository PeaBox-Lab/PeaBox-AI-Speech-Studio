# PeaBox Voice Studio v0.07.4

A reliability-hardened, governed, corporate voice-production workspace with collision-safe outputs, asset integrity verification, project migrations, transactional bundle imports, bounded audio mixing, command discovery, multi-provider generation, transcription, quality processing, portable timelines, and local review workflows.

## v0.07.4 Reliability & Integrity

- Collision-safe generated WAV, MP3, processed WAV, and timeline output names
- Live timeline asset SHA-256 verification
- Project schema version 2 and legacy migration
- Imported nested job-ID repair and non-portable path cleanup
- Transactional timeline bundle staging and rollback
- Local project write locks
- Bounded timeline mixing with compact float buffers
- Atomic Kokoro downloads, minimum-size validation, and checksum sidecars
- Cached Kokoro and Faster-Whisper model instances
- Sanitized user-facing errors
- Honest recorded planning-rate usage separate from actual invoice cost
- Correct v0.07.4 launcher banner and constrained direct dependencies

## Cumulative capabilities

The release retains Command Center, onboarding, preferences, corporate navigation, governance, approvals, projects, script blocks, cloud/local providers, voice discovery, quality controls, transcription, resumable jobs, Audio Quality Lab, Timeline Studio, secure bundles, and activity history.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.07.4.
5. Keep the `data`, `outputs`, and `models` folders writable.

## Validation

```bash
python -m unittest discover -s tests -v
```
