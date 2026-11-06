# Retention Policy

## Eligible categories
- Database backups beyond the configured keep-latest count
- Metadata records for quarantine items already restored and older than the configured threshold
- Generated support artifacts older than the configured threshold

## Excluded categories
Project JSON, active generated outputs, model files, source code, current quarantine payloads, and arbitrary files are not eligible.

## Workflow
1. Configure thresholds.
2. Review the exact preview.
3. Confirm permanent removal.
4. Apply the preview.
5. Review removed and skipped results.

The application does not perform retention in the background.
