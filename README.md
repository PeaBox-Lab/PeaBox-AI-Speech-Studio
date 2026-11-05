# PeaBox Voice Studio v0.07.2

A governed, corporate, local-first voice-production workspace with faster navigation, persistent interface preferences, favorite and recent projects, project-aware shortcuts, multi-provider generation, transcription, audio quality tools, portable timelines, and local review workflows.

## v0.07.2 productivity improvements

- Sidebar Quick Access buttons for Dashboard, Script, Generate, and Timeline
- Dashboard actions for editing, generating, batching, assembling, and governance review
- Favorite projects and recently opened project history
- Quick project access when no project is active
- Persistent default workspace area
- Compact navigation mode
- Reduced-motion mode
- Compact, Standard, or Detailed dashboard modes
- Local preference reset controls

## Preference scope

Interface preferences are stored locally under `data/ui_preferences.json`. They are deliberately separate from projects and are not included in project JSON or portable timeline bundles.

## Cumulative platform

v0.07.2 retains governance, approvals, corporate dashboard, project workspaces, script blocks, cloud and local providers, voice discovery, pronunciation rules, quality processing, transcription, resumable jobs, timelines, portable bundles, and activity history.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar displays `Enterprise workspace · v0.07.2`.
5. Open **Overview → Interface Preferences** to personalize the workspace.

## Validation

```bash
python -m unittest discover -s tests -v
```
