# PeaBox Voice Studio v0.11.0
A local-first corporate voice-production workspace with modular screens, governed workflows, provider sandboxes, managed workers, storage backends, backend resilience, and durable reviewed resilience profiles.

## v0.11.0 Governed Resilience Profiles
- Durable retry, timeout, and circuit settings without credentials
- Draft, In Review, Changes Requested, Approved, Active, and Archived states
- Controlled transition rules
- Reviewer must differ from profile creator for approval
- One Active profile per backend
- New activation automatically returns the previous Active profile to Approved
- Draft/changes-only editing
- Clone, compare, archive, reactivate, and Draft deletion
- Append-only local profile audit history
- Active profile instantiation and health probing
- Operations Center Profiles tab

## Validation
- 247 automated tests passed
- Validation bounds, transitions, reviewer separation, activation, cloning, deletion, diffs, audit, and instantiation verified
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.11.0.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
