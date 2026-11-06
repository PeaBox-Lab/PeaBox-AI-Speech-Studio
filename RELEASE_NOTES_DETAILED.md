# Detailed Release Notes — v0.08.0

## Why a secondary repository

JSON remains transparent and portable, but portfolio queries and operational checks should not require repeatedly scanning every project file. SQLite supplies a local rebuildable index without changing project ownership or portability.

## Recovery boundaries

Snapshots copy project state only. They intentionally avoid duplicating potentially large audio media. Timeline bundles remain the media-inclusive transfer format.

## Failure behavior

A repository-index error does not invalidate a completed JSON save. Operations Center can rebuild the index from project files.
