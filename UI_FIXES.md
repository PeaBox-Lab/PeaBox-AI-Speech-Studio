# PeaBox v0.07.1 UI Fixes
## Screenshot findings addressed
### Workspace area selector
The v0.07.0 theme applied white text to every sidebar descendant. Streamlit rendered the workspace selector with a white control surface, producing white-on-white text. v0.07.1 removes the global wildcard color rule and applies explicit colors to:
- The sidebar select surface
- Selected value text
- Input text
- Chevron icon
- Focus border
- Dropdown popover options
### Page banner clipping
The main Streamlit content container started too close to the fixed browser header and did not constrain banner overflow. v0.07.1 adds:
- Increased top clearance
- Width and box-sizing constraints
- Horizontal overflow protection
- Responsive padding
- Safe text wrapping
- Mobile and medium-screen breakpoints
### Navigation clarity
- Adds explicit `WORKSPACE AREA` and `SCREENS` labels
- Strengthens the active screen row with a blue background, cyan left marker, border, and shadow
- Improves hover states and keyboard focus visibility
- Improves muted sidebar text and project-status contrast
- Makes the sidebar scroll independently when content exceeds viewport height
### General polish
- Responsive title sizing
- More balanced content width and horizontal padding
- Improved expander and card overflow behavior
- More consistent button minimum height
- Full-width column stacking on small screens
