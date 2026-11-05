# Troubleshooting

## Confirm the running release

The sidebar must show `PeaBox v0.04.01`. If it shows another version, stop older Streamlit terminals with `Ctrl+C`, close old browser tabs, and use the exact Local URL printed by the new launcher.

## Compressed media cannot be transcribed

Open **System Check**. MP3, M4A, OGG, MP4, MOV, MKV, and WebM require FFmpeg. WAV can be transcribed without it. After installing FFmpeg and adding it to PATH, restart PeaBox.

## Transcript export buttons are unavailable

Review the timing validation table. Subtitle export and project saving are blocked if segments overlap or have zero duration. Use **Repair timing automatically**, review the repaired values, then export.

## Pronunciation output is unexpected

Open **Quality Studio** and review duplicate or overlapping rule diagnostics. Rules are applied in displayed order, so overlapping sources can affect the result.

## The page shows `DeltaGenerator` documentation

That issue was fixed in v0.03.12 and remains covered by regression tests. If it appears, an older release is still running. Stop all older Streamlit terminals and start this release from its own folder.
