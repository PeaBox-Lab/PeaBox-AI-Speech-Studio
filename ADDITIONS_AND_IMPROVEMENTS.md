# v0.08.0 Additions and Improvements

## Repository
- SQLite metadata catalog
- WAL mode and integrity checks
- Project indexing and rebuild
- JSON remains source-of-truth

## Recovery
- Project snapshots
- Snapshot retention
- Restore in place or as new project
- Collision-safe snapshot names

## Operations
- Structured JSONL event logging
- Log rotation and health
- Operations Center metrics and event view

## Architecture
- Secondary repository layer separated from project persistence
- Standard-library SQLite with no new external dependency
- Isolated repository paths for tests
