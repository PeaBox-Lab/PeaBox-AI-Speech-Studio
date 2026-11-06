# Help Articles

## The repository health check fails

Choose **Rebuild project index**. JSON project files remain the source-of-truth. If integrity still fails, close PeaBox, back up `data/projects`, delete `data/peabox.db`, and restart.

## A project is missing from the index

Open Project Workspace once or rebuild the index. Project JSON remains available even if it is not indexed.

## I need to undo a major change

Restore a project snapshot. Use restore-as-copy when you want to preserve the current version.

## My restored snapshot has missing audio

Snapshots do not copy audio. Relink the WAV file or restore/import a portable timeline bundle.

## Operation logs are large

PeaBox rotates the log automatically. Download it for support before removing old rotated files.
