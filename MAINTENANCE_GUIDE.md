# Storage and Maintenance Guide

## Storage inventory

Operations Center reports file counts and bytes for projects, outputs, models, data, and quarantine.

## Orphaned outputs

An output is considered orphaned when no project render, job, clip, comparison, or timeline export references it. Review the preview before choosing quarantine.

PeaBox moves orphaned files into a dated quarantine batch. The source files are not deleted immediately.

## Quarantine

- Restore a batch to return files to the output folder using collision-safe names.
- Permanently delete a batch only after selecting the confirmation checkbox.
- Quarantine actions accept only files directly inside the PeaBox output folder.

## Missing references

Missing references are project records pointing to unavailable files. Relink the intended WAV in Timeline Studio or rerun the relevant generation job.
