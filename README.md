# PeaBox Voice Studio v0.10.9
A local-first corporate voice-production workspace with modular screens, bounded workflows, governance, recovery, workers, quotas, object storage, resilient backends, and offline cloud-provider contract testing.

## v0.10.9 Cloud Provider Sandbox
- Deterministic offline Azure Speech adapter
- Deterministic offline Amazon Polly standard and neural adapters
- Deterministic offline Google Cloud TTS adapter
- Voice discovery normalization contract tests
- Provider-specific SSML and speed mapping validation
- Pause-marker compilation and XML escaping checks
- Deterministic MP3-like audio fixtures
- Discovery and synthesis failure injection
- Sanitized call evidence that records profile fields but not values
- Provider Setup contract suite with clear live-service limitations
- No network access or real credentials required

## Validation
- 232 automated tests passed
- Azure, Polly, and Google payload and catalog contracts verified
- Zero-network module loading validated
- All Python sources compile successfully
- Every archive entry is verified against its source hash

## Windows setup
1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the launcher and sidebar display v0.10.9.
5. Keep the `data`, `outputs`, and `models` folders writable.
## Validation
```bash
python -m unittest discover -s tests -v
```
