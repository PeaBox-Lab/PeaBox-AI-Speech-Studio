# Roadmap

## Delivered in v0.11.1
- Deterministic navigation and theme baselines
- Screen label and widget-call snapshots
- Contrast and responsive validation
- Desktop/tablet/mobile screenshot manifest
- Baseline drift comparison
- Operations Center Visual QA

## Recommended next release
- Approved browser runner for PNG capture and pixel-diff reports
- Live provider integration harness with explicit test credentials and cost guardrails
- Optional remote backend with explicit credentials, approval, and rollback
- Authenticated identity integration for governance actions

# Roadmap

## Delivered in v0.11.0
- Durable resilience profiles
- Draft/review/approval/activation lifecycle
- Reviewer separation
- Single-active enforcement
- Clone, compare, audit, and runtime probe

## Recommended next release
- Browser-driven screenshot regression suite
- Live provider integration harness with explicit test credentials and cost guardrails
- Optional remote backend with explicit credentials, approval, and rollback
- Authenticated identity integration for governance actions

# Roadmap

## Delivered in v0.10.9
- Azure offline sandbox
- Polly standard and neural offline sandboxes
- Google Cloud TTS offline sandbox
- Voice discovery and synthesis contract runner
- Failure injection and sanitized evidence
- Provider Setup sandbox panel

## Recommended next release
- Browser-driven screenshot regression suite
- Live provider integration harness with explicit test credentials and cost guardrails
- Durable resilience profiles with review controls
- Optional remote backend with explicit credentials, approval, and rollback

# Roadmap

## Delivered in v0.10.8
- Backend health contract
- Bounded retries and backoff
- Operation timeouts
- Circuit breaker and cooldown
- Runtime metrics and health reports
- Operations Center resilience probes

## Recommended next release
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Durable resilience profiles with review controls
- Optional remote backend with explicit credentials, approval, and rollback

# Roadmap

## Delivered in v0.10.7
- Formal storage backend contract
- Local backend adapter
- In-memory validation backend
- Backend registry and contract reports
- Cross-backend migration validation

## Recommended next release
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Optional remote backend with explicit credentials, approval, and rollback
- Backend health, retry, and circuit-breaker contract

# Roadmap

## Delivered in v0.10.6
- Local object-storage abstraction
- Safe logical keys and namespaces
- Verified object operations
- Durable manifest and integrity audit
- Legacy-directory migration previews
- Operations Center object controls

## Recommended next release
- Pluggable backend contract and in-memory test backend
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Optional remote object backend with explicit credentials and migration approval

# Roadmap

## Delivered in v0.10.5
- Local storage quota categories
- Warning and hard-limit policies
- Managed write preflight
- Concurrent capacity reservations
- Operations Center Capacity tab
- Project JSON exclusion

## Recommended next release
- Object-storage abstraction over local managed categories
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Optional operating-system service installation with explicit consent

# Roadmap

## Delivered in v0.10.4
- Long-running local worker daemon
- Single-daemon ownership and stale takeover
- Durable heartbeat and status
- Pause, resume, drain, and shutdown
- Batch Production daemon controls
- Dedicated foreground Windows launcher

## Recommended next release
- Local storage quotas and capacity policies
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Optional operating-system service installation with explicit user consent

# Roadmap

## Delivered in v0.10.3
- Durable local worker queue
- Exclusive leases and heartbeat
- Stale-worker recovery
- Live item-level progress events
- Cancellation and explicit project synchronization
- Session-only cloud credential boundary

## Recommended next release
- Cloud-provider sandbox integration tests
- Browser-driven screenshot regression suite
- Long-running worker daemon with explicit install and shutdown controls
- Object-storage abstraction and local quotas

# Roadmap

## Delivered in v0.10.2
- Project portfolio workflow facade
- Governance and approval workflow facade
- Cross-project governance and readiness rows
- Pending-first approval queue API
- Consolidated Portfolio Operations view

## Recommended next release
- Browser-driven screenshot regression suite
- Cloud-provider sandbox integration tests
- Optional operating-system maintenance scheduling
- Background worker and live job progress architecture

