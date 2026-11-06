from uuid import uuid4
from peabox_voice_studio.models import Project, utc_now
WORKFLOW_STATES = ["Draft", "In Review", "Changes Requested", "Approved", "Published", "Archived"]
RISK_LEVELS = ["Low", "Medium", "High", "Critical"]
APPROVAL_STATES = ["Pending", "Approved", "Rejected", "Withdrawn"]
ALLOWED_TRANSITIONS = {
    "Draft": {"In Review", "Archived"},
    "In Review": {"Draft", "Changes Requested", "Approved", "Archived"},
    "Changes Requested": {"Draft", "In Review", "Archived"},
    "Approved": {"In Review", "Published", "Archived"},
    "Published": {"In Review", "Archived"},
    "Archived": {"Draft"},
}
def governance(project: Project) -> dict:
    data = project.settings.setdefault("governance", {})
    data.setdefault("owner", "")
    data.setdefault("contributors", [])
    data.setdefault("status", "Draft")
    data.setdefault("risk_level", "Low")
    data.setdefault("due_date", "")
    data.setdefault("review_required", True)
    data.setdefault("approval_required", True)
    data.setdefault("comments", [])
    data.setdefault("decisions", [])
    data.setdefault("approvals", [])
    data.setdefault("audit_log", [])
    return data
def update_project_governance(project: Project, actor: str, owner: str, contributors: list[str], risk_level: str, due_date: str, review_required: bool, approval_required: bool) -> dict:
    data = governance(project)
    if risk_level not in RISK_LEVELS:
        raise ValueError("Invalid risk level")
    before = {key: data.get(key) for key in ("owner", "contributors", "risk_level", "due_date", "review_required", "approval_required")}
    data.update({
        "owner": owner.strip()[:120],
        "contributors": _clean_names(contributors)[:50],
        "risk_level": risk_level,
        "due_date": due_date.strip()[:40],
        "review_required": bool(review_required),
        "approval_required": bool(approval_required),
    })
    append_audit(project, actor, "governance.updated", "project", project.id, {"before": before, "after": {key: data.get(key) for key in before}})
    return data
def transition_status(project: Project, target: str, actor: str, note: str = "") -> str:
    data = governance(project)
    current = data.get("status", "Draft")
    if target not in WORKFLOW_STATES:
        raise ValueError("Invalid workflow state")
    if target == current:
        return current
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"Transition from {current} to {target} is not allowed")
    if target == "Approved" and data.get("approval_required", True):
        pending_or_approved = [item for item in data["approvals"] if item.get("status") in {"Pending", "Approved"}]
        if not pending_or_approved:
            raise ValueError("Create an approval request before moving to Approved")
        if not any(item.get("status") == "Approved" for item in pending_or_approved):
            raise ValueError("At least one approval request must be approved")
    previous = current
    data["status"] = target
    append_audit(project, actor, "workflow.transitioned", "project", project.id, {"from": previous, "to": target, "note": note[:1000]})
    return target
def add_comment(project: Project, author: str, body: str, target_type: str = "Project", target_id: str = "", priority: str = "Normal", parent_id: str | None = None) -> dict:
    author = author.strip(); body = body.strip()
    if not author or not body:
        raise ValueError("Author and comment text are required")
    if priority not in {"Low", "Normal", "High", "Blocking"}:
        raise ValueError("Invalid comment priority")
    comment = {
        "id": uuid4().hex, "created_at": utc_now(), "author": author[:120], "body": body[:5000],
        "target_type": target_type[:80], "target_id": target_id[:120], "priority": priority,
        "status": "Open", "parent_id": parent_id,
    }
    governance(project)["comments"].append(comment)
    append_audit(project, author, "comment.created", target_type, target_id or project.id, {"comment_id": comment["id"], "priority": priority, "parent_id": parent_id})
    return comment
def resolve_comment(project: Project, comment_id: str, actor: str, resolution: str = "") -> bool:
    for comment in governance(project)["comments"]:
        if comment.get("id") == comment_id:
            comment["status"] = "Resolved"
            comment["resolved_at"] = utc_now()
            comment["resolved_by"] = actor.strip()[:120]
            comment["resolution"] = resolution.strip()[:2000]
            append_audit(project, actor, "comment.resolved", comment.get("target_type", "Project"), comment.get("target_id") or project.id, {"comment_id": comment_id, "resolution": comment["resolution"]})
            return True
    return False
def reopen_comment(project: Project, comment_id: str, actor: str) -> bool:
    for comment in governance(project)["comments"]:
        if comment.get("id") == comment_id:
            comment["status"] = "Open"
            comment.pop("resolved_at", None); comment.pop("resolved_by", None); comment.pop("resolution", None)
            append_audit(project, actor, "comment.reopened", comment.get("target_type", "Project"), comment.get("target_id") or project.id, {"comment_id": comment_id})
            return True
    return False
