# PeaBox Voice Studio v0.07.0

A governed corporate voice-production workspace with workflow states, ownership, review comments, decision records, approval gates, audit history, executive readiness, portable projects and timelines, multi-provider generation, transcription, and non-destructive audio assembly.

## v0.07.0 Collaboration & Governance

### Governance Center

- Assign a project owner and contributor labels
- Set project risk, target date, review requirement, and approval requirement
- Move through controlled Draft, In Review, Changes Requested, Approved, Published, and Archived states
- View governance readiness and blocking conditions
- Review governance KPIs directly from the corporate dashboard

### Review comments

- Target a project, script block, timeline clip, batch job, transcript, or other reference
- Prioritize comments as Low, Normal, High, or Blocking
- Resolve with a resolution note
- Reopen resolved comments
- Retain comments rather than deleting review history

### Decision register

- Record proposed or decided outcomes
- Capture rationale and actor label
- Mark earlier decisions as superseded while preserving history

### Approval Queue

- Create approval requests with requester, reviewer label, scope, and attestation
- Approve, reject, or withdraw pending requests
- Gate the Approved workflow state when approvals are required
- Retain approval outcomes in the project and audit log

### Governance audit

- Append governance-setting, workflow, comment, decision, and approval actions
- Filter and review audit records
- Include governance records in project JSON and timeline bundles
- Consolidate governance summary and recent audit entries in Activity & History

## Important identity limitation

v0.07.0 is still a local application. Names are local labels, not authenticated identities. Approval records are attestations, not digital signatures. Authentication, permissions, shared storage, and organization-backed roles remain planned for the multi-user architecture.

## Preserved capabilities

All v0.06.0 corporate screens and all v0.05.01 production, timeline, bundle, audio, transcription, provider, and quality features remain available and compatible.

## Windows setup

1. Install 64-bit Python 3.10, 3.11, or 3.12.
2. Extract the ZIP into a new folder.
3. Run `start_windows.bat`.
4. Confirm the sidebar shows `Enterprise workspace · v0.07.0`.
5. Open **Administration → Governance Center** to assign ownership and workflow policy.

## Tests

```bash
python -m unittest discover -s tests -v
```
