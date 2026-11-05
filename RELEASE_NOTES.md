# PeaBox Voice Studio v0.03.01 Release Notes

This maintenance release makes the v0.03.00 multi-block workflow safer and easier to move between installations. Complete projects can now be exported and imported as JSON. Imports receive a new identity when needed, preventing accidental overwrite of an existing local project.

Batch Production now validates readiness before generation. Empty enabled blocks and other blocking problems are shown as errors; cloud blocks appear as warnings because this release's executable batch path remains Kokoro local. Render manifests include validation results, and completed batch outcomes are saved back to the project for later review.

Block editing adds search/filter, bulk enable/disable, and append-or-replace paragraph import. Existing v0.03.00 projects remain compatible.
