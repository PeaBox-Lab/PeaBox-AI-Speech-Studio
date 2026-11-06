# PeaBox Voice Studio v0.10.2
A local-first corporate voice-production workspace with registry-driven screens, bounded production, portfolio, and governance APIs, multi-provider speech, transcription, audio quality, portable timelines, recovery controls, and local maintenance planning.

## v0.10.2 Portfolio & Governance Facades
- Added a bounded Project Portfolio workflow API
- Added a bounded Governance and Approval workflow API
- Project Workspace no longer imports project, preference, and bundle implementations directly
- Governance Center, Approval Queue, Activity History, and Portfolio Operations share one governance contract
- Added composed portfolio totals, favorite/recent access rows, governance readiness rows, and pending-first approval queues
- Portfolio Operations shows ownership, workflow, risk, comments, approvals, and readiness across local projects
- Recovery, metadata snapshots, maintenance plans, and preview-first retention remain cumulative

## Validation
- 143 automated tests passed
- All 19 navigation screens smoke-render without an active project
- Facade parity and hidden-service isolation are verified
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.2.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
