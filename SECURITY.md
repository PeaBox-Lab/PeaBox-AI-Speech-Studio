# Security and Data-Safety Notes

- Cloud credentials remain in Streamlit session state and are excluded from projects and bundles.
- Unknown upstream exceptions are not shown verbatim to users.
- Timeline bundles reject traversal paths, symbolic links, encryption, non-WAV assets, excessive file counts, and oversized payloads.
- Imported project paths are cleared unless assets are safely extracted from a validated bundle.
- Kokoro model files receive local checksum sidecars after download and are checked on reuse.
- Governance actor labels and approvals remain local attestations, not authenticated identities or digital signatures.
- The application is intended for trusted local use; it does not provide network authentication, tenant isolation, or OS sandboxing.
