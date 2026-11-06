# Backend Resilience Guide

## Retry
Only configured retryable errors are retried. Attempts are bounded and delays use exponential backoff.

## Timeout
Each operation has a maximum runtime. Timeout does not guarantee an underlying external process can be interrupted; backends must still be idempotent.

## Circuit
Closed permits calls. Open rejects calls. After cooldown, half-open permits one probe. Success closes; failure reopens.

## Metrics
Calls, successes, failures, retries, timeouts, latency, last operation, and last error are runtime-only.

## Remote boundary
Remote endpoints and credentials are not included.
