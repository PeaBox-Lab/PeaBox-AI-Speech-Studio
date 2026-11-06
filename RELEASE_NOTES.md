# PeaBox Voice Studio v0.09.0 Release Notes

v0.09.0 turns the application shell into a modular screen platform. High-level workspace screens now render through a registry and shared context rather than living directly in the main script. The new Operations Center consolidates project health, repair previews, repository maintenance, local maintenance plans, and operational events. JSON project files remain the source of truth; SQLite is a disposable, rebuildable index.

# PeaBox Voice Studio v0.07.4 Release Notes
This release implements the highest-priority findings from the v0.07.3 audit. Generated outputs no longer silently replace files with the same name. Timeline readiness now checks the stored audio content hash, not only file existence and script-block state.
Project imports migrate to schema 2, receive repaired nested references, and clear absolute paths that cannot safely move between machines. Timeline bundle import stages all validated media before committing and rolls back committed files if a commit step fails.
Audio processing is more memory efficient and timeline mixing is bounded. Model instances are reused, Kokoro downloads gain integrity sidecars, unknown errors are sanitized, the launcher version is corrected, and direct dependencies are constrained.