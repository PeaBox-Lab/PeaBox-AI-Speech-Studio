# Recovery Guide

## Source of truth
Project JSON files remain authoritative. The SQLite database is a rebuildable metadata index.

## Quarantine
Only generated files under the output directory can be quarantined. Each action creates a JSON record and stores a content hash. Restore returns the file to its original location or uses a collision-safe restored name.

## Database restore
A selected backup must pass SQLite integrity validation. Before replacement, the current database is copied to the backups directory as a rollback artifact. Replacement uses a temporary file and atomic rename.

## Project snapshots
Snapshots contain project metadata and a manifest. They intentionally omit external media.

## Support bundles
Support bundles contain sanitized operational evidence only. Credentials, project text, transcripts, media, and absolute user paths are excluded.
