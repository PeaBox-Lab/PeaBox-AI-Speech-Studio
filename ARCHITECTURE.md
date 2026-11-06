# PeaBox Voice Studio v0.09.2 Architecture

## Bootstrap and registry
The 31-line bootstrap initializes state, creates `AppContext`, resolves navigation, and dispatches one of 19 registered screen renderers.

## Explicit dependency rule
Each screen imports the exact shared models, configuration values, services, and UI helpers that it uses. There is no wildcard dependency module. Screens cannot import `app.py` or another screen module.

## Dependency budget
A screen may import no more than 25 names. This threshold keeps ownership visible while allowing complex workflows such as Timeline Studio to remain cohesive. Unused imports are rejected.

## Shared context
`AppContext` carries session state and project lifecycle callbacks. It avoids global application imports while keeping screen renderer signatures consistent.

## Persistence and safety
Project JSON remains authoritative. SQLite is a rebuildable index. Operations are recorded as JSON Lines. Repairs are previewed and confirmed. Credentials remain session-only.

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
