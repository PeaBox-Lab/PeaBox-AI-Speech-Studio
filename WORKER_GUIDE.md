# Managed Worker Guide

## Start
Use `start_worker_windows.bat` or `python worker_local.py --daemon`. The worker stays in the foreground.

## Status record
The local status includes worker ID, PID, mode, timestamps, processed jobs, last queue ID, and last error.

## Modes
- **running:** polls and processes queued Kokoro work.
- **paused:** heartbeats but takes no new work.
- **draining:** processes eligible work, then stops.
- **shutdown:** exits before accepting new work.
- **stopped:** no active daemon.

## Ownership
Only one non-stale daemon may own the local claim. A stale heartbeat permits takeover.

## Security
Only Kokoro local jobs are accepted. Cloud credentials remain session-only and never enter daemon files.
