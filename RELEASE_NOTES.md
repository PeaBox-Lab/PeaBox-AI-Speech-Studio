# PeaBox Voice Studio v0.09.4 Release Notes

v0.09.4 fixes the screenshot-reported sidebar and navigation failures. Quick Access labels now remain readable against the dark corporate sidebar, programmatic navigation no longer mutates instantiated Streamlit widget keys, and Project Workspace uses the shared application context instead of an unavailable bootstrap helper.

# PeaBox Voice Studio v0.09.3 Release Notes

v0.09.3 introduces bounded workflow APIs for Timeline Studio, Batch Production, and Transcription Studio. These complex screens now depend on stable facade modules rather than the implementation details of multiple underlying services, improving maintainability without changing user workflows or project formats.

# PeaBox Voice Studio v0.07.4 Release Notes
This release implements the highest-priority findings from the v0.07.3 audit. Generated outputs no longer silently replace files with the same name. Timeline readiness now checks the stored audio content hash, not only file existence and script-block state.
Project imports migrate to schema 2, receive repaired nested references, and clear absolute paths that cannot safely move between machines. Timeline bundle import stages all validated media before committing and rolls back committed files if a commit step fails.
Audio processing is more memory efficient and timeline mixing is bounded. Model instances are reused, Kokoro downloads gain integrity sidecars, unknown errors are sanitized, the launcher version is corrected, and direct dependencies are constrained.
