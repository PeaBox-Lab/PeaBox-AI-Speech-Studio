# Detailed Release Notes — v0.07.4

## Data integrity

The application previously reused deterministic filenames. A later render could replace an earlier asset while clip metadata still described the old audio. All generated outputs now use collision-safe numbered filenames, and timeline validation compares the current file hash with the registered hash.

## Migration

Project JSON exports now declare schema version 2. Import migrates missing structures, rejects future schemas, assigns a safe identity, repairs nested batch-job references, and removes absolute paths that are not portable.

## Runtime

Timeline mix buffers use compact numeric arrays and a sample limit. Kokoro and Whisper model instances are cached. Bundle payloads use lower safety limits.

## Billing language

Successful generation records planning-rate usage. It does not populate actual provider invoice cost, because provider billing and contract adjustments are not retrieved by this local application.
