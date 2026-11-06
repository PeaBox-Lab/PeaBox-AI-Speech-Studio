# PeaBox Voice Studio v0.11.2

**PeaBox Voice Studio** is a local-first, corporate voice-production workspace built with Python and Streamlit. It combines structured script production, local and cloud text-to-speech, editable transcription, audio-quality workflows, non-destructive timeline assembly, governance, operational recovery, managed background processing, storage controls, and deterministic visual QA in one desktop-oriented application.

The current release is **v0.11.2**. It contains **19 registry-driven screens**, **5 bounded workflow facades**, **50 automated test modules**, **278 passing tests**, and a deterministic visual baseline covering **57 planned desktop, tablet, and mobile captures**.

> PeaBox is intended for trusted local use. Cloud credentials exist only in the current Streamlit session. Governance names and approvals are local labels and attestations—not authenticated identities or digital signatures.

## Table of contents

- [What PeaBox does](#what-peabox-does)
- [Release highlights](#release-highlights)
- [Quick start on Windows](#quick-start-on-windows)
- [Manual installation](#manual-installation)
- [Optional system dependencies](#optional-system-dependencies)
- [Application navigation](#application-navigation)
- [Core workflows](#core-workflows)
- [Architecture](#architecture)
- [Projects and local data](#projects-and-local-data)
- [Speech providers](#speech-providers)
- [Local worker and job processing](#local-worker-and-job-processing)
- [Operations, recovery, and maintenance](#operations-recovery-and-maintenance)
- [Object storage and capacity management](#object-storage-and-capacity-management)
- [Governance and approvals](#governance-and-approvals)
- [Visual regression and quality gates](#visual-regression-and-quality-gates)
- [Security model](#security-model)
- [Testing and validation](#testing-and-validation)
- [Troubleshooting](#troubleshooting)
- [Known limitations](#known-limitations)
- [Roadmap](#roadmap)
- [Project documentation](#project-documentation)

## v0.11.2 — PNG pixel-diff reports

PeaBox now validates approved browser-generated PNG capture sets against the 57-target screenshot manifest. The release adds:

- baseline and candidate capture inventories;
- PNG signature, decoding, and expected-dimension validation;
- exact and threshold-based pixel comparison;
- changed-pixel count and percentage;
- maximum channel delta and mean RGB delta;
- highlighted diff PNGs;
- JSON and ZIP diff reports;
- CLI exit codes for success, visual failure, and incomplete capture sets;
- Visual QA readiness and comparison controls.

Place captures under:

```text
visual_baselines/captures/baseline/
visual_baselines/captures/candidate/
```

Then run:

```bash
python compare_visual_captures.py
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Every capture passed the configured thresholds |
| `1` | At least one valid capture exceeded the pixel threshold |
| `2` | A capture set is missing, invalid, extra, or dimensionally incorrect |

PeaBox compares PNGs but does not install or launch a browser. Screenshot generation remains an approved external browser-runner step.

## What PeaBox does

PeaBox supports an end-to-end narration and voice-production workflow:

1. Create or import a portable project.
2. Write a master script and split it into production blocks.
3. Configure provider, language, voice, speed, direction notes, pronunciation rules, and pause markers.
4. Generate an individual render or create a resumable batch job.
5. Inspect and process WAV audio, including normalization and silence trimming.
6. Compare local voices using A/B generation.
7. Arrange durable clips in a non-destructive timeline and export a merged WAV master.
8. Transcribe local audio or video, edit timestamped segments, repair timing, and export TXT, SRT, or VTT.
9. Record ownership, risks, comments, decisions, approvals, and workflow transitions.
10. Monitor project health, storage capacity, worker status, backups, maintenance plans, resilience profiles, and visual contracts.

## Release highlights

### v0.11.1 — Deterministic UI baselines

- Navigation and page-metadata snapshots for all 19 pages
- Theme-token and reusable-component contract snapshots
- Per-screen labels, Streamlit widget-call counts, source line counts, and source hashes
- Contrast checks for sidebar controls and content cards
- Desktop, tablet, and mobile screenshot manifest
- 57 planned screenshot filenames
- Stable baseline hashing and structural drift comparison
- Operations Center **Visual QA** tab

### Cumulative platform highlights

- Modular screen registry and shared application context
- Bounded workflow APIs for portfolio, governance, batch, timeline, and transcription
- Durable local Kokoro worker queue and managed foreground daemon
- Live worker progress, events, cancellation, synchronization, leases, and stale recovery
- Configurable storage quotas and capacity reservations
- Local object-storage abstraction and pluggable storage backend contract
- Local and non-persistent memory backends
- Backend retries, timeouts, circuit breaking, health reports, and metrics
- Durable reviewed resilience profiles
- Deterministic offline Azure, Polly, and Google provider sandboxes
- Operations recovery, backups, quarantine, maintenance, and retention controls

## Quick start on Windows

### Requirements

- 64-bit Python **3.10**, **3.11**, or **3.12**
- A writable extracted application directory
- Internet access during initial dependency installation
- Internet access during first Kokoro model download, unless model files are already present

### Start the application

1. Extract the release ZIP into a new folder.
2. Double-click:

```text
start_windows.bat
```

3. The launcher:
   - locates a compatible Python installation;
   - creates or reuses `.venv`;
   - upgrades packaging tools;
   - installs `requirements.txt` with `constraints.txt`;
   - starts Streamlit with `app.py`.
4. Open the Local URL printed in the terminal.
5. Confirm the sidebar shows **v0.11.2**.

### Start the local worker daemon

Run the application launcher at least once so `.venv` exists, then double-click:

```text
start_worker_windows.bat
```

The worker remains visible in a foreground terminal. Press `Ctrl+C` for foreground shutdown, or use the managed daemon controls described later in this README.

## Manual installation

From the extracted project directory:

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt -c constraints.txt
python -m streamlit run app.py
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt -c constraints.txt
python -m streamlit run app.py
```

The application is tested against Python 3.10–3.12. Other versions are not supported by the supplied launcher.

## Optional system dependencies

### FFmpeg

FFmpeg is required for compressed media transcription formats such as MP3, M4A, OGG, MP4, MOV, MKV, and WebM. Plain WAV transcription can operate without FFmpeg.

Check availability:

```bash
ffmpeg -version
```

Use **Administration → System Check** to see whether PeaBox can locate FFmpeg.

### Local Kokoro files

PeaBox downloads these files on first local generation:

```text
models/kokoro-v1.0.int8.onnx
models/voices-v1.0.bin
```

Checksum sidecars are generated locally and verified on reuse.

## Application navigation

PeaBox uses grouped workspace navigation.

| Area | Screen | Purpose |
|---|---|---|
| Overview | Executive Dashboard | Portfolio status, readiness, onboarding, quick actions, recent activity |
| Overview | Project Workspace | Create, open, import, export, rename, and maintain projects |
| Overview | Command Center | Search screens and project-aware safe navigation commands |
| Overview | Interface Preferences | Navigation density, motion, startup area, dashboard detail |
| Overview | Portfolio Operations | Governance portfolio, recovery, maintenance, storage, backends, resilience, profiles, and Visual QA |
| Production | Script Editor | Provider-aware script blocks, presets, pacing, direction, ordering, inclusion |
| Production | Speech Generator | Generate and review one local Kokoro output |
| Production | Batch Jobs | Validate, create, run, queue, recover, cancel, and package production jobs |
| Production | Timeline Studio | Arrange durable WAV clips and export a merged production master |
| Audio & Quality | Voice Library | Search local and session-discovered cloud voices; manage presets |
| Audio & Quality | Quality Studio | Pronunciation dictionary, pause markers, processed-text previews |
| Audio & Quality | Audio Quality Lab | WAV inspection, normalization, trimming, and A/B comparisons |
| Audio & Quality | Transcription Studio | Local transcription, editing, timing repair, sessions, and exports |
| Administration | Governance Center | Ownership, risk, comments, decisions, workflow transitions |
| Administration | Approval Queue | Request and decide local approval attestations |
| Administration | Provider Setup | Session-only cloud credentials, voice discovery, offline sandboxes |
| Administration | System Check | Python, FFmpeg, models, and storage diagnostics |
| Administration | Activity & History | Renders, jobs, exports, comparisons, transcripts, and governance history |
| Support | Roadmap & Help | Delivered capabilities and planned architecture |

The sidebar also provides **Dashboard**, **Script**, **Generate**, and **Timeline** Quick Access controls.

## Core workflows

### 1. Create and prepare a project

Open **Project Workspace** and create a project with a name and description. The project contains:

- master script;
- ordered script blocks;
- production settings;
- render history;
- batch jobs;
- timeline clip records;
- transcript sessions;
- comparisons and presets;
- governance data.

Project files are stored as JSON and are the authoritative portable metadata source.

### 2. Structure the script

Open **Script Editor** to:

- add blank blocks;
- import paragraphs from the master script;
- enable or disable blocks;
- reorder and duplicate blocks;
- choose provider, voice, language, and speed;
- save reusable voice/direction presets;
- attach direction notes;
- preview processed text;
- insert and validate pause markers.

### 3. Configure pronunciation and pauses

In **Quality Studio**, add project pronunciation rules and preview provider-aware text preparation.

Pause markers use this format:

```text
[[pause:1.5]]
```

Cloud providers receive compiled SSML breaks. Kokoro receives a punctuation-based local approximation.

### 4. Generate speech

Use **Speech Generator** for a single Kokoro render, or **Batch Jobs** for multi-block production.

Repeated output names do not overwrite existing files. PeaBox uses collision-safe numbered filenames.

### 5. Run batch production

A batch job stores item-level provider, text, voice, language, speed, status, attempts, output reference, errors, and planning-rate estimates.

Available actions include:

- Run/resume inline
- Retry failed
- Cancel queued
- Reopen cancelled
- Duplicate job
- Delete job
- Download output ZIP
- Queue eligible Kokoro jobs for the local worker

Recorded planning-rate usage is an application estimate based on successful characters. It is **not** a cloud-provider invoice.

### 6. Assemble a timeline

**Timeline Studio** supports:

- durable WAV clip records;
- tracks, start offsets, and gain;
- sequential arrangement and configurable gaps;
- waveform peak previews;
- stale-source detection;
- current-file SHA-256 validation;
- missing-file relinking;
- metadata refresh;
- source-version acknowledgement;
- manifest export;
- portable timeline bundle export;
- bounded-memory merged WAV creation.

Original audio files are not modified by timeline editing.

### 7. Transcribe media

**Transcription Studio** supports local Faster-Whisper transcription with:

- model selection;
- automatic or selected language;
- editable timestamped segments;
- speaker/search filtering fields;
- overlap and timing validation;
- automatic timing repair;
- saved project transcript sessions;
- TXT, SRT, and VTT exports.

## Architecture

### High-level design

```text
app.py
  └── creates AppContext
      ├── resolves grouped navigation
      └── dispatches screen renderer

peabox_voice_studio/
  ├── screens/       19 Streamlit screen modules
  ├── facades/       bounded workflow APIs
  ├── services/      persistence, jobs, audio, timeline, governance, operations
  ├── providers/     Kokoro, cloud providers, offline provider sandboxes
  ├── context.py     shared renderer contract
  ├── models.py      Project and ScriptBlock models
  ├── ui.py          navigation, theme, components, visual contracts
  └── config.py      version, paths, size limits, operational locations
```

### Bootstrap

`app.py` is intentionally small. It:

1. configures Streamlit;
2. loads local interface preferences;
3. initializes the project store and session-only provider state;
4. builds `AppContext`;
5. resolves the selected page;
6. dispatches the registered renderer.

### Screen registry

Every navigation identity maps to exactly one `render(ctx)` function. Screens do not import the application bootstrap or peer screen implementations.

### Workflow facades

Bounded APIs isolate complex screen workflows:

- `facades/portfolio.py`
- `facades/governance.py`
- `facades/batch.py`
- `facades/timeline.py`
- `facades/transcription.py`

### Services

The service layer includes:

- project locking and atomic writes;
- migrations and import-reference repair;
- resumable jobs;
- worker queue and daemon lifecycle;
- audio processing and timeline mixing;
- transcription and subtitles;
- governance and approvals;
- recovery and maintenance;
- quotas, reservations, object storage, backend resilience, and profiles;
- deterministic visual baselines.

## Projects and local data

### Data directories

```text
data/
  projects/                  authoritative project JSON
  backups/                   SQLite recovery points
  quarantine/                reversible generated-output quarantine
  support/                   generated support artifacts
  worker/                    queue envelopes, events, daemon state
  peabox.db                  rebuildable project metadata index
  maintenance.json           local maintenance plans
  storage_policy.json        capacity policy
  storage_reservations.json  active capacity reservations
  object_manifest.json       logical object metadata
  resilience_profiles.json   governed resilience profiles

outputs/                     generated and processed audio
models/                      Kokoro model and voice files
visual_baselines/            checked-in UI baseline and capture manifest
```

### Source of truth

- Project JSON is authoritative.
- SQLite is a secondary, rebuildable index.
- Metadata snapshots do not include external media.
- Timeline bundles are the media-inclusive portability format.

### Project import behavior

Imported projects receive a collision-safe identity unless identity preservation is explicitly safe. Nested job references are rewritten. Non-portable output paths are removed. Rendered job items with removed paths are marked for recovery or rerun.

## Speech providers

### Kokoro local

- Local WAV output
- Voice, language, and speed controls
- Automatic model download
- Checksum verification
- Cached engine instance
- Supported by inline execution and the local worker queue

### Azure Speech

- Session-only API key and region
- Voice discovery
- MP3 generation
- Voice, language, and speed controls

### Amazon Polly

- Standard and neural modes
- Session-only AWS access key, secret, optional token, and region
- Voice discovery
- MP3 generation

### Google Cloud Text-to-Speech

- Session-only service-account JSON
- Voice discovery with optional language filter
- MP3 generation

### Offline provider sandbox

Provider Setup contains deterministic offline sandboxes for:

- Azure Speech
- Amazon Polly standard
- Amazon Polly neural
- Google Cloud Text-to-Speech

The sandbox validates normalized catalogs, SSML, pauses, escaping, language, speed, engine, deterministic audio fixtures, and failure paths. It does **not** validate real credentials, permissions, quotas, billing, regions, network access, or live service availability.

## Local worker and job processing

### Queue security boundary

The durable local worker accepts **Kokoro local jobs only**. Cloud credentials remain session-only and are never written into queue files.

### One-shot worker

```bash
python worker_local.py --once
```

### Managed daemon

```bash
python worker_local.py --daemon
```

### Daemon commands

```bash
python worker_local.py --status
python worker_local.py --pause
python worker_local.py --resume
python worker_local.py --drain
python worker_local.py --shutdown
```

### Worker guarantees

- one active daemon claim;
- durable heartbeat and status;
- exclusive per-job leases;
- stale-daemon and stale-job recovery;
- item-started and item-finished events;
- progress calculation;
- cancellation;
- explicit synchronization back into project JSON.

The Windows daemon launcher reuses the existing `.venv` and does not install or upgrade packages.

## Operations, recovery, and maintenance

**Portfolio Operations** consolidates:

- cross-project ownership and risk;
- open comments and pending approvals;
- readiness status;
- SQLite integrity and backup creation;
- metadata snapshots;
- maintenance plans;
- retention previews;
- capacity policies;
- logical object manifests;
- storage backends and migrations;
- resilience probes and profiles;
- Visual QA.

### Recovery controls

- Project-health findings and previewed safe repairs
- Rebuildable SQLite index
- Integrity-checked database backups
- Rollback copy before database restore
- Reversible quarantine for generated output files
- Collision-safe quarantine restore
- Sanitized support bundles

### Maintenance and retention

Maintenance plans support Daily, Weekly, Monthly, and Quarterly frequencies with due, overdue, paused, completion, notes, and history states.

Retention is preview-first and limited to approved recovery directories. It can target:

- database backups beyond the keep-latest count;
- old metadata records for already-restored quarantine items;
- old generated support artifacts.

Project JSON, active outputs, and models are outside retention cleanup.

## Object storage and capacity management

### Capacity policies

PeaBox supports separate local limits for:

- generated outputs;
- downloaded models;
- backups and recovery artifacts;
- worker queue, events, and daemon state.

Policies support warning thresholds, hard limits, overwrite-aware growth calculations, and capacity reservations. Project JSON is excluded from quota enforcement.

### Logical object storage

Managed files can be addressed by namespace and safe key:

```text
outputs:narration/chapter-01.wav
models:kokoro-v1.0.int8.onnx
backups:peabox_20261106.db
worker:jobs/<queue-id>.json
```

Object keys reject traversal, absolute paths, empty segments, and unsupported characters.

Supported operations include:

- put and get;
- verified import;
- list and exists;
- copy and move;
- permanent delete;
- manifest rebuild;
- missing, size, and hash drift audit;
- migration preview and application.

### Storage backends

The formal backend contract defines:

- `put`
- `get`
- `exists`
- `delete`
- `list`
- `copy`
- `move`
- `audit`

Built-in backends:

- **local** — durable, manifest-backed, and quota-aware;
- **memory** — non-persistent validation backend.

No remote backend or remote-storage credentials are configured in v0.11.1.

### Backend resilience

Any backend can be wrapped with:

- bounded retries;
- configurable delay and backoff;
- operation timeout;
- closed/open/half-open circuit breaker;
- cooldown recovery;
- runtime metrics;
- health reports.

### Governed resilience profiles

Profiles persist only retry/timeout/circuit settings—never credentials. The lifecycle is:

```text
Draft → In Review → Approved → Active
          ↘ Changes Requested
Active → Approved or Archived
Archived → Draft
```

The approving reviewer label must differ from the creator label. Only one profile per backend can be Active. Actor labels are local labels, not authenticated identities.

## Governance and approvals

### Project governance

- owner and contributors;
- risk level;
- target date;
- review and approval requirements;
- controlled workflow transitions;
- audit history.

Workflow states:

```text
Draft
In Review
Changes Requested
Approved
Published
Archived
```

### Review comments

Comments can target a project, script block, timeline clip, batch job, transcript, or other reference. Comments can be resolved and reopened; they are retained rather than silently deleted.

### Decision register

Decisions store title, outcome, rationale, status, author label, and timestamps. Superseded decisions remain visible.

### Approval Queue

Approval requests store requester, reviewer label, scope, attestation, status, decision note, and timestamps. Approval records are local attestations, not digital signatures.

## Visual regression and quality gates

Generate deterministic baselines:

```bash
python generate_visual_baselines.py
```

The baseline records:

- navigation groups and page metadata;
- theme tokens and component selectors;
- sidebar visual contracts;
- responsive media queries;
- screen labels and Streamlit call counts;
- screen line counts and source hashes;
- contrast ratios.

The screenshot manifest defines three viewports per page:

| Viewport | Size |
|---|---:|
| Desktop | 1440 × 1000 |
| Tablet | 1024 × 900 |
| Mobile | 390 × 844 |

With 19 pages, the manifest contains 57 planned PNG captures. Actual browser capture and pixel-diff execution require an approved external browser runner; PeaBox does not silently install one.

## Security model

### Credentials

- Cloud credentials stay in Streamlit session state.
- Credentials are excluded from project JSON, exports, bundles, queues, support bundles, and resilience profiles.
- Offline sandbox reports record profile field names, not credential values.

### File safety

- Atomic file replacement
- Local project file locks
- Collision-safe generated filenames
- Path-safe imports
- Bundle traversal rejection
- Symlink and encrypted-member rejection
- File-count and size limits
- WAV-only referenced bundle assets
- Content-hash validation
- Quota preflight before managed writes

### Error handling

Expected safe errors may be shown to users. Unknown exceptions are replaced with a generic user-safe message. Error text is bounded.

### Trust boundary

PeaBox is designed for trusted local operation. It does not provide:

- user authentication;
- tenant isolation;
- OS-level sandboxing;
- authenticated governance identities;
- remote object credentials;
- silent background-service installation.

## Testing and validation

The v0.11.2 release was validated with:

- **278 passing automated tests**;
- **50 test modules**;
- full Python source compilation;
- 19-page smoke execution without an active project;
- deterministic UI-baseline regeneration;
- file-by-file source/ZIP SHA-256 equality;
- ZIP corruption check.

### Run the recommended test suite

```bash
python -m pytest -q --disable-warnings
```

### Run using unittest discovery

```bash
python -m unittest discover -s tests -v
```

### Compile all Python files

```bash
python -m compileall -q .
```

### Regenerate visual baselines

```bash
python generate_visual_baselines.py
```

Do not regenerate a baseline solely to make a failing test pass. Review the intended UI change first.

## Troubleshooting

### The sidebar shows an older version

- Stop older Streamlit terminals with `Ctrl+C`.
- Close stale browser tabs.
- Start the launcher from the newly extracted release folder.
- Open the exact Local URL printed by that terminal.

### A timeline clip is missing

Open the clip in Timeline Studio, upload the replacement WAV, and choose **Relink uploaded WAV**.

### A timeline clip is stale

The linked script block changed after rendering. Regenerate and relink the audio, or review the existing audio and acknowledge the current block version.

### Bundle import fails

The archive may contain an unsafe path, encrypted member, symbolic link, unsupported referenced asset, excessive files, or an oversized payload. Re-export the bundle from PeaBox rather than editing the ZIP manually.

### Compressed transcription fails

Install FFmpeg and confirm **System Check** reports it as Ready.

### A quota blocks generation

Open **Portfolio Operations → Capacity**. Free managed storage, release unused reservations, apply an approved retention preview, or raise the relevant category limit.

### Worker queue does not progress

1. Check daemon status.
2. Start or resume the worker.
3. Recover stale leases if a worker was interrupted.
4. Sync worker progress into the project.

### Cloud generation fails after the offline sandbox passes

Check live credentials, permissions, region, quota, billing, network access, and provider service status. Sandbox success does not verify those live conditions.

### Visual baseline validation fails

Review the reported navigation, theme, component, responsive, or contrast contract. Fix the regression or deliberately approve and regenerate the baseline.

## Known limitations

- Streamlit is the current UI runtime; this is not a multi-user web service.
- Cloud credentials are session-only and must be re-entered after restart.
- The durable local worker processes Kokoro jobs only.
- Remote object storage is not configured.
- The memory storage backend is non-persistent and must not be used as a backup.
- Governance identities and approvals are not authenticated.
- Maintenance plans are evaluated when the screen opens; they are not OS-scheduled tasks.
- Actual PNG capture and pixel comparison require an external approved browser runner.
- Planning-rate cost figures are not provider invoices.

## Roadmap

The next documented milestones are:

- approved browser-based PNG capture and pixel-diff reports;
- live provider integration tests with explicit test credentials and cost guardrails;
- optional remote storage with credentials, approval, verification, and rollback;
- authenticated identities for governance actions.

Experimental areas such as voice cloning, consent ledgers, watermarking, real-time agents, or regulatory claims require separate licensing, consent, security, jurisdiction, and authoritative-guidance review before implementation.

## Project documentation

The release includes focused documentation for specific areas:

| File | Purpose |
|---|---|
| `USER_GUIDE.md` | Feature usage by release |
| `HELP.md` | Operational help and limitations |
| `TROUBLESHOOTING.md` | Common recovery procedures |
| `SECURITY.md` | Security and data-safety boundaries |
| `GOVERNANCE.md` | Local governance model |
| `WORKFLOW_API.md` | Portfolio, governance, timeline, batch, and transcription facades |
| `WORKER_GUIDE.md` | Queue and managed daemon lifecycle |
| `STORAGE_POLICY.md` | Quotas and reservations |
| `OBJECT_STORAGE.md` | Logical keys, manifest, audit, and migration |
| `STORAGE_BACKENDS.md` | Backend contract and migration |
| `BACKEND_RESILIENCE.md` | Retry, timeout, and circuit behavior |
| `RESILIENCE_PROFILES.md` | Reviewed durable resilience policies |
| `PROVIDER_SANDBOX.md` | Offline provider-contract testing |
| `VISUAL_REGRESSION.md` | Deterministic baselines and capture manifest |
| `ROADMAP.md` | Delivered and planned capabilities |
| `CHANGELOG.md` | Cumulative changes |
| `VERSION_HISTORY.md` | Release-by-release summary |

## Distribution and licensing

No license file is included in the current release. Add an appropriate license before public redistribution, and review the licenses and terms of all model files, voices, Python dependencies, and cloud services used by your deployment.
