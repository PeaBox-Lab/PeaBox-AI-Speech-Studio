# PeaBox Voice Studio v0.10.0
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, governance, multi-provider speech generation, transcription, audio quality tools, portable timelines, and an integrated operations recovery toolkit.

## v0.10.0 Operations Recovery Toolkit
- Storage inventory and category-level capacity summaries
- Unreferenced-output detection with reversible quarantine
- Quarantine restore with collision-safe destination naming
- SQLite integrity checks, local backups, transactional restore, and rollback preservation
- Project metadata snapshots with explicit media exclusion
- Sanitized support bundles excluding credentials, project text, transcripts, media, and absolute user paths
- Historical project schema fixture matrix and nested-reference portability tests
- Consolidated Operations Center tabs for health, repository, storage, backups, and support

## Validation
- 167 automated tests passed
- All Python sources compile successfully
- Recovery actions are confirmation-gated in the interface
- Invalid database backups are rejected before mutation
- All ZIP entries are verified byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.0.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
