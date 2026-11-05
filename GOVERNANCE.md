# PeaBox v0.07.0 Governance Model

## Purpose

The Governance Center provides portable review discipline for local projects before authenticated collaboration is available. It records ownership labels, workflow state, risk, comments, decisions, approvals, and application audit events inside project JSON.

## Identity boundary

Names entered as owner, contributor, author, requester, reviewer, approver, or actor are **local labels**. PeaBox v0.07.0 does not authenticate users, verify organizational authority, create digital signatures, or enforce file permissions. These records support review traceability, not legal identity verification.

## Workflow states

- Draft
- In Review
- Changes Requested
- Approved
- Published
- Archived

Transitions are restricted. When approval is required, a project cannot move to Approved until at least one approval request is recorded as Approved.

## Review comments

Comments include:

- Author label
- Target type and optional target reference
- Low, Normal, High, or Blocking priority
- Open or Resolved status
- Resolution note and resolver label

Comments are retained and reopened rather than deleted.

## Decision register

Decision records retain title, outcome, rationale, author, date, and status. Superseded decisions remain visible with the superseding reason.

## Approval queue

Approval requests retain requester, reviewer label, scope, attestation, status, decision note, and timestamps. Approve, Reject, and Withdraw are local recorded actions.

## Audit log

Governance actions append audit entries with actor label, action, target, timestamp, and details. The application does not expose an audit-entry deletion function. Project exports and timeline bundles carry the log.
