# v0.10.7 User Guide Update

Open **Portfolio Operations → Backends** to view registered backends and contract status. You can preview local objects by namespace and run a confirmed migration validation into temporary memory. The memory backend is erased when the application reruns or exits and is not a backup.

# v0.10.6 User Guide Update

Open **Portfolio Operations → Objects**. Select **Rebuild object manifest** to register existing managed files, then audit or browse them. Copy creates a verified second object. Move requires confirmation and removes the source only after the copy verifies. Delete is permanent and requires a separate confirmation.

# v0.10.5 User Guide Update

Open **Portfolio Operations → Capacity** to configure quotas. Set category limits in MB and a warning threshold, then save. The table shows current use and reservations. Use reservations before a planned large local operation, and release them when cancelled or complete.

Project JSON is excluded. If a generated write is blocked, free space through retention/quarantine controls or raise the relevant category limit.

# v0.10.4 User Guide Update

## Start the daemon
Run `start_worker_windows.bat`, or activate the environment and run:
```bash
python worker_local.py --daemon
```
Keep the terminal open.

## Control it
Use Batch Jobs or these commands:
```bash
python worker_local.py --status
python worker_local.py --pause
python worker_local.py --resume
python worker_local.py --drain
python worker_local.py --shutdown
```
Drain completes queued work before stopping. Shutdown stops before taking new work.

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
