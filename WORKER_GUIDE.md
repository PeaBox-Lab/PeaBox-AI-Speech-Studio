# Local Worker Guide

## Scope
The worker processes Kokoro local jobs only. Cloud credentials are not persisted.

## Run once
```bash
python worker_local.py --once
```

## Lifecycle
1. Queue a validated Kokoro job.
2. Worker acquires an exclusive lease.
3. Each item emits started and finished events.
4. Durable progress is updated.
5. Worker releases the lease.
6. User synchronizes results into the project.

## Recovery
Expired leases can be recovered from Batch Jobs. Running items are returned to queued state with a recovery note.
