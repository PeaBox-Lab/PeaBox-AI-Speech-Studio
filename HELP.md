# v0.10.1 Help Update

- Maintenance plans are reminders and evidence records inside the application, not scheduled background jobs.
- Retention previews are read-only.
- Applying retention is permanent for the displayed backup, restored-record, and support-artifact candidates.
- Authoritative project JSON, active outputs, and models are excluded from retention cleanup.

# v0.10.0 Help Update

- **Quarantine is not deletion:** files can be restored unless their quarantine copy is manually removed.
- **SQLite is secondary:** database backup and restore affects the project index, not authoritative project JSON.
- **Snapshots exclude media:** use timeline bundles for projects that must travel with WAV assets.
- **Support bundles are sanitized:** review the included JSON before sharing if your organization requires additional controls.

# v0.09.4 Help Update

If upgrading from v0.09.2 or v0.09.3, replace the extracted application folder with v0.09.4. Existing project JSON, timeline bundles, transcript sessions, batch jobs, and preferences remain compatible. The release specifically resolves blank-looking Quick Access controls and navigation exceptions.

# v0.09.3 Help Update

No project conversion is required. Existing project JSON, timeline bundles, batch jobs, transcript sessions, governance records, and preferences remain compatible with v0.09.3.

# Help Articles
## A timeline clip says the audio changed
The WAV content no longer matches the hash recorded when the clip was added. Review the file, then use Refresh Audio Metadata or relink the intended WAV.
## My output filename has `_2` or another number
PeaBox preserves existing output files. When a filename already exists, it creates a numbered filename instead of overwriting it.
## An imported job needs to be rerun
Direct project JSON does not carry media files. Rendered output paths are cleared during import and affected items are marked for rerun. Use a portable timeline bundle when WAV portability is required.
## A large timeline cannot be mixed
The in-memory safety limit prevents the application from exhausting system memory. Shorten the timeline, export sections, or wait for the future worker/streaming mixer architecture.
## A Kokoro integrity check fails
Delete the named model and its `.sha256` sidecar, then generate again to download a fresh copy.
