# PeaBox Voice Studio v0.03.12 Release Notes

This patch fixes the interface failure shown in the supplied screenshot. A conditional Streamlit expression returned an internal `DeltaGenerator` object. Streamlit's automatic expression rendering then displayed framework API documentation in the main page, obscuring the real project interface and making the application appear frozen.

The sidebar project-status code now uses an explicit statement-based `if/else`, so no internal UI object is emitted as page content. The sidebar also displays the running PeaBox version, and the Windows launcher prints both the version and launch folder to make stale or older running copies easy to identify.

All v0.03.11 voice catalogs, presets, provider setup, projects, jobs, transcription, and rendering features are preserved.
