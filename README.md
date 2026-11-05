# PeaBox Voice Studio v0.06.0

A corporate multi-screen voice-production workspace with an executive dashboard, grouped business navigation, portable projects and timelines, multi-provider generation, quality controls, transcription, non-destructive WAV assembly, and consolidated activity history.

## v0.06.0 Corporate UI

### Executive Dashboard

- Active-project KPI cards for script blocks, timeline clips, batch jobs, and transcripts
- Production-readiness table across project, providers, timeline, and system checks
- Four-stage workflow guidance: Prepare, Generate, Assemble, Review
- Consolidated recent activity from renders, timeline exports, and batch jobs
- New-user dashboard showing saved projects and system readiness

### Grouped navigation

- **Overview:** Executive Dashboard, Project Workspace
- **Production:** Script Editor, Speech Generator, Batch Jobs, Timeline Studio
- **Audio & Quality:** Voice Library, Quality Studio, Audio Quality Lab, Transcription Studio
- **Administration:** Provider Setup, System Check, Activity & History
- **Support:** Roadmap & Help

### Corporate visual system

- Enterprise navy/blue visual shell with restrained cyan accents
- Consistent contextual page headers
- Status badges, KPI cards, section titles, callouts, and workflow cards
- Improved whitespace, borders, button styling, metrics, expanders, and content width
- Active project and high-level project counts always visible in the sidebar

### Consolidated Activity & History

One screen now separates:

- Individual renders
- Batch jobs and recorded usage cost
- Timeline exports
- A/B comparisons
- Saved transcript sessions

## Compatibility

All v0.05.01 project data, timeline bundles, jobs, presets, catalogs, transcripts, comparison history, and audio workflows remain compatible. The release changes presentation and navigation, not the persistence format.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar shows `Enterprise workspace · v0.06.0`.
5. Start from **Overview → Executive Dashboard** or **Project Workspace**.

## Tests

```bash
python -m unittest discover -s tests -v
```
