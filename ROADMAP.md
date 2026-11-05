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

## Next — v0.03.10: Cloud batch and configuration

- Encrypted/session-scoped provider profiles
- Dynamic voice discovery cache and provider capability matrix
- Asynchronous per-block cloud generation with retry and cancellation
- Actual-versus-estimated cost ledger
- Batch status, partial retry, and resumable manifests

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

## v0.06.00: Scale and collaboration

- SQLite repository migration followed by optional PostgreSQL
- Background job queue and local worker process
- Object-storage abstraction, quotas, structured logs, and health checks
- Authentication, roles, shared projects, and review comments

## Guarded research track

Voice cloning, consent ledgers, C2PA, deep watermarking, and real-time agents must not be presented as legally compliant or production-ready merely because they appear in a market plan. Before implementation, validate model licenses, consent requirements, jurisdictional applicability, export-tool compatibility, security controls, and authoritative current guidance.
