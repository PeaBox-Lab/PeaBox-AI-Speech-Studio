# v0.11.2 Additions and Improvements

## Capture readiness
- Expected filename and dimension validation
- Missing, invalid, and extra capture detection
- Baseline and candidate readiness summaries

## Pixel reports
- Changed pixels and percentage
- Per-channel threshold
- Allowed changed percentage
- Maximum and mean deltas
- Baseline and candidate hashes
- Highlighted diff images

## Delivery
- JSON report
- ZIP report and diff bundle
- CLI exit codes
- Visual QA controls

# v0.11.1 Additions and Improvements

## Baselines
- Navigation snapshot
- Page metadata snapshot
- Theme tokens and components
- Screen labels and widget-call counts
- Source hashes

## Visual contracts
- Sidebar control styling
- Reusable component selectors
- Mobile breakpoint
- Contrast ratios

## Capture planning
- Desktop viewport
- Tablet viewport
- Mobile viewport
- 57 unique PNG targets

## Tooling
- Baseline generator
- Validation gate
- Drift comparison
- Operations Center Visual QA

# v0.11.0 Additions and Improvements

## Profile governance
- Draft creation
- Review submission
- Changes Requested
- Approval
- Activation
- Deactivation
- Archive and reactivation

## Controls
- Creator/reviewer separation
- Single Active profile per backend
- Draft-only deletion
- Draft/changes-only editing
- Clone and compare
- Audit history
- Active profile health probe

# v0.10.9 Additions and Improvements

## Offline sandboxes
- Azure Speech
- Amazon Polly standard
- Amazon Polly neural
- Google Cloud TTS

## Contract validation
- Voice normalization
- Required catalog fields
- SSML structure
- Pause markers
- XML escaping
- Speed and engine mapping
- Deterministic audio fixtures

## Failure and safety
- Discovery failure injection
- Synthesis failure injection
- No network clients
- No real credentials
- No billing

# v0.10.8 Additions and Improvements

## Retry
- Bounded attempts
- Retryable exception policy
- Initial delay and backoff
- Retry metrics

## Timeout
- Per-operation timeout
- Dedicated timeout error
- Timeout metrics

## Circuit breaker
- Closed/open/half-open states
- Failure threshold
- Cooldown
- Single probe
- Automatic reset on success

## Observability
- Call and success counts
- Failure and retry counts
- Average latency
- Last operation and error
- Health reports

# v0.10.7 Additions and Improvements

## Backend contract
- Put and get
- Exists and delete
- List
- Copy and move
- Audit

## Built-in backends
- Local durable backend
- In-memory validation backend

## Migration
- Namespace filtering
- File and byte preview
- Hash verification
- Conflict and failure reporting

## Registry
- Named factories
- Unknown-backend rejection
- Contract type validation

# v0.10.6 Additions and Improvements

## Object API
- Safe logical keys
- Six managed namespaces
- Put, get, import, copy, move, and delete
- Register and unregister

## Integrity
- SHA-256 verification
- Durable metadata manifest
- Rebuild from local storage
- Missing, size, and hash drift audit

## Migration
- Read-only preview
- File and byte totals
- Verified copy or move application
- Per-item failure reporting

# v0.10.5 Additions and Improvements

## Quota categories
- Generated outputs
- Downloaded models
- Backups, quarantine, and support artifacts
- Worker queue, events, and daemon state

## Controls
- Enable or disable quotas
- Warning threshold
- Per-category MB limits
- Live used, reserved, remaining, and percent values
- Capacity reservations and release

## Enforcement
- Atomic write preflight
- Kokoro WAV preflight
- Backup preflight
- Quarantine preflight
- Overwrite growth calculation

# v0.10.4 Additions and Improvements

## Daemon lifecycle
- Foreground daemon mode
- Single-daemon claim
- Durable heartbeat and status
- Stale takeover
- Graceful release

## Controls
- Status
- Pause
- Resume
- Drain
- Shutdown

## Launching
- Dedicated Windows worker launcher
- Reuses existing virtual environment
- No silent service installation

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
