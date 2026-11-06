# v0.10.3 User Guide Update

## Queue a job
In **Batch Jobs**, create or select a resumable Kokoro job and choose **Queue for local worker**.

## Run the worker
Open a second terminal in the extracted application folder, activate the same virtual environment, and run:
```bash
python worker_local.py --once
```
Return to Batch Jobs and choose **Sync worker progress**. Use **Recover stale leases** after an interrupted worker.

Cloud-provider jobs continue to use **Run/resume** inside the active session.

# v0.10.2 User Guide Update

Open **Overview → Portfolio Operations** for a cross-project governance table. Use **Project Workspace** for project creation and portability, **Governance Center** for ownership/comments/decisions, and **Approval Queue** for requests and decisions. Existing recovery and maintenance controls remain in Portfolio Operations.

# User Guide
## Preserve output history
PeaBox automatically creates numbered filenames when output names repeat. Existing files remain untouched.
## Move a project
- Use Project JSON for scripts, settings, governance, and metadata. Non-portable media paths are removed on import.
- Use a timeline bundle to move validated WAV assets with the project.
## Resolve timeline integrity warnings
- **Audio changed:** refresh metadata only after confirming the current file is correct.
- **Source stale:** regenerate or acknowledge the current script-block version after review.
- **File missing:** relink a replacement WAV.
## Monitor costs
Recorded planning-rate usage is an estimate based on successfully generated characters. It is not the provider invoice.
