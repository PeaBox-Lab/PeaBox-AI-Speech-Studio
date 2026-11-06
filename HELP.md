# Help Articles

## What is an orphaned output?

It is a file in the output folder that no current project record references. It may still be valuable, so PeaBox quarantines rather than deleting it immediately.

## A valid file is marked orphaned

Ensure the project referencing it is present and readable, then rebuild the index and reload Operations Center. References use current project JSON, not only the SQLite index.

## Database restore does not restore a project

The database is a metadata index. Restore project content from a project snapshot, project JSON, or timeline bundle.

## Support bundle privacy

The bundle excludes credentials, project scripts, transcripts, and audio. Operational event details and project counts are included.
