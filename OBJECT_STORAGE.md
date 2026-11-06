# Local Object Storage Guide

## Identity
Objects are identified by namespace and safe relative key. Absolute paths are implementation details.

## Namespaces
outputs, models, backups, quarantine, support, and worker.

## Manifest
The manifest records bytes, SHA-256, content type, and timestamps. Rebuild discovers files; audit compares current files to registered metadata.

## Migration
Always preview first. Apply uses verified imports and reports individual failures.

## Remote boundary
This implementation is local. No remote endpoint or credential is configured.
