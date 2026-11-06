# PeaBox Voice Studio v0.11.1
A local-first corporate voice-production workspace with modular screens, governed workflows, provider sandboxes, managed workers, resilient storage backends, and deterministic visual regression baselines.

## v0.11.1 Deterministic UI Baselines
- Navigation and page-metadata snapshots for all 19 pages
- Theme token and component contract snapshots
- Static screen widget-call, label, line-count, and source-hash snapshots
- WCAG-style contrast checks for sidebar controls and content cards
- Responsive desktop, tablet, and mobile viewport manifest
- 57 planned screenshot capture filenames
- Stable baseline hashing and drift comparison
- Checked-in JSON baseline and screenshot manifest
- Regeneration command with validation gate
- Operations Center Visual QA dashboard and downloads
- Restored explicit sidebar Quick Access contrast styling detected by the new contract

## Validation
- 261 automated tests passed
- 19 page identities and screen modules verified
- 57 unique viewport capture targets verified
- Determinism, round-trip, drift detection, contrast, responsive rules, and checked-in baselines tested
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.11.1.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
