# PeaBox Voice Studio v0.04.01 Release Notes

This maintenance release hardens the Quality and Transcription Studio introduced in v0.04.00.

Transcript edits are now validated before subtitle export or project saving. Overlaps, zero-duration segments, and invalid timing are surfaced directly. An automatic repair action makes segments sequential and applies a minimum duration. Older saved sessions are validated and repaired when loaded, and existing sessions can be updated in place.

A new System Check page reports Python compatibility, FFmpeg availability, writable project/output storage, and Kokoro model readiness. Compressed-media transcription is disabled with a clear explanation when FFmpeg is unavailable, while WAV input remains usable.

Pronunciation rules now display duplicate and overlap diagnostics, and the preview states whether any rule actually changed the text.
