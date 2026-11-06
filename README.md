# PeaBox Voice Studio v0.08.1

A local-first enterprise voice-production workspace with Operations Center maintenance, reversible storage cleanup, database backup and restore, sanitized support bundles, project snapshots, a rebuildable SQLite index, governance, multi-provider generation, transcription, audio quality, and portable timelines.

## v0.08.1 Operations Maintenance

- Storage inventory by area, file count, and bytes
- Referenced, orphaned, and missing output analysis
- Preview-first reversible quarantine
- Quarantine restore and confirmed permanent deletion
- SQLite backup with collision-safe names and retention
- Database restore with integrity validation and WAL cleanup
- SQLite optimization
- Sanitized downloadable support bundle
- Dedicated maintenance and support documentation

## Safety model

Cleanup is non-destructive by default. Files move to quarantine and can be restored. Permanent deletion requires an explicit checkbox. Project JSON remains source-of-truth; the SQLite index is rebuildable.

## Cumulative capabilities

The release retains v0.08.0 Operations Center and snapshots, v0.07.4 integrity controls, corporate navigation, Command Center, preferences, governance and approvals, local/cloud speech, transcription, quality controls, resumable jobs, Timeline Studio, secure bundles, and complete activity history.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `Enterprise workspace · v0.08.1`.
5. Open **Administration → Operations Center** for health and maintenance.

## Validation

```bash
python -m unittest discover -s tests -v
```
