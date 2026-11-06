# PeaBox Voice Studio v0.08.1 Release Notes

This maintenance release expands Operations Center with storage analysis, reversible cleanup, database recovery, and support diagnostics.

PeaBox identifies output files that are referenced, orphaned, or missing. Orphaned files can be moved into quarantine and later restored. Permanent quarantine deletion requires explicit confirmation.

SQLite backups are collision-safe, retained to a configured count, integrity-checked before restore, and restored with stale WAL/SHM cleanup. A sanitized support bundle packages operational metadata without scripts, credentials, transcripts, or audio.
