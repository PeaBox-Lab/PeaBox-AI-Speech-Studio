# Detailed Release Notes — v0.08.1

## Non-destructive cleanup

The release intentionally avoids direct orphan deletion. Quarantine batches retain a manifest with original paths, byte sizes, and SHA-256 hashes.

## Database recovery

SQLite backup uses the database backup API rather than copying a live file. Restore validates the backup, stages a restored database, validates it again, removes stale sidecars, and then replaces the live index.

## Support bundle boundary

Support bundles contain metadata and diagnostics only. They are designed for troubleshooting without disclosing voice content or provider secrets.
