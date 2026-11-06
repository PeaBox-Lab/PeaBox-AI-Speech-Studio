# Troubleshooting
## A timeline clip is missing
Open the clip in **Timeline Studio**, upload the replacement WAV under **Relink replacement WAV**, and choose **Relink uploaded WAV**. PeaBox copies it into the output folder and refreshes its metadata and waveform peaks.
## A clip is marked stale
The linked script block changed after rendering. Regenerate and relink the audio, or review the current audio and choose **Acknowledge current block version**.
## Bundle import fails
PeaBox rejects unsafe archive paths, encrypted members, symbolic links, oversized bundles, and non-WAV referenced assets. Recreate the bundle from v0.05.01 rather than manually modifying it.
## Imported asset name changed
A file with the same name already existed. PeaBox created a collision-safe numbered filename and rewrote the imported clip reference automatically.
## The sidebar shows an older version
Stop older Streamlit terminals with `Ctrl+C`, close stale browser tabs, and use the exact Local URL printed by the v0.05.01 launcher.