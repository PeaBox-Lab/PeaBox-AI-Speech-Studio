# PeaBox Voice Studio v0.10.3 Release Notes

v0.10.3 introduces the roadmap’s local worker and live-progress foundation. Kokoro batch jobs can be queued durably, processed from a separate terminal, monitored through append-only events, cancelled, recovered after stale leases, and explicitly synchronized back into the project.

# PeaBox Voice Studio v0.10.2 Release Notes

v0.10.2 completes the roadmap’s portfolio and governance facade milestone. Project and governance screens now rely on stable workflow contracts, and Portfolio Operations provides a consolidated cross-project view of ownership, risk, review comments, approvals, and readiness.

# PeaBox Voice Studio v0.07.4 Release Notes
This release implements the highest-priority findings from the v0.07.3 audit. Generated outputs no longer silently replace files with the same name. Timeline readiness now checks the stored audio content hash, not only file existence and script-block state.
Project imports migrate to schema 2, receive repaired nested references, and clear absolute paths that cannot safely move between machines. Timeline bundle import stages all validated media before committing and rolls back committed files if a commit step fails.
Audio processing is more memory efficient and timeline mixing is bounded. Model instances are reused, Kokoro downloads gain integrity sidecars, unknown errors are sanitized, the launcher version is corrected, and direct dependencies are constrained.
