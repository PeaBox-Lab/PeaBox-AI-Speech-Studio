# Provider Sandbox Guide

## Purpose
Validate application request and normalization contracts offline.

## Providers
Azure Speech, Amazon Polly standard/neural, and Google Cloud TTS.

## Validates
Normalized voices, required fields, SSML, pauses, escaping, speed, engine, language, deterministic fixtures, and failure paths.

## Does not validate
Credentials, permissions, quotas, billing, network, regional availability, or live service health.

## Security
Profile field names may be recorded; values are never stored in sandbox reports.
