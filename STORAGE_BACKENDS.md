# Storage Backend Contract

## Required operations
put, get, exists, delete, list, copy, move, and audit.

## Local backend
Durable and quota-aware. Uses existing namespaces, object manifest, safe keys, and integrity checks.

## Memory backend
Non-persistent. Used for parity tests and migration validation.

## Migration
Preview first. Apply copies content, verifies SHA-256, and reports per-object failures.

## Remote boundary
A remote backend is not included. Future implementation must require explicit endpoint/credential setup, migration approval, verification, and rollback planning.
