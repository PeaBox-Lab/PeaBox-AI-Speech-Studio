# PeaBox Voice Studio v0.10.7
A local-first corporate voice-production workspace with modular screens, bounded workflows, governance, recovery, maintenance, managed workers, storage quotas, logical objects, and pluggable storage backends.

## v0.10.7 Pluggable Storage Backends
- Formal `StorageBackend` contract
- Durable local backend adapter over existing namespaces and manifests
- Non-persistent in-memory backend for validation and testing
- Backend registry and factory validation
- Contract reports for required operations
- Cross-backend migration previews
- Hash-verified backend migrations with per-item failures
- Local/memory behavior and metadata parity tests
- Operations Center backend contract and migration validation
- No remote backend or credentials configured

## Validation
- 205 automated tests passed
- Local and memory backend parity verified
- Backend registration, conflicts, filters, migration, and audit behavior tested
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.7.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
