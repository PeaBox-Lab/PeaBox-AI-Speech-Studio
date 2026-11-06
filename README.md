# PeaBox Voice Studio v0.10.1
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, governance, multi-provider speech generation, transcription, audio quality tools, portable timelines, recovery controls, and local maintenance planning.

## v0.10.1 Maintenance & Retention
- Local Daily, Weekly, Monthly, and Quarterly maintenance plans
- Due, overdue, paused, and completion status tracking
- Durable completion history with task results and notes
- Preview-only retention policies for excess database backups, old restored-quarantine records, and generated support artifacts
- Exact candidate counts and reclaimable-byte totals before cleanup
- Explicit confirmation before retention is applied
- Safe-root enforcement prevents retention from touching projects, outputs, models, or arbitrary files
- Operations Center consolidation with a dedicated Maintenance tab

## Validation
- 178 automated tests passed
- Retention preview never mutates files
- Cleanup removes only exact preview candidates inside approved recovery directories
- Plans are local checklists evaluated when Operations Center opens; no background scheduler is implied
- All archive entries are verified byte-for-byte against the source tree

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.1.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
