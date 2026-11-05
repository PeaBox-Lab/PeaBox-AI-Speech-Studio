# PeaBox Voice Studio v0.07.3

A governed, corporate, local-first voice-production workspace with a searchable command center, first-run onboarding, actionable empty states, fast project continuation, multi-provider speech, transcription, quality processing, portable timelines, and structured local review.

## v0.07.3 Workspace Command Center

- Search all screens by name, purpose, provider, or workflow keyword
- Project-aware command availability
- Safe navigation-only command execution
- Recent command history
- Quick return to frequently used workflows

## Guided onboarding

- Five-step setup progress on the Executive Dashboard
- Tracks project creation, script preparation, provider readiness, first render, and timeline assembly
- Dismissible guide stored in local preferences
- Restore onboarding from Interface Preferences

## Actionable empty states

Key project-dependent screens now explain what is missing and provide a direct navigation action:

- Script Editor
- Batch Jobs
- Timeline Studio
- Governance Center
- Approval Queue
- Command Center project-required results

## Cumulative platform

v0.07.3 preserves the corporate dashboard, responsive theme, interface preferences, favorites and recents, governance and approvals, cloud and local providers, voice catalogs and presets, transcription, quality tools, resumable jobs, Timeline Studio, secure timeline bundles, and full activity history.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `Enterprise workspace · v0.07.3`.
5. Use **Overview → Command Center** to locate any workflow quickly.

## Validation

```bash
python -m unittest discover -s tests -v
```
