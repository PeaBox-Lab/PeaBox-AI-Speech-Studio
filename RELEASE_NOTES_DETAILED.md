# PeaBox Voice Studio v0.10.2 Detailed Release Notes

## Project portfolio API
The portfolio facade owns project-store access, project JSON export, timeline-bundle import/export, paragraph-to-block conversion, favorite/recent resolution, preference persistence, deduplicated quick-access rows, and aggregate portfolio totals.

## Governance workflow API
The governance facade owns project governance state, settings, comments, decisions, transitions, approvals, readiness, summary metrics, pending-first approval queues, and cross-project governance rows.

## Screen isolation
Project Workspace cannot import the hidden projects, preferences, or bundle services directly. Governance Center and Approval Queue cannot import the governance implementation directly. Activity History and Portfolio Operations use the same public contract.

## Portfolio Operations
The cross-project view reports owner, workflow state, risk, open and blocking comments, pending and approved requests, readiness, and readiness issue count. KPIs show total projects, open reviews, pending approvals, unassigned projects, and generated storage.

## Cumulative operations
Database backup, metadata snapshots, local maintenance plans, and confirmation-gated retention previews remain available.

## Verification
143 tests cover cumulative services, all navigation smoke paths, facade parity, composed summaries, access-row deduplication, governance rows, pending-first approval queues, modular screen contracts, and recovery controls.

# Detailed Release Notes — v0.07.4
## Data integrity
The application previously reused deterministic filenames. A later render could replace an earlier asset while clip metadata still described the old audio. All generated outputs now use collision-safe numbered filenames, and timeline validation compares the current file hash with the registered hash.
## Migration
Project JSON exports now declare schema version 2. Import migrates missing structures, rejects future schemas, assigns a safe identity, repairs nested batch-job references, and removes absolute paths that are not portable.
## Runtime
Timeline mix buffers use compact numeric arrays and a sample limit. Kokoro and Whisper model instances are cached. Bundle payloads use lower safety limits.
## Billing language
Successful generation records planning-rate usage. It does not populate actual provider invoice cost, because provider billing and contract adjustments are not retrieved by this local application.
