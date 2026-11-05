# Troubleshooting

## The page shows `DeltaGenerator` documentation

This was caused by a Streamlit expression in releases through v0.03.11. Streamlit interpreted the returned UI object as content and rendered its internal API documentation. v0.03.12 replaces that expression with a normal `if/else` statement.

## The sidebar does not show Provider Setup or Voice Library

An older release is still running. Stop its terminal with `Ctrl+C`, close the browser tab, extract v0.03.12 into a new folder, and run the new folder's `start_windows.bat`. The sidebar should display `PeaBox v0.03.12`.

## Buttons appear not to respond

1. Confirm the sidebar version says `PeaBox v0.03.12`.
2. Stop every older Streamlit terminal with `Ctrl+C`.
3. Start only the v0.03.12 launcher.
4. Open the Local URL printed by that launcher.
5. If port 8501 belongs to an older process, the new launcher may print a different port. Use the exact URL it prints.

## Clean restart

Deleting `.venv` is normally unnecessary. If dependency installation was interrupted, close the app, delete only the extracted release folder's `.venv`, and run `start_windows.bat` again. Projects under `data/projects` should be backed up before replacing an extracted folder.
