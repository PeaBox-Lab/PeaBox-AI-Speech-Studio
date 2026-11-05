# Detailed Release Notes — v0.07.3

## Design objective

PeaBox had grown to many dedicated screens. Grouped navigation and quick actions improved daily use, but new and occasional users still needed to know where a task lived. v0.07.3 adds task-oriented discovery without restructuring the underlying features again.

## Command safety

Commands only navigate to existing screens. They do not delete data, submit approvals, generate paid cloud audio, or change project content. Project-dependent results are disabled until prerequisites are available.

## Onboarding behavior

Onboarding derives progress from current project state and provider availability. Dismissing the guide changes only local interface preferences. It can be restored at any time.
