# PeaBox Voice Studio v0.05.01 Release Notes

This maintenance release makes the v0.05.00 Timeline Studio portable and recoverable. A timeline bundle includes project JSON plus copied WAV assets, while import creates a new project identity, extracts collision-safe local files, and rewrites clip references.

Bundle imports validate archive paths, member types, size limits, and WAV content. Original absolute file paths are never trusted. Clips whose source audio was not available during export remain unlinked so they can be recovered using the new relink workflow.

Timeline Studio also adds metadata refresh, stale-source acknowledgement, duplicate-ID repair, confirmed missing-record cleanup, and clip-set duplication for alternate edits.
