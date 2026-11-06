# v0.10.9 Feature Additions

## Offline Cloud Provider Sandbox
Validate cloud voice discovery and synthesis payload contracts without external services, credentials, network access, or charges.

# v0.10.8 Feature Additions

## Backend Resilience
Wrap any storage backend with bounded retries, timeouts, circuit protection, health probes, and operational metrics before using it in production workflows.

# v0.10.7 Feature Additions

## Pluggable Storage Backends
Validate storage implementations through a stable contract and test cross-backend migration with a non-persistent in-memory backend while retaining the local backend as the durable default.

# v0.10.6 Feature Additions

## Local Object Storage
Address managed files through stable logical keys, audit them against a metadata manifest, perform verified object operations, and migrate existing local directories through preview-first workflows.

# v0.10.5 Feature Additions

## Storage Capacity Policies
Monitor and control generated outputs, models, recovery artifacts, and worker state with warning thresholds, hard limits, and capacity reservations.

# v0.10.4 Feature Additions

## Managed Local Worker
Keep one Kokoro worker running in a separate foreground terminal, inspect its durable status, control its intake, drain queued work, and shut it down gracefully.

# v0.10.3 Feature Additions

## Local Worker & Live Progress
Queue Kokoro batch jobs, process them outside the Streamlit request, monitor durable item-level progress, recover interrupted leases, and synchronize completed state back into the project.

# v0.10.2 Feature Additions

## Portfolio Operations
Review ownership, workflow stage, risk, comments, approvals, and readiness across every local project.

## Stable portfolio and governance APIs
Project and governance screens now share bounded public workflows instead of coupling to implementation modules.

# Features Guide
## Workspace productivity
- Executive Dashboard
- Workspace Command Center
- Grouped corporate navigation
- Sidebar Quick Access
- Favorite and recent projects
- Recent command history
- First-run onboarding
- Interface density, motion, startup, and dashboard preferences
## Projects and production
- Portable project workspace and master script
- Provider-aware script blocks
- Single speech generation and resumable batch jobs
- Multi-provider voice discovery
- Non-destructive Timeline Studio and merged WAV exports
## Audio, quality, and transcription
- Voice Library and presets
- Pronunciation dictionary and safe pause markers
- WAV analysis, normalization, silence trimming, and A/B comparisons
- Local transcription with editable segments and TXT/SRT/VTT export
## Governance
- Owners, contributors, risk, target date, and workflow states
- Review comments and resolutions
- Decision register
- Approval Queue
- Application governance audit log
## Portability and safety
- Project JSON import/export
- Secure timeline bundles with copied WAV assets
- Missing-asset relinking
- Session-only cloud credentials
- Setup diagnostics and visual regression protections
