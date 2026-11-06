# PeaBox Voice Studio v0.11.1 Detailed Release Notes

## Navigation baseline
The baseline records all navigation groups, labels, internal page identities, icons, and page metadata. It verifies 19 unique pages and exact metadata coverage.

## Theme baseline
Theme extraction records corporate color tokens, required reusable component selectors, sidebar select/radio/button contracts, and responsive media queries. Validation requires the mobile breakpoint and key visual components.

## Screen source snapshots
Each modular screen records module name, source line count, unique labels, Streamlit call counts, and SHA-256 source hash. This catches structural UI changes without executing a browser.

## Contrast
The harness calculates relative-luminance contrast ratios. Sidebar white text against the dark control and primary ink against white cards must meet 4.5:1. During implementation, the check detected missing explicit Quick Access contrast styling and the rule was restored.

## Screenshot manifest
Every page is paired with desktop 1440×1000, tablet 1024×900, and mobile 390×844 capture targets. The manifest contains 57 unique PNG filenames linked to the baseline hash.

## Drift comparison
Baseline comparison separately identifies navigation, theme, and per-screen changes. The generator refuses to write artifacts when visual contracts fail.

## Operations interface
Visual QA reports page count, screen-module count, planned captures, contract issues, baseline hash, contrast values, and viewport names, with downloadable baseline and manifest JSON.

## Browser boundary
This release produces screenshot-ready deterministic baselines and manifests. Actual PNG capture and pixel comparison remain an external browser-runner step; no browser was silently installed.

## Verification
261 tests cover navigation uniqueness, theme contracts, contrast, screen coverage, determinism, round-trip serialization, drift detection, manifest uniqueness, checked-in artifact parity, generator gates, and interface disclosures.

# PeaBox Voice Studio v0.11.0 Detailed Release Notes

## Durable profile contents
Profiles persist backend name, retry attempts, delay, backoff, operation timeout, circuit failure threshold, recovery duration, description, creator, reviewer, review note, timestamps, status, and history. Credentials, endpoints, and object content are excluded.

## Lifecycle
Draft profiles can be edited or submitted for review. Review can approve or request changes. Changes Requested can return to Draft or review. Approved profiles may be activated. Active profiles may return to Approved or be archived. Archived profiles may return to Draft.

## Separation and activation
The approving reviewer label must differ from the creator label. Activating a profile automatically deactivates another Active profile for the same backend by returning it to Approved. This preserves one effective profile per backend.

## Change control
Only Draft and Changes Requested profiles can be edited. Profile updates retain before/after settings. Profiles can be cloned to a new Draft and compared against the current Active profile. Only Draft profiles can be deleted.

## Audit
Create, update, transition, activation replacement, and deletion actions append local audit records containing timestamp, actor label, action, profile identity, and transition details. Labels remain local and unauthenticated.

## Runtime use
Only an Active profile can instantiate a resilient backend. The profile is validated again and converted into RetryPolicy, CircuitBreaker, timeout, and ResilientBackend objects. The UI can run a health probe using the Active profile.

## Verification
247 tests cover bounds, persistence, edit restrictions, reviewer separation, transition rules, single-active enforcement, changes round trip, cloning, deletion, diffs, audit, Active requirements, instantiation, and UI controls.

# PeaBox Voice Studio v0.10.9 Detailed Release Notes

## Azure sandbox
Normalizes Azure-style voice records and validates the Azure SSML envelope, escaped voice name, percentage speed mapping, pause compilation, XML escaping, output format, and deterministic audio fixture.

## Polly sandbox
Normalizes standard and neural Polly voice fixtures separately, retains engine selection, validates SSML input, and returns deterministic MP3-like bytes.

## Google sandbox
Normalizes object-style Google voice responses, including multiple languages and enum-like gender values, validates language/voice selection fields, and returns deterministic fixture bytes.

## Contract runner
Each provider is tested for non-empty normalized catalogs, required voice fields, successful synthesis, compiled pause markers, escaped text, and valid fixture prefix. Results include provider, pass/fail, issues, voice count, audio fixture bytes, and sanitized call report.

## Failure injection
Discovery and synthesis failures can be triggered deterministically to verify user-facing failure paths without relying on provider outages.

## Security and cost boundary
The sandbox records only profile field names, not values. It does not import requests, boto3, or Google Cloud clients during contract execution. It makes no live calls and creates no provider billing.

## Limitations
Passing sandbox contracts does not confirm live credentials, account permissions, quotas, billing configuration, regional voice availability, network access, or current provider service status.

## Verification
232 tests cover every provider, normalization, SSML, speed, language, engine, deterministic bytes, input validation, injected failures, sanitized evidence, zero-network imports, call counts, and Provider Setup disclosures.

