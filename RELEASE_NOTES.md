# PeaBox Voice Studio v0.09.2 Release Notes

v0.09.2 hardens the full-screen modular architecture by replacing the broad shared dependency surface with explicit imports in every screen. Each screen now declares exactly which services, models, constants, and UI helpers it owns, making changes easier to review and preventing accidental cross-feature coupling.

# PeaBox Voice Studio v0.09.1 Release Notes

v0.09.1 completes the screen-architecture transition begun in v0.09.0. Every navigation destination now has an independent renderer module, while the main application only initializes shared state and dispatches the selected screen. This lowers regression risk, makes page ownership explicit, and creates a stable base for browser tests and future provider integrations.

# PeaBox Voice Studio v0.07.4 Release Notes
This release implements the highest-priority findings from the v0.07.3 audit. Generated outputs no longer silently replace files with the same name. Timeline readiness now checks the stored audio content hash, not only file existence and script-block state.
Project imports migrate to schema 2, receive repaired nested references, and clear absolute paths that cannot safely move between machines. Timeline bundle import stages all validated media before committing and rolls back committed files if a commit step fails.
Audio processing is more memory efficient and timeline mixing is bounded. Model instances are reused, Kokoro downloads gain integrity sidecars, unknown errors are sanitized, the launcher version is corrected, and direct dependencies are constrained.
