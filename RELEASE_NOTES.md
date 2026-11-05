# PeaBox Voice Studio v0.04.00 Release Notes

This release begins the Quality & Transcription Studio phase described in the supplied development plan. Projects can maintain pronunciation replacements and use controlled pause markers without editing raw SSML. Cloud providers receive compiled SSML breaks, while local Kokoro generation receives a safe punctuation-based approximation. Batch jobs store processed text alongside original text so later retries remain reproducible.

Transcription results are now editable as timestamped segments. Users can search the working transcript, add speaker labels, export TXT/SRT/VTT, and save transcript sessions inside a project for later editing.

The v0.03.12 UI fix remains protected by regression and page-smoke tests.
