# v0.09.4 Additions and Improvements

## Visual fixes
- Readable Quick Access button labels
- Dark sidebar-specific button surfaces
- Visible hover, keyboard-focus, and disabled states

## Runtime fixes
- Deferred programmatic navigation
- Navigation defaults applied before widget creation
- Project Workspace uses `AppContext.project`

## Regression protection
- Contrast contract tests
- Session-state lifecycle tests
- Modular Project Workspace dependency tests

# v0.09.3 Additions and Improvements

## New workflow APIs
- Timeline workflow facade
- Batch job workflow facade
- Transcription workflow facade

## Architecture controls
- Direct hidden-service imports blocked in facaded screens
- Explicit and unique facade export lists
- Streamlit-free facade modules
- Behavioral parity validation

## Compatibility
- No project migration required
- No navigation or workflow changes
- Cumulative Operations Center retained

# v0.07.4 Additions and Improvements
## Integrity
- Collision-safe output naming
- Asset content-hash validation
- Atomic model downloads and local checksum verification
- Project write locks
## Portability
- Project schema 2
- Migration registry
- Nested project-reference rewrite
- Absolute-path cleanup
- Transactional bundle imports
## Runtime
- Cached model instances
- Compact timeline buffers
- Timeline sample limit
- Reduced bundle limits
## UX and release
- Sanitized errors
- Honest cost terminology
- Updated launcher version
- Direct dependency constraints
