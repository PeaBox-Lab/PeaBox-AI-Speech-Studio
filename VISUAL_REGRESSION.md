# Visual Regression Guide

## Generate
Run `python generate_visual_baselines.py`. The command validates contracts before writing JSON.

## Baseline contents
Navigation, page metadata, theme tokens, component selectors, responsive rules, screen labels, widget calls, source hashes, and contrast ratios.

## Capture manifest
Nineteen pages across desktop, tablet, and mobile produce 57 expected PNG filenames.

## Browser boundary
PNG capture and pixel diff require an approved external browser runner. The current release does not install one.

## Review
Do not update a baseline solely to make a failing test pass. Review and approve the intended UI change.
