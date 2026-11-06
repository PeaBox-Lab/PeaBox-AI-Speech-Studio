# PeaBox Voice Studio v0.10.1 Detailed Release Notes

## Maintenance plans
Users can create Daily, Weekly, Monthly, or Quarterly plans with standard operational tasks. Plans track due or overdue status, may be paused and resumed, and retain completion timestamps, per-task results, and notes. Plans are evaluated locally when Operations Center opens; this release does not install a background scheduler or operating-system task.

## Retention previews
Retention policy inputs control the number of database backups retained and the age thresholds for restored quarantine records and generated support artifacts. The preview lists every candidate, reason, size, total file count, and reclaimable bytes without changing the file system.

## Safe cleanup boundary
Retention application requires explicit confirmation. It processes only the exact preview candidates and only when their resolved paths remain inside the backups, quarantine, or support directories. Missing files and paths outside those roots are skipped and reported. Project JSON, active outputs, models, and arbitrary files are outside the retention boundary.

## Compatibility
Recovery backups, quarantine records, support bundles, project files, workflow facades, navigation, providers, timelines, transcripts, governance, and approvals remain cumulative.

## Verification
178 tests cover maintenance plan lifecycle, due calculations, completion history, pause/resume, persistence, preview immutability, backup retention, restored-record retention, support retention, exact-candidate deletion, outside-root rejection, and interface confirmation gates.

# PeaBox Voice Studio v0.10.0 Detailed Release Notes

## Storage inventory and quarantine
Operations Center summarizes files and bytes by category and detects generated output files that are not referenced by current project records. Selected output files can be moved into quarantine only after confirmation. Quarantine records include origin, reason, size, timestamp, and SHA-256. Restore is reversible and collision-safe.

## Database backup and restore
The secondary SQLite project index can be integrity-checked and backed up with SQLite’s backup mechanism. Restore validates the selected backup first, preserves the current database as a rollback copy, writes through a temporary file, and atomically replaces the index. Project JSON remains authoritative.

## Metadata snapshots
An active project can be downloaded as a metadata snapshot containing project JSON and a manifest with version, creation time, project identity, hash, and an explicit `includes_media: false` marker. Timeline bundles remain the media-inclusive portability format.

## Sanitized support bundles
Support bundles include diagnostics, repository status, aggregate storage evidence, file extensions and sizes, and minimal event identities. They exclude credentials, project text, transcript content, media content, and absolute user paths.

## Migration matrix
Fixtures now cover legacy schema migration, current schema stability, rejection of unsupported future schemas, nested job identity repair, removal of non-portable paths, and explicit asset-path preservation mode.

## Verification
167 tests cover cumulative functionality, quarantine safety, reversible restore, corrupt database rejection, rollback creation, support redaction, metadata snapshots, migration compatibility, and Operations Center confirmation controls.

# PeaBox Voice Studio v0.09.4 Detailed Release Notes

## Sidebar contrast
The Dashboard, Script, Generate, and Timeline Quick Access buttons previously inherited light-page button styling, producing pale text on near-white boxes. Sidebar buttons now use an explicit dark-blue background, white text, visible border, and defined hover, focus, and disabled states.

## Safe navigation lifecycle
Streamlit prevents a widget-owned session key from being changed after the widget is created in the same run. `navigate_to()` now writes only a neutral pending destination. On the next rerun, `sidebar_navigation()` resolves that destination and sets the navigation widget defaults before either widget is instantiated.

## Project Workspace context
The modular Projects screen retained a call to the old app-local `current_project()` helper. It now reads `ctx.project`, matching the renderer contract used by all modular screens.

## Compatibility
Project data, workflow facades, navigation labels, governance, approvals, timelines, batch jobs, transcription sessions, exports, and provider behavior remain unchanged.

## Verification
151 tests cover cumulative features plus explicit sidebar contrast selectors, deferred navigation ordering, widget-key isolation, context-based Project Workspace state, page smoke execution, and facade boundaries.

# PeaBox Voice Studio v0.09.3 Detailed Release Notes

## Workflow facades
Timeline Studio consumes one timeline workflow API covering clip management, validation, mixing, and portable bundles. Batch Production consumes one job workflow API covering validation, job lifecycle, retries, cancellation, and execution. Transcription Studio consumes one transcript workflow API covering readiness, editing, timing repair, sessions, and exports.

## Boundary enforcement
The three screens are prohibited from importing their hidden service modules directly. Facades explicitly list their public exports, contain no Streamlit code, and cannot rely on screen implementations.

## Behavioral parity
Tests verify that every facade export exists, is callable, is unique, and resolves to the established service implementation. This ensures the new boundary changes architecture rather than runtime behavior.

## Compatibility
Project JSON, migrations, providers, voice settings, batch jobs, timeline clips, transcript sessions, governance records, approvals, render history, and exports retain their cumulative formats and behavior.

## Verification
145 tests cover cumulative service behavior, navigation smoke execution, modular screens, facade isolation, public export contracts, behavioral parity, project health, and repository rebuilding.

# Detailed Release Notes — v0.07.4
## Data integrity
The application previously reused deterministic filenames. A later render could replace an earlier asset while clip metadata still described the old audio. All generated outputs now use collision-safe numbered filenames, and timeline validation compares the current file hash with the registered hash.
## Migration
Project JSON exports now declare schema version 2. Import migrates missing structures, rejects future schemas, assigns a safe identity, repairs nested batch-job references, and removes absolute paths that are not portable.
## Runtime
Timeline mix buffers use compact numeric arrays and a sample limit. Kokoro and Whisper model instances are cached. Bundle payloads use lower safety limits.
## Billing language
Successful generation records planning-rate usage. It does not populate actual provider invoice cost, because provider billing and contract adjustments are not retrieved by this local application.
