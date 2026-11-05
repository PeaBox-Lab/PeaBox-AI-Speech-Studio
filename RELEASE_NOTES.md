# PeaBox Voice Studio v0.03.10 Release Notes

This release activates the cloud-batch foundation from the roadmap. Azure Speech, Amazon Polly, and Google Cloud TTS can be configured for the current Streamlit session, while Kokoro remains available without credentials. Secret values are deliberately excluded from projects and exports.

Batch Production now creates persistent job snapshots. Each block tracks its own state, attempts, output, failure message, estimated cost, and recorded usage cost. Successful items are not repeated when a job resumes; failed items can be queued again; queued work can be cancelled. Completed files and job metadata can be downloaded together.

Execution remains UI-initiated and process-bound. The next scalability step is a separate worker and live progress channel rather than claiming that this release provides true background execution.
