# Visual Capture Directories

Place approved browser-generated PNGs in:

- `baseline/` — reviewed reference captures
- `candidate/` — captures from the build under test

Filenames and dimensions must match `../screenshot_manifest.json`. Run:

```bash
python compare_visual_captures.py
```

Generated diff PNGs and reports are runtime artifacts and are excluded from release packaging.
