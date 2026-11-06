# Changelog

## v0.10.2 — Portfolio & Governance Facades
- Added `facades.portfolio` for project lifecycle, favorites/recents, imports, exports, and portfolio summaries.
- Added `facades.governance` for project governance, comments, decisions, workflow transitions, approvals, readiness, and portfolio rows.
- Added composed pending-first approval queues and portfolio governance reports.
- Routed Project Workspace, Governance Center, Approval Queue, Activity History, and Portfolio Operations through bounded APIs.
- Retained cumulative recovery, snapshots, maintenance plans, and retention previews.
- Validation: 143 tests passed.

# Changelog
## v0.07.4 — 2026-11-05
### Fixed
- Silent overwrite of generated output files
- Timeline readiness failing to detect altered audio content
- Imported batch jobs retaining the old project ID and absolute output paths
- Non-transactional bundle extraction
- Launcher displaying an obsolete version
- Estimated costs being presented as actual usage
### Added
- Project schema 2 migration framework
- Project write locks
- Timeline memory and bundle-size guards
- Model instance caching and Kokoro checksum sidecars
- User-safe error sanitization
- Direct dependency constraints
- Integrity, migration, rollback, runtime, model, and release-consistency tests
## v0.07.3 — 2026-11-05
### Added
- Workspace Command Center with screen and workflow search
- Project-aware command availability and safe navigation-only execution
- Recent command history
- Five-step first-run onboarding progress
- Dismiss and restore onboarding controls
- Shared actionable empty-state component
- Direct prerequisite navigation for project-dependent screens
- Command, onboarding, navigation, page-smoke, and compatibility tests
### Compatibility
- Recent commands and onboarding state are local interface preferences
- Project and timeline bundle formats remain unchanged
## v0.07.2 — 2026-11-05
### Added
- Sidebar Quick Access actions
- Active-project dashboard shortcuts
- Favorite and recent projects
- Persistent default workspace area
- Compact navigation and reduced-motion settings
- Compact, Standard, and Detailed dashboard modes
- Interface Preferences screen and preference reset controls
- Local preference service with atomic writes and corruption recovery
- Productivity, preferences, navigation, page-smoke, and compatibility tests
### Compatibility
- UI preferences are separate from portable project data
- All v0.07.1 project and bundle formats remain compatible
## v0.07.1 — 2026-11-05
### Fixed
- White-on-white Workspace Area selector caused by a global sidebar color override
- Low-contrast sidebar captions and project-status badges
- Weak selected-screen navigation state
- Top-banner clipping and insufficient fixed-header clearance
- Horizontal overflow and text wrapping at narrower viewport widths
### Improved
- Explicit workspace and screen navigation labels
- Select focus and dropdown popover accessibility
- Responsive content padding and mobile column stacking
- Card, expander, button, and header visual consistency
### Added
- Static visual-contract regression tests
- UI defect analysis and fix documentation
## v0.07.0 — 2026-11-05
### Added
- Governance Center with ownership, contributors, risk, target date, and review policy
- Controlled project workflow states and transition rules
- Persistent review comments with priority, target, resolution, and reopening
- Decision register with rationale and supersession history
- Approval Queue with local attestations and approval-gated workflow
- Append-only application governance audit entries
- Governance KPIs and readiness on the Executive Dashboard
- Governance tab in Activity & History
- Governance workflow, export, UI, page-smoke, and compatibility tests
### Clarification
- Actor and reviewer names are local labels, not authenticated identities
- Approval records are local attestations, not digital signatures
### Compatibility
- All v0.06.0 and earlier project and timeline bundle formats remain readable
## v0.06.0 — 2026-11-05
### Added
- Corporate visual theme and reusable UI component system
- Executive Dashboard with KPIs, readiness, workflow, and recent activity
- Grouped business navigation across five workspace areas
- Contextual page headers with project and version context
- Consolidated Activity & History tabs
- Corporate UI, dashboard, navigation, page-smoke, and feature-preservation tests
- UI design specification
### Changed
- Reordered and renamed menu labels for clearer business workflows
- Replaced the flat sidebar menu with area selection plus screen navigation
- Improved spacing, cards, metrics, callouts, expanders, and button hierarchy
### Compatibility
- All v0.05.01 project and bundle formats remain compatible
- No production feature was removed
## v0.05.01 — 2026-11-05
### Added
- Portable timeline ZIP bundles with project JSON and copied WAV assets
- Collision-safe bundle import with new project identity and rewritten paths
- Archive traversal, symbolic-link, encryption, count, and size protections
- WAV-content validation before asset extraction
- Clip relinking, metadata refresh, stale-source acknowledgement, and record cleanup
- Clip-set duplication for alternate timeline arrangements
- Bundle security, roundtrip, collision, relinking, repair, navigation, and regression tests
### Changed
- Clip records now include an asset-content hash
- Bundle imports clear prior timeline export history
## v0.04.01 — 2026-11-05
### Added
- System Check for Python, FFmpeg, storage, and Kokoro model readiness
- Media-format readiness checks before transcription
- Transcript overlap, duration, and empty-text validation
- Automatic sequential timing repair
- Saved transcript update and schema-v2 session support
- Pronunciation duplicate and overlap diagnostics
- Pronunciation match preview status
- Tests for diagnostics, timing repair, invalid-export blocking, and rule conflicts
### Changed
- Invalid transcript timing now blocks SRT/VTT export and project saving
- Older invalid transcript sessions are repaired when loaded
### Preserved
- v0.04.00 quality and transcription features
- v0.03.12 UI rendering regression protection
## v0.03.12 — 2026-11-05
### Fixed
- Replaced a conditional Streamlit UI expression that leaked a `DeltaGenerator` object into page content
- Restored the normal Projects interface and unobstructed sidebar navigation
- Added a visible sidebar version marker to identify stale running releases
- Added launcher output showing the exact release folder and version
### Added
- Regression tests for Streamlit magic-expression leaks
- Navigation structure tests covering all registered application pages
- Troubleshooting guidance for stopping older Streamlit processes and opening the correct local URL
## v0.03.11 — 2026-11-05
### Added
- Azure, Polly, and Google voice discovery
- Session-cached normalized voice catalogs
- Searchable cross-provider Voice Library and capability matrix
- Catalog-backed cloud voice selection in script blocks
- Reusable project voice/direction presets
- Job duplication, cancelled-item reopening, and job deletion
- Catalog, preset, normalization, and job-recovery tests
### Security
- Credentials and discovered catalogs remain session-only
- Presets store only non-secret generation settings
### Compatibility
- v0.03.10 projects and saved jobs remain readable
## v0.03.10 — 2026-11-05
### Added
- Session-only Azure Speech, Amazon Polly, and Google Cloud TTS profiles
- Provider-specific cloud voice and language identifiers
- Provider-readiness validation before job creation
- Persistent resumable batch jobs and per-item state
- Retry failed items and cancel queued work
- Job output ZIPs and a 20-job project history
- Estimated-versus-recorded usage cost tracking
- Tests covering jobs, retries, cancellation, job persistence, and credential exclusion
### Security
- API keys, AWS secrets, tokens, and Google service-account contents remain only in Streamlit session state
- Project exports and job records contain no credential values
### Limitation
- Jobs execute in the Streamlit process when the user runs them; a separate background worker is not yet included
## v0.03.01 — 2026-11-05
### Added
- Complete project JSON export and collision-safe import
- Append-or-replace paragraph import mode
- Block filtering and bulk enable/disable controls
- Batch-readiness validation with errors and warnings
- Schema-v2 render manifests with validation details
- Persistent last-batch summary and per-block results
- Tests for project portability, validation failures, bulk controls, and result summaries
### Fixed
- Empty enabled blocks are rejected before local generation
- Render results now retain block titles for easier diagnosis
- Project imports no longer risk overwriting an existing identity
### Compatibility
- Existing v0.03.00 raw project files remain readable
- Imported bundles accept both wrapped exports and raw project objects
## v0.03.00 — 2026-11-05
### Added
- Ordered Script Blocks workspace
- Per-block provider, language, voice, speed, direction notes, and batch inclusion
- Paragraph-to-block import, reordering, duplication, and deletion
- Batch Production dashboard with estimates and JSON manifest
- Kokoro local multi-block rendering and packaged batch download
- Migration-safe block schema and batch services
- Evidence-based roadmap derived from the supplied development plan
- Automated tests for block lifecycle, ordering, manifests, batch behavior, ZIP output, launcher, subtitles, and file safety
### Preserved
- Persistent projects and Master Script
- Single local Kokoro generation and render history
- Local Faster-Whisper transcription with TXT/SRT output
- Flexible Python 3.10–3.12 Windows launcher
