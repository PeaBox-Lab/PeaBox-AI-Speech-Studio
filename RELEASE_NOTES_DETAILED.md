# PeaBox Voice Studio v0.09.0 Detailed Release Notes

## Architecture
`AppContext` defines the stable dependencies available to modular screens. `SCREEN_RENDERERS` maps navigation identities to callable renderers. The bootstrap initializes services, resolves navigation, and dispatches registered screens while existing production screens continue to operate unchanged.

## Modular screens
Executive Dashboard, Command Center, Interface Preferences, Operations Center, and Roadmap & Help now live in dedicated modules. This isolates feature ownership, makes screen-level testing practical, and prevents further growth of the monolithic bootstrap.

## Operations Center
The Operations Center reports project health, previews deterministic safe repairs, requires confirmation before mutation, rebuilds the secondary SQLite index, records local maintenance-plan completions, and displays structured operational events.

## Compatibility and validation
Project JSON remains authoritative and portable. Existing schema migration, file locks, collision-safe outputs, timeline integrity checks, transactional bundle imports, bounded audio mixing, governance, provider, transcription, and quality workflows remain available. 157 automated tests passed.

# Detailed Release Notes — v0.07.4
## Data integrity
The application previously reused deterministic filenames. A later render could replace an earlier asset while clip metadata still described the old audio. All generated outputs now use collision-safe numbered filenames, and timeline validation compares the current file hash with the registered hash.
## Migration
Project JSON exports now declare schema version 2. Import migrates missing structures, rejects future schemas, assigns a safe identity, repairs nested batch-job references, and removes absolute paths that are not portable.
## Runtime
Timeline mix buffers use compact numeric arrays and a sample limit. Kokoro and Whisper model instances are cached. Bundle payloads use lower safety limits.
## Billing language
Successful generation records planning-rate usage. It does not populate actual provider invoice cost, because provider billing and contract adjustments are not retrieved by this local application.