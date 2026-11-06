# v0.09.2 Additions and Improvements

## Screen ownership
- Explicit imports for all 19 screen modules
- Removed broad wildcard dependency sharing
- No screen-to-screen implementation dependencies
- No screen dependency on the application bootstrap

## Architecture controls
- 25-name maximum import budget per screen
- Automated unused-import detection
- Automated wildcard-import rejection
- Automated peer-screen isolation checks

## Validation
- 170 passing automated tests
- Complete compilation and archive-integrity verification

# v0.09.1 Additions and Improvements

## Architecture
- Dedicated module for every navigation page
- 31-line application bootstrap
- Expanded shared application context
- Single complete screen registry
- Enforced one-page/one-renderer mapping

## Operations
- Project health summary and issue details
- Preview-only safe repair plans
- Explicit repair confirmation
- Rebuildable project metadata index
- Local maintenance plans and completion evidence
- Structured operations event viewer

## Quality
- Full page smoke coverage
- Module-boundary checks
- Repository and operations service tests
- 165 passing automated tests

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
