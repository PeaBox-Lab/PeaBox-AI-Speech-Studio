# PeaBox Voice Studio v0.10.4
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, portfolio governance, recovery controls, maintenance planning, resumable jobs, live progress, and a managed local worker daemon.

## v0.10.4 Managed Worker Daemon
- Long-running local Kokoro worker mode
- Single-daemon ownership enforced by a local claim file
- Durable daemon status and heartbeat evidence
- Pause and resume controls
- Drain mode that finishes queued work before stopping
- Graceful shutdown request
- Stale-daemon detection and safe takeover
- Batch Production daemon status and controls
- Dedicated Windows worker launcher using the existing virtual environment
- One-shot worker mode remains available

## Validation
- 165 automated tests passed
- Exclusive daemon ownership and stale takeover verified
- Pause, resume, drain, shutdown, heartbeat, and processing lifecycle tested
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.4.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
