# v0.09.2 Help Update

No project migration or user action is required for v0.09.2. Existing project JSON files, timeline bundles, transcript sessions, batch jobs, governance records, and local preferences remain compatible.

# v0.09.1 Help Update

## Repository recovery
The SQLite project list is secondary. If it is missing or inconsistent, use **Operations Center → Repository → Rebuild project index**. The rebuild reads project JSON and does not replace it.

## Project repairs
Health repairs affect only explicitly previewed metadata problems. Missing audio cannot be recreated automatically; relink those assets in Timeline Studio.

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
