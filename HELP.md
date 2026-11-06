# v0.11.2 Help Update

- **Exit 2:** capture set is incomplete, invalid, contains extras, or has wrong dimensions.
- **Exit 1:** valid images differ beyond the selected threshold.
- **Antialiasing noise:** use a reviewed channel threshold or changed-pixel allowance; do not hide meaningful layout changes.
- **No screenshots:** use an approved browser runner; PeaBox does not generate browser PNGs itself.
- **Diff ZIP:** contains the JSON report and available highlighted diff images.

# v0.11.1 Help Update

- **Baseline validation failed:** inspect the listed theme, component, breakpoint, or contrast contract.
- **Checked-in baseline differs:** review navigation/theme/screen changes before regenerating.
- **No PNG files:** this release creates the capture manifest; use an approved browser runner for screenshots.
- **Contrast issue:** ensure explicit foreground and background styles exist for the affected control.

# v0.11.0 Help Update

- **Approval rejected:** reviewer label must differ from creator.
- **Cannot edit:** clone the Approved/Active profile, or request changes before editing.
- **Previous Active changed to Approved:** only one profile per backend can be Active.
- **Cannot delete:** only Draft profiles can be deleted.
- **Actor labels:** local labels, not authenticated identities.

# v0.10.9 Help Update

- **Sandbox passed, live failed:** check credentials, region, permissions, quota, billing, network, and provider status.
- **Sandbox discovery failure:** inspect normalized fixture and provider contract code.
- **Sandbox synthesis failure:** inspect SSML, voice, language, speed, and engine fields.
- **No charges:** sandbox tests never call a live provider.

# v0.10.8 Help Update

- **Circuit open:** wait for the recovery duration before the half-open probe.
- **Timeout:** increase the runtime probe timeout only after checking backend health.
- **Retries exhausted:** inspect the last error and backend audit.
- **Memory backend:** non-persistent validation only.
- **Remote backend:** not configured in this release.

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