# PeaBox Voice Studio v0.10.8 Detailed Release Notes

## Retry policy
Retries are limited to configured attempts and retryable exception classes. Delay begins at the configured value and grows by the backoff multiplier. Non-retryable errors stop immediately. Attempts and retries are counted separately.

## Timeouts
Each backend call runs through a bounded execution future. Operations exceeding the configured duration raise a backend timeout and increment timeout metrics. The wrapper does not reinterpret object results.

## Circuit breaker
The circuit begins closed. Consecutive terminal failures increment the failure count and open the circuit at the threshold. Open circuits reject calls until cooldown. After cooldown, one half-open probe is allowed. Success closes and resets the circuit; failure reopens it.

## Metrics
The wrapper records calls, successes, terminal failures, retries, timeouts, total duration, average milliseconds, last operation, and last error type. Metrics are runtime operational evidence and contain no object content.

## Health
Health runs the backend audit through the same resilience wrapper and reports backend name, healthy state, audit result, circuit snapshot, and metrics. Failures are reported without exposing object data.

## Operations interface
The Resilience tab configures runtime retry attempts, delay, timeout, failure threshold, and cooldown, then probes local and memory backends. Results show health, circuit, calls, retries, timeouts, and last error.

## Boundary
Policies are runtime-only in this release. No remote backend, endpoint, credential, or durable resilience profile is configured.

## Verification
218 tests cover retry success, delays, non-retryable errors, exhaustion, open rejection, half-open recovery, one-probe protection, reopen on failure, timeouts, metrics, health, combined reports, policy normalization, and UI controls.

# PeaBox Voice Studio v0.10.7 Detailed Release Notes

## Backend contract
`StorageBackend` defines put, get, exists, delete, list, copy, move, and audit operations. Higher-level code can validate a backend through a contract report rather than depending on local filesystem implementation details.

## Local backend
`LocalBackend` adapts the existing safe-key, namespace, manifest, quota, copy/move/delete, and integrity-audit behavior. Existing object identities and files are unchanged.

## Memory backend
`MemoryBackend` implements the same public operations and metadata fields entirely in memory. It is intended for tests, migration validation, and future integration development. Its contents disappear when the process ends.

## Registry
The backend registry maps names to factories, validates registration input, rejects unknown names, and verifies that created objects implement the formal contract. Built-in names are `local` and `memory`.

## Cross-backend migration
A migration preview lists source backend, target backend, optional namespace filter, object identities, hashes, file count, and bytes. Application copies each object, verifies the target hash, and records completed or failed items. Existing targets fail unless overwrite is explicitly requested by code.

## Operations interface
The Backends tab displays registered backends, contract validity, local object count, audit status, namespace-filtered migration previews, and confirmation-gated non-persistent migration tests into memory.

## Remote boundary
No remote backend, endpoint, credential, or persistent backend selection is configured. Those require a future explicit credential and migration approval workflow.

## Verification
205 tests cover backend parity, metadata fields, overwrite behavior, audit tampering, registry validation, unknown backends, custom implementation rejection, namespace-filtered migration, conflict reporting, and UI disclosures.

# PeaBox Voice Studio v0.10.6 Detailed Release Notes

## Logical keys and namespaces
Objects use `<namespace>:<key>` identities. Keys are normalized POSIX-style relative paths and reject empty segments, traversal, absolute paths, spaces, and unsupported characters. Namespaces map to the existing outputs, models, backups, quarantine, support, and worker directories.

## Object operations
The local backend supports atomic byte writes, verified file imports, reads, copies, moves, and permanent deletion. Imports copy to a temporary target, compare SHA-256 when verification is enabled, atomically replace the target, and remove the source only after successful verification when move mode is requested.

## Metadata manifest
Registered objects store identity, namespace, key, filename, bytes, SHA-256, detected content type, and timestamps. The manifest is atomically updated under a local lock. Rebuild scans managed namespaces; audit detects missing objects, size changes, and hash changes.

## Migration
A migration preview lists source path, target namespace/key, file count, and bytes without mutation. Application imports every item through the verified object API and reports completed and failed items.

## Operations interface
The Objects tab can rebuild or audit the manifest, filter and browse registered objects, copy objects, move them after explicit confirmation, or permanently delete them after separate confirmation.

## Boundary
This release provides a local abstraction only. It does not configure remote object storage or persist cloud credentials. Existing directory layout and quotas remain intact.

## Verification
191 tests cover key validation, traversal rejection, namespace safety, atomic put/get, duplicate handling, verified import, move semantics, copy/move/delete, rebuild, audit drift, missing objects, migrations, and UI safeguards.

