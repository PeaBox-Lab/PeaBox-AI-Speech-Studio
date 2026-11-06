# Storage Policy Guide

## Categories
- outputs: generated WAV, MP3, and processed media
- models: downloaded model and voice files
- recovery: backups, quarantine, and support artifacts
- worker: queue envelopes, events, leases, and daemon state

## Excluded
Project JSON is excluded from quota enforcement.

## Reservations
Reservations reduce remaining capacity before a planned write and prevent overbooking. Release unused reservations promptly.

## Enforcement
Managed writes are checked before commit. Replacements are charged only for growth beyond the current file size.
