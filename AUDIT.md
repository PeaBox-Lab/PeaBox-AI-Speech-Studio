# Code and Product Audit

## Audit basis

This audit uses only the attached v0.2 project export. No web, current market, competitor, pricing, or usage data was consulted. The original export contains one Streamlit application file plus a README, requirements file, and Windows launcher.

## Executive assessment

The attached application proves the core workflow: local Kokoro speech, three cloud speech providers, Faster-Whisper transcription, voice discovery, downloadable results, and planning-cost estimates. Its principal constraint is concentration of UI, provider calls, storage, formatting, and exception handling inside one application module. That shape is workable for a prototype but makes feature growth, testing, and failure isolation harder.

## Findings and actions

| Area | Observed in attached code | Risk or friction | v0.02.01 response |
|---|---|---|---|
| Architecture | UI and all provider logic are in `app.py` | Changes can create cross-feature regressions | Split providers, services, models, and configuration |
| Projects | No persistent project entity in the attached version | Scripts and settings are not reusable as a workspace | Add local JSON projects with master scripts and metadata |
| Generation history | Audio is written to one output folder without project linkage | Users cannot trace renders to scripts or settings | Record the latest 100 renders per project |
| Error experience | Full exceptions are shown in the UI | Technical detail can overwhelm users | Show concise contextual failure messages |
| File safety | Output names are sanitized, but writes are direct | Interrupted writes can leave incomplete files | Add atomic file writes and ID-based project paths |
| Transcription | Temporary descriptor handling is fixed | Large uploads can still exhaust local resources | Add a 500 MB upload limit and retain cleanup retries |
| Subtitle quality | The attached SRT uses decimal seconds rather than standard timestamps | Some players may reject or misread exports | Generate `HH:MM:SS,mmm` timestamps |
| Credentials | Credentials are session-only | Appropriate for local use, but no production secret store | Preserve session-only behavior and document the boundary |
| Cost estimates | Static values are embedded in the application | Estimates can become stale | Label them inherited and require independent verification |
| Performance | Models and clients are constructed inside actions | Repeated setup adds latency | Modularize now; cache/worker improvements are on the roadmap |
| Testing | No tests are included in the attached four-file export | Regressions are difficult to detect | Add lifecycle, path-safety, atomic-write, and subtitle tests |
| Scalability | Local JSON and local output folders are single-user | Not suitable for concurrent multi-user deployment | Define a migration path to a database, object storage, and workers |

## Usability assessment

The original navigation exposes Create Speech, Transcription, Cost Guide, and Help. The next release adds a Projects landing area and visible active-project state so the user can understand where scripts and renders belong. The Master Script becomes the reusable source for Create Speech, reducing copy/paste and making repeat rendering easier.

## Innovation opportunities derived from the code

The current provider coverage and transcription capability support a future integrated production workflow: script blocks, per-block voices, pronunciation controls, batch rendering, subtitle alignment, reusable presets, and comparison rendering. These are roadmap candidates, not claims about market demand.

## Alternative-solution study limitation

No external application data was available in the workspace, so named competitor comparisons and market-size claims are intentionally excluded. `ROADMAP.md` provides an evidence checklist for a later web-enabled study rather than fabricating comparisons.
