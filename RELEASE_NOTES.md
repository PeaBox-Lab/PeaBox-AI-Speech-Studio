# PeaBox Voice Studio v0.05.00 Release Notes

This release delivers the first non-destructive Timeline Studio phase from the supplied product roadmap. WAV assets become durable project clip records rather than only downloaded files. Each clip stores cached waveform peaks, timing, gain, track, source linkage, and readiness information.

Clips can be arranged sequentially or overlapped at explicit start times. Timeline export validates missing files and incompatible audio formats, mixes enabled clips into a new 16-bit PCM WAV, and creates a portable manifest. Original source audio is never modified.

This is a Streamlit form-based timeline, not yet the later React/Web Audio drag-and-drop interface. The clip and manifest schema provides the migration foundation for that frontend.
