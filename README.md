# PeaBox Voice Studio v0.10.6
A local-first corporate voice-production workspace with modular screens, bounded workflow APIs, governance, recovery, maintenance, managed workers, storage quotas, and a local object-storage abstraction.

## v0.10.6 Local Object Storage Layer
- Safe logical keys independent of absolute local paths
- Namespaces for outputs, models, backups, quarantine, support, and worker data
- Atomic object writes with existing quota preflight
- Verified file import with optional move semantics
- Copy, move, delete, read, register, and unregister operations
- Durable metadata manifest with size, SHA-256, content type, and timestamps
- Manifest rebuild and integrity audit
- Legacy-directory migration preview and verified application
- Operations Center object browser and guarded controls
- Local-only backend; no remote credentials or cloud storage configuration

## Validation
- 191 automated tests passed
- Traversal and unsupported-key rejection verified
- Manifest drift, missing objects, imports, copy/move/delete, and migrations tested
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.6.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