def add_decision(project: Project, actor: str, title: str, decision: str, rationale: str = "", status: str = "Decided") -> dict:
    if status not in {"Proposed", "Decided", "Superseded"}:
        raise ValueError("Invalid decision status")
    if not title.strip() or not decision.strip():
        raise ValueError("Decision title and outcome are required")
    item = {
        "id": uuid4().hex, "created_at": utc_now(), "created_by": actor.strip()[:120],
        "title": title.strip()[:200], "decision": decision.strip()[:5000], "rationale": rationale.strip()[:5000], "status": status,
    }
    governance(project)["decisions"].insert(0, item)
    append_audit(project, actor, "decision.created", "Decision", item["id"], {"title": item["title"], "status": status})
    return item
def supersede_decision(project: Project, decision_id: str, actor: str, reason: str = "") -> bool:
    for item in governance(project)["decisions"]:
        if item.get("id") == decision_id:
            item["status"] = "Superseded"
            item["superseded_at"] = utc_now(); item["superseded_by"] = actor.strip()[:120]; item["supersede_reason"] = reason.strip()[:2000]
            append_audit(project, actor, "decision.superseded", "Decision", decision_id, {"reason": item["supersede_reason"]})
            return True
    return False
def request_approval(project: Project, requester: str, reviewer: str, scope: str, attestation: str = "") -> dict:
    if not requester.strip() or not reviewer.strip() or not scope.strip():
        raise ValueError("Requester, reviewer, and scope are required")
    item = {
        "id": uuid4().hex, "created_at": utc_now(), "requester": requester.strip()[:120],
        "reviewer": reviewer.strip()[:120], "scope": scope.strip()[:500], "attestation": attestation.strip()[:2000], "status": "Pending",
    }
    governance(project)["approvals"].insert(0, item)
    append_audit(project, requester, "approval.requested", "Approval", item["id"], {"reviewer": item["reviewer"], "scope": item["scope"]})
    return item
def decide_approval(project: Project, approval_id: str, actor: str, status: str, note: str = "") -> bool:
    if status not in {"Approved", "Rejected", "Withdrawn"}:
        raise ValueError("Invalid approval decision")
    for item in governance(project)["approvals"]:
        if item.get("id") == approval_id:
            item["status"] = status
            item["decision_at"] = utc_now(); item["decided_by"] = actor.strip()[:120]; item["decision_note"] = note.strip()[:2000]
            append_audit(project, actor, f"approval.{status.lower()}", "Approval", approval_id, {"note": item["decision_note"]})
            return True
    return False
def governance_summary(project: Project) -> dict:
    data = governance(project)
    comments = data["comments"]
    approvals = data["approvals"]
    return {
        "status": data["status"],
        "risk_level": data["risk_level"],
        "owner": data["owner"],
        "contributors": len(data["contributors"]),
        "open_comments": sum(item.get("status") == "Open" for item in comments),
        "blocking_comments": sum(item.get("status") == "Open" and item.get("priority") == "Blocking" for item in comments),
        "pending_approvals": sum(item.get("status") == "Pending" for item in approvals),
        "approved_requests": sum(item.get("status") == "Approved" for item in approvals),
        "decisions": len(data["decisions"]),
        "audit_entries": len(data["audit_log"]),
    }
def governance_readiness(project: Project) -> dict:
    data = governance(project); summary = governance_summary(project); issues = []
    if not data["owner"]:
        issues.append({"severity": "warning", "message": "Project owner is not assigned"})
    if summary["blocking_comments"]:
        issues.append({"severity": "error", "message": f"{summary['blocking_comments']} blocking review comment(s) remain open"})
    if data["review_required"] and data["status"] in {"Approved", "Published"} and summary["open_comments"]:
        issues.append({"severity": "warning", "message": "Open review comments remain on an approved or published project"})
    if data["approval_required"] and data["status"] in {"Approved", "Published"} and not summary["approved_requests"]:
        issues.append({"severity": "error", "message": "No approved approval request is recorded"})
    errors = sum(item["severity"] == "error" for item in issues)
    warnings = sum(item["severity"] == "warning" for item in issues)
    return {"ready": errors == 0, "errors": errors, "warnings": warnings, "issues": issues, "summary": summary}
def append_audit(project: Project, actor: str, action: str, target_type: str, target_id: str, details: dict | None = None) -> dict:
    entry = {
        "id": uuid4().hex, "timestamp": utc_now(), "actor": (actor.strip() or "Unspecified")[:120],
        "action": action[:120], "target_type": target_type[:80], "target_id": str(target_id)[:120], "details": details or {},
    }
    log = governance(project)["audit_log"]
    log.append(entry)
    if len(log) > 2000:
        del log[:-2000]
    return entry
def _clean_names(names: list[str]) -> list[str]:
    result = []
    for name in names:
        clean = str(name).strip()[:120]
        if clean and clean not in result:
            result.append(clean)
    return result
