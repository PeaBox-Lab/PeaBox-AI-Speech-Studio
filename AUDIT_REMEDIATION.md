# v0.07.4 Audit Remediation

## Critical and high-priority fixes

- Generated WAV and MP3 files now use collision-safe numbered paths instead of silently overwriting existing outputs.
- Timeline clips verify current file content against the stored SHA-256 asset hash; altered files are no longer reported as ready.
- Project imports migrate schema, assign a new identity, rewrite nested job project IDs, and remove non-portable absolute output paths.
- Timeline bundle imports validate and stage every asset before commit, with rollback if commit fails.
- Timeline mixing uses a compact float array and enforces a maximum sample count.

## Reliability and security improvements

- Project JSON saves use a local lock file to reduce concurrent lost updates.
- Kokoro model downloads are atomic, have a minimum-size check, and create SHA-256 sidecars for subsequent integrity verification.
- Kokoro and Faster-Whisper model instances are cached and reused.
- Unknown exceptions are converted to generic user-safe messages rather than exposing arbitrary upstream bodies.
- Bundle compressed and uncompressed size limits are reduced and enforced on import/export.

## Release consistency

- Windows launcher version updated to v0.07.4.
- Installer uses top-level version constraints through `constraints.txt`.
- Cost tracking distinguishes recorded planning-rate usage from an actual provider invoice.
- Project export schema advanced to version 2 with migration tests.
