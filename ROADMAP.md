# Product Roadmap

## Evidence boundary

This roadmap is based on the attached v0.2 code and the engineering gaps identified in `AUDIT.md`. It does not claim current market size, competitor capabilities, pricing, or user-demand rankings.

## Product direction

Evolve PeaBox Voice Studio from a provider demo into a local-first speech-production workspace: persistent projects, repeatable settings, multi-part scripts, reliable renders, and export workflows. Keep local operation simple while creating clean seams for future hosted deployment.

## Release sequence

### v0.02.01 — Project foundation (built here)

- Persistent local projects and Master Script
- Project-linked render history and last-used settings
- Modular providers and services
- Safer filenames, atomic writes, and resource limits
- Standards-compatible SRT export
- Automated core tests and documented limitations

### v0.03.00 — Script blocks and batch production

- Split a master script into ordered blocks
- Assign voice, provider, speed, and language per block
- Reorder, duplicate, disable, and preview blocks
- Batch-render selected blocks with progress and cancellation
- Produce a manifest connecting each output to text and settings

### v0.04.00 — Voice direction and quality controls

- Pronunciation dictionary and replacements
- Pauses, emphasis, rate, pitch, and style controls where supported
- Voice favorites, searchable filters, and reusable presets
- Side-by-side A/B renders with user notes
- Loudness normalization and configurable silence trimming

### v0.05.00 — Timeline and publishing

- Assemble rendered blocks on a simple timeline
- Regenerate one block without rebuilding the whole project
- Export merged audio, SRT/VTT, transcript, and project manifest
- Add chapter markers and target-duration indicators
- Validate missing or stale render dependencies before export

### v0.06.00 — Reliability and scale

- Background job queue for long renders and transcription
- SQLite/PostgreSQL repository abstraction
- Object-storage abstraction for generated media
- Resumable jobs, structured logging, health checks, and quotas
- Authentication and role controls for hosted deployments

## UX priorities

1. Make project state obvious at all times.
2. Preserve user work automatically or clearly indicate unsaved changes.
3. Keep provider-specific settings inside a consistent generation flow.
4. Present plain-language errors with a recovery action.
5. Make expensive or destructive actions explicit and reversible where possible.
6. Keep transcripts, subtitles, scripts, settings, and audio traceable to one project.

## Performance priorities

- Cache model instances rather than rebuilding them per action.
- Move long-running work off the UI thread.
- Stream or chunk large media where provider APIs allow it.
- Avoid loading complete render histories or media bytes until requested.
- Add timing and failure metrics before optimizing provider-specific paths.

## Future market and alternatives research checklist

When web-enabled research is available, collect dated evidence for:

- Primary user segments and jobs-to-be-done
- Named desktop, web, cloud, and open-source alternatives
- Pricing units, free tiers, voice/language coverage, and export limits
- Project organization, collaboration, batch, timeline, and API features
- Privacy posture, local/offline capability, credential handling, and data retention
- Review themes around onboarding, voice quality, speed, reliability, and support
- Differentiation opportunities supported by repeated user evidence

Do not convert this checklist into product claims until each item is supported by current evidence.
