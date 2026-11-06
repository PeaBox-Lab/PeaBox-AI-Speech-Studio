# Operations Center Guide

## Repository index

PeaBox continues to store each project as portable JSON. `data/peabox.db` is a local SQLite metadata index used for faster portfolio and health views. If the database is deleted or damaged, open Operations Center and choose **Rebuild project index**.

The index stores project identity, name, dates, governance status, risk, and counts for blocks, clips, jobs, and transcript sessions. It does not store cloud credentials.

## Structured operation log

`data/operations.jsonl` records project save/delete, repository rebuild, snapshot create/restore/delete, and index warnings. The log rotates when it exceeds the configured size. It can be downloaded from Operations Center.

## Health checks

Operations Center shows:

- SQLite integrity result
- Repository schema version
- Indexed project count
- Database size
- Operation-event count and log size
- Snapshot count for the active project
