# v0.10.3 Additions and Improvements

## Worker architecture
- Durable local queue
- Separate Kokoro worker process
- Exclusive leases and heartbeat
- Stale-worker recovery
- Append-only progress events

## Batch Production
- Queue for local worker
- Live progress bar
- Recent event table
- Cancel queued worker job
- Recover stale leases
- Sync results into project

## Security
- Cloud jobs rejected from persistent queue
- No session credentials stored in worker files

# v0.10.2 Additions and Improvements

## New workflow APIs
- Project portfolio facade
- Governance and approvals facade
- Portfolio summary and quick-access composition
- Cross-project governance readiness rows
- Pending-first approval queue

## Operations
- Consolidated portfolio KPI view
- Ownership and risk visibility
- Review and approval totals
- Readiness status by project
- Cumulative recovery and maintenance controls

# v0.07.4 Additions and Improvements
## Integrity
- Collision-safe output naming
- Asset content-hash validation
- Atomic model downloads and local checksum verification
- Project write locks
## Portability
- Project schema 2
- Migration registry
- Nested project-reference rewrite
- Absolute-path cleanup
- Transactional bundle imports
## Runtime
- Cached model instances
- Compact timeline buffers
- Timeline sample limit
- Reduced bundle limits
## UX and release
- Sanitized errors
- Honest cost terminology
- Updated launcher version
- Direct dependency constraints
