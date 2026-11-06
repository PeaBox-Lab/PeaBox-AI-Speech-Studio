# PeaBox Voice Studio v0.10.3
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, governance, recovery controls, maintenance planning, resumable batch jobs, and a durable local worker queue with live progress.

## v0.10.3 Local Worker & Live Progress
- Durable worker queue envelopes stored outside project JSON
- Separate `worker_local.py` process for Kokoro local batch execution
- Exclusive worker leases with heartbeat and expiry
- Stale-lease recovery that safely requeues interrupted items
- Append-only per-queue progress events
- Item-level started and finished evidence
- Worker cancellation and explicit project synchronization
- Live progress bar and event history in Batch Production
- Inline Run/resume remains available for existing workflows
- Cloud jobs remain session-bound and cannot enter the local worker queue

## Validation
- 155 automated tests passed
- Exclusive lease and stale-worker recovery behavior verified
- Cancellation, renderer failure, progress, events, and project synchronization tested
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.3.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
