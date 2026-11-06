# PeaBox Voice Studio v0.09.3 Architecture

## Application shell
The compact bootstrap creates `AppContext` and dispatches all navigation through the screen registry.

## Screen modules
Nineteen screens own Streamlit presentation and interaction state. Screens do not import the application bootstrap or peer screens.

## Production facades
`facades.timeline`, `facades.batch`, and `facades.transcription` define stable workflow APIs for the largest production screens. They re-expose established service functions through explicit `__all__` contracts and contain no UI dependency.

## Boundary rule
Facaded screens may call their facade but cannot import the hidden services behind it. Tests enforce this rule and verify parity with the established service implementation.

## Persistence
Project JSON remains authoritative. The repository index is rebuildable. Repairs remain previewed and confirmation-gated. Credentials stay session-only.
