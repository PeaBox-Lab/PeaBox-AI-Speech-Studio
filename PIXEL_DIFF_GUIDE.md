# PNG Pixel-Diff Guide

## Directories
- `visual_baselines/captures/baseline/`
- `visual_baselines/captures/candidate/`
- `visual_baselines/diffs/`

## Compare
```bash
python compare_visual_captures.py
```

## Policies
- `--pixel-threshold`: maximum channel delta ignored per pixel.
- `--allowed-changed-percent`: maximum percentage of changed pixels accepted.

## Exit codes
- 0: passed
- 1: visual differences exceeded policy
- 2: capture set not ready

## Review rule
Do not update the reviewed baseline only to clear a failure. Inspect the PNG and diff report, confirm the UI change is intended, and then approve a new baseline.
