# PeaBox Voice Studio v0.10.5
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, governance, recovery controls, maintenance planning, managed workers, and configurable local storage quotas.

## v0.10.5 Storage Quotas & Capacity Policies
- Separate limits for generated outputs, downloaded models, recovery artifacts, and worker state
- Configurable warning threshold and hard limits
- Pre-write quota enforcement for atomic writes and Kokoro WAV generation
- Backup and quarantine preflight checks
- Overwrite-aware byte calculations
- Capacity reservations to prevent concurrent over-allocation
- Operations Center capacity dashboard and policy editor
- Explicit exclusion of authoritative project JSON
- Quotas can be disabled for unrestricted local operation

## Validation
- 178 automated tests passed
- Category mapping, usage, warnings, blocking, overwrite deltas, and reservations verified
- Atomic writes are confirmed to invoke quota preflight
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.5.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
