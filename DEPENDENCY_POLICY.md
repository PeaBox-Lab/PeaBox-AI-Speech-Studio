# Dependency Policy

`requirements.txt` defines supported version ranges. `constraints.txt` pins the direct application dependencies used by the Windows launcher for more repeatable installation.

This is not yet a full hash-locked transitive dependency set. A future CI release pipeline should generate platform-specific hash-locked files, an SBOM, vulnerability scan results, and signed checksums for every release artifact.
