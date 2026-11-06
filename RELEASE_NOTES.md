# PeaBox Voice Studio v0.11.2 Release Notes

v0.11.2 completes the pixel-comparison half of the visual-regression roadmap. Approved browser-generated baseline and candidate PNG sets can now be validated, compared with configurable tolerances, and packaged into machine-readable reports and highlighted diff artifacts.

# PeaBox Voice Studio v0.11.1 Release Notes

v0.11.1 delivers the roadmap’s visual regression foundation without requiring a browser package. It creates deterministic structural baselines for navigation, theme, screens, labels, widget calls, responsive rules, and contrast, plus a screenshot-ready capture manifest.

# PeaBox Voice Studio v0.11.0 Release Notes

v0.11.0 adds durable governance to backend resilience configuration. Retry, timeout, and circuit policies can now move through a local draft-review-approval-activation lifecycle before they are used to wrap a backend.

# PeaBox Voice Studio v0.10.9 Release Notes

v0.10.9 delivers the roadmap’s cloud-provider sandbox milestone. Azure, Polly, and Google application contracts can now be tested deterministically without network access, real credentials, provider charges, or external service dependencies.

# PeaBox Voice Studio v0.10.8 Release Notes

v0.10.8 adds the resilience contract required before future remote storage can be considered. Any storage backend can now be wrapped with retries, operation timeouts, circuit breaking, health probes, and operational metrics without changing its object semantics.

# PeaBox Voice Studio v0.10.7 Release Notes

v0.10.7 formalizes the object-storage layer behind a pluggable backend contract. The current local backend remains authoritative, while a non-persistent in-memory backend verifies behavioral parity and cross-backend migration without introducing remote credentials.

# PeaBox Voice Studio v0.10.6 Release Notes

v0.10.6 delivers the roadmap’s object-storage abstraction milestone as a local backend. Managed files can now be addressed by safe namespace/key pairs, indexed in a durable manifest, audited for drift, and migrated without exposing absolute paths to higher-level workflows.

# PeaBox Voice Studio v0.10.5 Release Notes

v0.10.5 delivers the roadmap’s local storage quota milestone. The application can warn before capacity pressure, block managed writes before they exceed configured limits, and reserve capacity for concurrent planned operations without restricting authoritative project JSON.

# PeaBox Voice Studio v0.10.4 Release Notes

v0.10.4 advances the local worker foundation into a managed daemon. One process can continuously drain Kokoro jobs while exposing durable status, heartbeat, pause/resume, drain, shutdown, and stale-takeover controls.

# PeaBox Voice Studio v0.10.3 Release Notes

v0.10.3 introduces the roadmap’s local worker and live-progress foundation. Kokoro batch jobs can be queued durably, processed from a separate terminal, monitored through append-only events, cancelled, recovered after stale leases, and explicitly synchronized back into the project.

# PeaBox Voice Studio v0.10.2 Release Notes

v0.10.2 completes the roadmap’s portfolio and governance facade milestone. Project and governance screens now rely on stable workflow contracts, and Portfolio Operations provides a consolidated cross-project view of ownership, risk, review comments, approvals, and readiness.

# PeaBox Voice Studio v0.07.4 Release Notes
This release implements the highest-priority findings from the v0.07.3 audit. Generated outputs no longer silently replace files with the same name. Timeline readiness now checks the stored audio content hash, not only file existence and script-block state.
Project imports migrate to schema 2, receive repaired nested references, and clear absolute paths that cannot safely move between machines. Timeline bundle import stages all validated media before committing and rolls back committed files if a commit step fails.
Audio processing is more memory efficient and timeline mixing is bounded. Model instances are reused, Kokoro downloads gain integrity sidecars, unknown errors are sanitized, the launcher version is corrected, and direct dependencies are constrained.
