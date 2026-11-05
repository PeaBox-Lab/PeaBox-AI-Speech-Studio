# PeaBox Voice Studio v0.03.00 Release Notes

This release moves PeaBox from a single-script utility toward the multi-voice production workflow described in the attached development context. A project can now contain ordered script blocks, each with independent provider, voice, language, speed, direction notes, and batch inclusion settings.

The Batch Production view turns those blocks into a portable render manifest, summarizes estimated length and inherited provider cost, renders enabled Kokoro local blocks, and packages generated audio with its manifest. Cloud blocks remain visible and portable but are intentionally skipped by the local batch renderer until credential profiles, asynchronous jobs, retries, and actual-cost tracking are implemented.

The supplied context also informs a staged roadmap for cloud aggregation, pronunciation and diarization, a non-destructive timeline, scale, provenance, and consent. No claim is made that the market or legal figures were independently verified in this workspace.
