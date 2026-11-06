# Workflow API Guide

## Portfolio facade
Provides project storage, imports, exports, favorites, recents, quick access, and aggregate portfolio metrics.

## Governance facade
Provides governance state, ownership, risk, comments, decisions, workflow transitions, approvals, readiness, cross-project rows, and approval queues.

## Boundary rule
Screens call facades. Facades call established services. Facades contain no Streamlit code and declare explicit public exports.
