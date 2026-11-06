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
