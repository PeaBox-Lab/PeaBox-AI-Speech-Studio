# Backup and Recovery Guide

## Project snapshots

Snapshots are local JSON recovery points under `data/backups/<project-id>/`. They include scripts, settings, governance, jobs, timeline metadata, and transcript sessions, but they do not copy referenced audio files.

## Create a snapshot

1. Open a project.
2. Go to **Administration → Operations Center**.
3. Enter an optional label.
4. Select **Create project snapshot**.

PeaBox retains the most recent configured number of snapshots per project.

## Restore

- **Restore over active project** keeps the current project identity and replaces its JSON content.
- **Restore as new project** creates a new identity and preserves the current project.

## Audio recovery

Use portable timeline bundles for project-plus-WAV portability. Project snapshots and project JSON do not copy audio assets.
