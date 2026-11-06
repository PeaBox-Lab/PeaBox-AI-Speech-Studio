# PeaBox Voice Studio v0.09.1 Detailed Release Notes

## Complete screen extraction
All 19 user-facing navigation pages now live in dedicated modules: dashboard, projects, command center, preferences, operations, governance, approvals, diagnostics, provider setup, voice library, quality, audio lab, timeline, script blocks, batch production, speech generation, transcription, history, and help.

## Application contract
`AppContext` supplies project state, preferences, provider profiles, discovered voice catalogs, configured-provider resolution, and project lifecycle callbacks. `SCREEN_RENDERERS` is the single dispatch map and rejects unknown destinations. Screen modules never import the application bootstrap.

## Operations and recovery
The Operations Center provides project health reports, preview-only repair plans, confirmation-gated repairs, a rebuildable SQLite project index, local maintenance plans, and structured event history. Project JSON remains the source of truth.

## Compatibility
The release retains project schema migration, collision-safe output naming, project file locks, asset hashes, transactional bundle import, bounded timeline mixing, cached models, sanitized errors, governance, approvals, multi-provider speech, editable transcription, quality processing, and portable timeline bundles.

## Verification
165 tests cover cumulative functionality, full registry coverage, renderer contracts, module boundaries, page smoke execution, operations services, project health, repair behavior, maintenance plans, and repository rebuilding.

# Detailed Release Notes — v0.07.4
## Data integrity
The application previously reused deterministic filenames. A later render could replace an earlier asset while clip metadata still described the old audio. All generated outputs now use collision-safe numbered filenames, and timeline validation compares the current file hash with the registered hash.
## Migration
Project JSON exports now declare schema version 2. Import migrates missing structures, rejects future schemas, assigns a safe identity, repairs nested batch-job references, and removes absolute paths that are not portable.
## Runtime
Timeline mix buffers use compact numeric arrays and a sample limit. Kokoro and Whisper model instances are cached. Bundle payloads use lower safety limits.
## Billing language
Successful generation records planning-rate usage. It does not populate actual provider invoice cost, because provider billing and contract adjustments are not retrieved by this local application.
