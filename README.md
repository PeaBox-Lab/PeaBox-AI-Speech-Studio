# PeaBox Voice Studio v0.03.10

A local-first Streamlit workspace for portable projects, provider-aware script blocks, resumable multi-provider jobs, Kokoro production, and Faster-Whisper transcription.

## v0.03.10 highlights

- Session-only setup for Azure Speech, Amazon Polly, and Google Cloud TTS
- Credentials are never written to project JSON, exported projects, job manifests, or logs
- Provider-specific language codes and voice identifiers on cloud blocks
- Provider readiness validation before job creation
- Persistent job snapshots with queued, running, rendered, failed, and cancelled item states
- Resume queued jobs after reopening a project
- Retry failed items without repeating successful renders
- Cancel queued items
- Download completed job audio and job metadata in one ZIP
- Estimated cost at job creation and recorded usage cost for successful generations
- Job history limited to the most recent 20 records per project

## Important behavior

The Streamlit session must still contain the relevant provider credentials when a saved cloud job is resumed. Project files contain provider names and generation settings, but never secret values.

Recorded usage cost is calculated from successfully rendered character counts using the configured planning rate. It is useful for project tracking but is not a provider invoice and may differ from billed usage, taxes, free tiers, regional pricing, or contracts.

Jobs are resumable and persistent, but execution is still initiated from the UI and runs in the application process. A separate background worker and live progress channel remain planned for the next architecture stage.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP.
3. Run `start_windows.bat`.
4. Install FFmpeg and add it to PATH for compressed audio/video transcription.

## Workflow

1. Open Provider Setup and configure only the providers needed for the current session.
2. Create or import a project and configure its blocks.
3. Enter exact cloud language codes and provider voice IDs on cloud blocks.
4. Open Batch Production and resolve readiness errors.
5. Create a persistent job, then run or resume it.
6. Retry failed items, cancel queued work, or download completed job outputs.

## Tests

```bash
python -m unittest discover -s tests -v
```
