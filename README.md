# PeaBox Voice Studio v0.10.8
A local-first corporate voice-production workspace with modular screens, bounded workflows, governance, recovery, managed workers, quotas, object storage, pluggable backends, and backend resilience policies.

## v0.10.8 Backend Resilience
- Runtime resilience wrapper for any storage backend
- Configurable retry attempts, initial delay, and exponential backoff
- Per-operation timeout enforcement
- Closed, open, and half-open circuit states
- Failure thresholds and cooldown recovery
- Single half-open probe protection
- Call, success, failure, retry, timeout, latency, and last-error metrics
- Backend health reports combining audit, circuit, and metrics
- Operations Center resilience simulator for local and memory backends
- No remote credentials or persistent resilience selection

## Validation
- 218 automated tests passed
- Retry, non-retryable, exhaustion, timeout, circuit, half-open, and recovery paths verified
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.8.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
