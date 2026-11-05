# PeaBox Voice Studio v0.02.02 Release Notes

This maintenance release fixes Windows startup when Python 3.11 is not installed. `start_windows.bat` now delegates to a PowerShell launcher that searches for Python 3.12, 3.11, and 3.10 in that order, then checks the `python` and `python3` commands. It creates the virtual environment with the first compatible interpreter found.

A valid existing `.venv` is reused. An incomplete environment or one outside the supported 3.10–3.12 range is rebuilt. If no compatible Python is available, the launcher exits with clear instructions rather than silently skipping environment creation or attempting an unattended system installation.

All v0.02.01 project workspace, provider, transcription, render-history, audit, and roadmap capabilities are preserved.
