# v0.09.2 Feature Additions

## Explicit screen ownership
Each screen declares only the shared services and interface components it requires. This reduces accidental coupling and makes screen-level maintenance and testing more predictable.

## Dependency quality gates
The test suite rejects wildcard imports, unused imports, peer-screen imports, application-bootstrap imports, and dependency budgets above 25 names.

# v0.09.1 Feature Additions

## Fully modular workspace
Every workspace destination is isolated in its own screen module and resolved through one central registry.

## Operations Center
Review project health, preview and confirm safe repairs, rebuild the secondary project index, manage local maintenance plans, and inspect operational events.

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
