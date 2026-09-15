# PeaBox Voice Studio v1.0

Fully functional local Python app for offline narration and AI transcription.

## Features
- Offline TTS using system voices
- TXT, MD, DOCX and text-PDF import
- WAV generation, playback and download
- Upload or microphone transcription
- Faster-Whisper local inference
- TXT and SRT exports
- SQLite job history

## Windows
Extract the ZIP and double-click `start_windows.bat`. Python 3.10-3.12 is required. The launcher creates an isolated environment and installs dependencies.

## macOS/Linux
Run `chmod +x start_linux_mac.sh && ./start_linux_mac.sh`. On Ubuntu/Debian, install `espeak-ng libespeak1 ffmpeg`.

## Notes
The first transcription downloads a Whisper model. TTS needs no internet. FFmpeg is recommended for MP3/M4A/video. Data is stored in `data/`; outputs in `outputs/`. This focused release intentionally excludes voice cloning and dubbing to remain reliable on ordinary computers.

## Responsible use
Only process recordings you are authorized to use. Do not create deceptive or impersonating audio.
