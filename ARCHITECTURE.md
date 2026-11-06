# PeaBox Voice Studio v0.09.1 Architecture

## Bootstrap
`app.py` configures Streamlit, initializes local runtime state, creates `AppContext`, resolves navigation, and dispatches the registered renderer. It contains no screen implementation.

## Screen registry
`peabox_voice_studio/screens/registry.py` maps every internal navigation identity to exactly one callable `render(ctx)` function.

## Application context
`AppContext` carries version, project store, active project, interface preferences, session-only provider profiles, discovered voice catalogs, configured-provider resolution, and project lifecycle callbacks.

## Persistence
Project JSON is authoritative and portable. The SQLite repository is secondary and can be rebuilt. Operational events are stored as JSON Lines. Maintenance plans are local records, not background schedules.

## Safety boundaries
Repairs are previewed before confirmation. Session credentials do not enter project exports. Project writes retain locking and atomic replacement. Timeline bundles remain the media-inclusive portability format.
