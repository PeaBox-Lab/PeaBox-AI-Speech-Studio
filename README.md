# PeaBox Voice Studio v0.08.0

A local-first enterprise voice-production workspace with a rebuildable SQLite project index, project snapshots, structured operational logs, repository health, governed review, multi-provider speech, transcription, audio quality, portable timelines, and command-driven navigation.

## v0.08.0 Operations & Repository Foundation

- SQLite metadata index while JSON remains portable source-of-truth
- Automatic index updates on project save/list/delete
- One-click project-index rebuild
- Repository integrity and schema health
- Project snapshots with retention
- Restore over active project or restore as a new project
- Structured JSONL operational events with rotation
- Downloadable operation log
- Operations Center dashboard and indexed project catalog

## Recovery model

- **Project JSON:** portable project metadata and settings
- **Timeline bundle:** portable project plus WAV assets
- **Project snapshot:** local JSON recovery point
- **SQLite index:** disposable, rebuildable local catalog
- **Operation log:** local support and troubleshooting evidence

## Cumulative capabilities

The release retains v0.07.4 integrity hardening, Command Center, onboarding, preferences, corporate UI, governance and approvals, cloud/local speech, transcription, audio quality, resumable jobs, Timeline Studio, secure bundles, and all cumulative documentation.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `Enterprise workspace · v0.08.0`.
5. Open **Administration → Operations Center** to verify repository health.

## Validation

```bash
python -m unittest discover -s tests -v
```
