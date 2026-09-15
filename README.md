# PeaBox Voice Studio 2

Local Kokoro TTS, Faster-Whisper transcription, and optional Azure Speech, Amazon Polly and Google Cloud TTS.

## Windows
Install 64-bit Python 3.11, extract the folder and run `start_windows.bat`. The launcher creates a clean Python 3.11 virtual environment. This avoids current Python 3.13 compatibility problems in audio/ML dependencies.

## Features
- Multiple Kokoro local voices and languages
- Automatic model download on first Kokoro generation
- Dynamic voice discovery from Azure, Polly and Google
- Cloud MP3 generation
- Local transcription to TXT/SRT
- WinError 32 temporary-file lock fix
- Cost estimates per script and provider comparison

Install FFmpeg and add it to PATH for MP3/video transcription. Credentials are held only in the Streamlit session. Do not commit secrets.