# PeaBox Voice Studio v0.10.5 Detailed Release Notes

## Managed categories
Policies separately cover generated outputs, downloaded model files, recovery artifacts such as backups/quarantine/support, and worker queue/event/state files. Project JSON is intentionally excluded so project metadata remains writable and recoverable even when generated storage is full.

## Warnings and hard limits
Each category reports files, bytes used, bytes reserved, limit, remaining capacity, usage percent, warning state, and blocked state. The warning threshold is configurable. A hard limit blocks the managed write before a temporary or final file is committed.

## Write enforcement
Atomic managed writes invoke quota preflight automatically. Kokoro’s direct WAV writer estimates the sample payload before writing. Database backups and quarantine moves preflight the destination category. Existing-file replacement charges only the growth delta.

## Capacity reservations
A reservation records category, bytes, purpose, identity, and timestamp. Reservations reduce reported remaining capacity and prevent a second operation from overbooking the same local quota. They can be explicitly released from Operations Center.

## Capacity interface
Operations Center provides policy enablement, warning threshold, per-category limits in MB, live category status, active reservations, release controls, and test reservation creation.

## Compatibility
Existing project JSON, workers, queues, recovery data, maintenance plans, governance, providers, timelines, and transcription remain compatible. Quotas default to generous local limits and may be disabled.

## Verification
178 tests cover policy normalization, category mapping, usage, warning and blocked state, overwrite deltas, disabled mode, reservation accounting, overbooking rejection, preflight invocation, all-category status, and UI controls.

# PeaBox Voice Studio v0.10.4 Detailed Release Notes

## Managed daemon
Run `python worker_local.py --daemon` or `start_worker_windows.bat` to keep a local worker active. The daemon polls for queued Kokoro jobs, processes one at a time, updates progress events, and remains available for later work.

## Ownership and heartbeat
The daemon claims a single local lock and writes a durable status record containing worker identity, process ID, mode, start time, heartbeat, processed count, last queue, and last error. A second live daemon is rejected. An expired heartbeat allows controlled stale takeover.

## Operational controls
`--pause` stops taking new work while continuing heartbeats. `--resume` returns to normal polling. `--drain` processes remaining eligible jobs and then stops. `--shutdown` requests graceful exit before new work begins. `--status` prints the durable status record.

## Interface
Batch Production displays current daemon mode, stale status, worker identity, heartbeat, and processed count. Pause, resume, drain, and shutdown controls write durable commands for the foreground daemon to observe.

## Launch safety
The Windows worker launcher reuses the application virtual environment and does not install or upgrade packages. The daemon remains a visible foreground process so the user can stop it with Ctrl+C. This release does not silently install an operating-system service.

## Compatibility
One-shot worker mode, inline Run/resume, queue cancellation, stale job leases, live events, synchronization, cloud session boundaries, portfolio governance, recovery, and maintenance remain cumulative.

## Verification
165 tests cover daemon claims, duplicate rejection, orphan-lock replacement, stale takeover, heartbeat ownership, control modes, managed queue processing, status reporting, UI controls, and Windows launcher behavior.

# PeaBox Voice Studio v0.10.3 Detailed Release Notes

## Durable worker queue
Queueing creates a standalone envelope containing a copy of the resumable job, queue identity, project and job links, state, progress, lease metadata, and error state. Queue data is stored in the local worker directory rather than in credentials or UI session state.

## Local worker process
Run `python worker_local.py --once` from the application environment to process queued Kokoro jobs. The process acquires an exclusive lease, emits item-started and item-finished events, updates durable progress after each item, and releases the lease at completion.

## Leases and recovery
A second worker cannot acquire an unexpired lease. Heartbeats extend ownership. If a worker stops, stale-lease recovery clears the expired lease and requeues any item left in `running`, recording the recovery in the event stream.

## Live progress and synchronization
Batch Production shows queue state, progress percentage, and recent events. Worker results remain isolated until **Sync worker progress** is selected, which replaces the matching project job only after project identity validation.

## Security boundary
Only Kokoro local queued items are accepted. Azure, Polly, and Google jobs remain inline because their credentials are intentionally stored only in the active Streamlit session and are not persisted into queue files.

## Compatibility
Inline execution, retries, cancellation, reopening, duplication, deletion, output ZIPs, and all cumulative portfolio, governance, recovery, and maintenance workflows remain available.

## Verification
155 tests cover queue persistence, events, cloud rejection, exclusive leases, heartbeat, release, stale recovery, successful processing, renderer failure, cancellation, progress, project synchronization, and UI controls.

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