# Evidence-Based Product Roadmap
## Roadmap basis
This roadmap translates the attached market, architecture, UX, and user-story context into build stages appropriate for the existing local Streamlit application. The attached market figures and legal statements are treated as supplied planning context, not independently verified claims.
## Delivered — v0.03.00: Multi-block production
- Ordered script blocks derived from a Master Script
- Per-block provider, voice, language, speed, notes, and enabled state
- Reordering, duplication, selective inclusion, and project persistence
- Batch planning totals and portable JSON manifest
- Kokoro local batch rendering with downloadable ZIP
This stage addresses the supplied multi-voice workflow and creates the clip object model required by a later timeline without forcing an immediate frontend rewrite.
## Delivered — v0.03.01: Portability and batch reliability
- Complete project JSON export/import with collision-safe identities
- Append-or-replace script-block import and bulk block controls
- Batch readiness errors and cloud-execution warnings
- Versioned schema-v2 manifests and persistent last-batch outcomes
This maintenance stage reduces data-loss and failed-render risk before cloud batch execution is introduced.
## Delivered — v0.03.10: Cloud batch foundation
- Session-only cloud credential profiles excluded from project data
- Provider readiness and provider-specific block identifiers
- Persistent resumable jobs, retries, cancellation, and output packages
- Estimated and recorded usage cost tracking
Dynamic voice discovery, capability catalogs, reusable presets, and expanded job recovery were delivered in v0.03.11. The remaining infrastructure gap is moving execution into a separate worker with live progress.
## Delivered — v0.03.11: Cloud production usability
- Session-cached Azure, Polly, and Google voice discovery
- Searchable normalized voice library and provider capability matrix
- Reusable project voice/direction presets
- Job duplicate, reopen, retry, cancellation, deletion, and output recovery controls
## v0.04.00: Quality and transcription studio
- Pronunciation dictionary and provider-aware SSML controls
- Reusable voice/direction presets and searchable voice filters
- Audio normalization and silence controls
- Optional speaker diarization with explicit model setup
- Speaker-labelled TXT, SRT, and VTT exports
## v0.05.00: Non-destructive timeline
- AudioClip repository separated from script blocks
- Waveform peak extraction and clip duration metadata
- Drag/reorder timeline with start offsets and regeneration status
- Background music track and mix preview
- Merged WAV export and chapter/manifest outputs
A React/Web Audio frontend and FastAPI service become justified at this stage, when low-latency playback and timeline interaction exceed Streamlit's strengths.
## Delivered — v0.05.01: Timeline portability and recovery
- Portable project-plus-WAV timeline bundles
- Collision-safe and path-safe asset import
- Clip relinking, metadata refresh, stale acknowledgement, and invalid-record cleanup
## Delivered — v0.06.0: Corporate multi-screen workspace
- Executive dashboard and workflow-aligned grouped navigation
- Reusable corporate visual components and consistent page framing
- Consolidated activity and history review screens
## Delivered — v0.07.0: Collaboration and governance foundation
- Project ownership, contributors, risk, review policy, and workflow states
- Review comments, decision register, approval queue, and application audit history
- Dashboard governance readiness and consolidated review history
Authenticated identities, permissions, and shared storage remain part of the future multi-user architecture.
## Delivered — v0.07.2: Daily productivity and personalization
- Project-aware quick actions and sidebar shortcuts
- Favorite and recent projects
- Persistent local interface density, motion, startup, and dashboard preferences
## Delivered — v0.07.3: Command discovery and guided onboarding
- Searchable safe-navigation command center
- Project-aware command availability and recent commands
- First-run progress and actionable prerequisite empty states
## Delivered — v0.07.4: Reliability and integrity hardening
- Collision-safe outputs and live asset hash verification
- Schema migrations, reference repair, transactional imports, and project write locks
- Bounded media memory, cached models, sanitized errors, and release consistency controls
## v0.06.00: Scale and collaboration
- SQLite repository migration followed by optional PostgreSQL
- Background job queue and local worker process
- Object-storage abstraction, quotas, structured logs, and health checks
- Authentication, roles, shared projects, and review comments
## Guarded research track
Voice cloning, consent ledgers, C2PA, deep watermarking, and real-time agents must not be presented as legally compliant or production-ready merely because they appear in a market plan. Before implementation, validate model licenses, consent requirements, jurisdictional applicability, export-tool compatibility, security controls, and authoritative current guidance.
