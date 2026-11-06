# v0.10.7 Help Update

- **Memory backend:** temporary validation only; never treat it as durable storage.
- **Migration conflict:** the target already contains that key; use a different destination or an explicit overwrite workflow.
- **Unknown backend:** only local and memory are built in.
- **Remote storage:** not configured; no remote credentials are accepted or stored in this release.

# v0.10.6 Help Update

- **Invalid object key:** use letters, numbers, underscores, periods, and hyphens in relative path segments.
- **Manifest issue:** rebuild the manifest, then audit again.
- **Hash changed:** the file changed outside the object API; inspect before rebuilding.
- **Object exists:** choose a new key or deliberately use an overwrite-capable API.
- **Remote storage:** not configured in this release; all namespaces remain local.

# v0.10.5 Help Update

- **Quota exceeded:** free managed storage or increase the category limit.
- **Unexpected reserved space:** release stale reservations in Capacity.
- **Models blocked:** increase Downloaded models capacity before first Kokoro use.
- **Backup blocked:** free recovery space or increase Backups and recovery capacity.
- **Project save:** authoritative project JSON is not governed by these quotas.

# v0.10.4 Help Update

- **Daemon already active:** use `--status`; do not start a second process.
- **Daemon shown as stale:** start the daemon again; stale ownership can be reclaimed.
- **Paused:** use `--resume` or the Batch Jobs control.
- **Draining:** the worker stops after eligible queued work is complete.
- **Foreground terminal closed unexpectedly:** recover stale job leases in Batch Jobs and restart the daemon.

# v0.10.3 Help Update

- **No queued jobs:** create and queue a Kokoro local batch first.
- **Cloud job rejected:** cloud credentials are session-only; use inline Run/resume.
- **Worker interrupted:** click Recover stale leases, then run the worker again.
- **Project not updated:** click Sync worker progress after the worker finishes.
- **Queue leased:** another worker owns the job until its lease expires or is released.

# v0.10.2 Help Update

Portfolio Operations is a local summary derived from project JSON. It does not authenticate owners or reviewers. Approval records remain local attestations rather than digital signatures. Project data and export formats remain compatible.

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
