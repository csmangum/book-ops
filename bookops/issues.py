from __future__ import annotations

import hashlib
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import Evidence, Finding, Issue
from .utils import dump_json, load_json


def _issue_fingerprint(finding: dict[str, Any]) -> str:
    key = "|".join(
        [
            str(finding.get("rule_id")),
            str(finding.get("scope")),
            str(finding.get("message")),
            str(finding.get("evidence", [])),
        ]
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def load_issue_store(path: Path) -> dict[str, Any]:
    return load_json(path, default={"issues": []}) or {"issues": []}


def save_issue_store(path: Path, store: dict[str, Any]) -> None:
    dump_json(path, store)


def findings_to_issues(findings: list[dict[str, Any]]) -> list[Issue]:
    issues: list[Issue] = []
    for finding in findings:
        evidence = [
            Evidence(
                file=e.get("file", ""),
                line_start=e.get("line_start", 0),
                line_end=e.get("line_end", 0),
                excerpt=e.get("excerpt", ""),
            )
            for e in finding.get("evidence", [])
        ]
        fid = _issue_fingerprint(finding)
        issues.append(
            Issue(
                id=f"ISSUE-{fid}",
                rule_id=finding.get("rule_id", "UNKNOWN"),
                title=finding.get("title", "Issue"),
                severity=finding.get("severity", "low"),
                status="open",
                scope=finding.get("scope", "project"),
                message=finding.get("message", ""),
                evidence=evidence,
                metadata=finding.get("metadata", {}),
            )
        )
    return issues


def merge_issues(existing: list[dict[str, Any]], new_issues: list[Issue]) -> list[dict[str, Any]]:
    by_id = {item["id"]: item for item in existing}
    for issue in new_issues:
        item = issue.to_dict()
        if issue.id in by_id:
            previous_status = by_id[issue.id].get("status", "open")
            if previous_status in {"resolved", "waived", "in_progress"}:
                item["status"] = previous_status
                item["resolution_note"] = by_id[issue.id].get("resolution_note", "")
            by_id[issue.id] = item
        else:
            by_id[issue.id] = item
    return sorted(by_id.values(), key=lambda i: (i.get("status", ""), i.get("severity", ""), i.get("id", "")))


def apply_analysis_findings(issue_store_path: Path, findings: list[dict[str, Any]]) -> dict[str, Any]:
    store = load_issue_store(issue_store_path)
    created = findings_to_issues(findings)
    store["issues"] = merge_issues(store.get("issues", []), created)
    save_issue_store(issue_store_path, store)
    return store


def update_issue_status(issue_store_path: Path, issue_id: str, status: str, note: str = "") -> dict[str, Any]:
    store = load_issue_store(issue_store_path)
    for issue in store.get("issues", []):
        if issue.get("id") == issue_id:
            issue["status"] = status
            if note:
                issue["resolution_note"] = note
            break
    save_issue_store(issue_store_path, store)
    return store


def filter_issues(
    store: dict[str, Any],
    status: str | None = None,
    severity: str | None = None,
    scope: str | None = None,
) -> list[dict[str, Any]]:
    issues = store.get("issues", [])
    if status:
        issues = [i for i in issues if i.get("status") == status]
    if severity:
        issues = [i for i in issues if i.get("severity") == severity]
    if scope:
        if scope == "project":
            # Project scope includes full issue landscape.
            pass
        elif scope == "chapter":
            issues = [i for i in issues if str(i.get("scope", "")).startswith("chapter:")]
        else:
            issues = [i for i in issues if str(i.get("scope", "")).startswith(scope)]
    return issues


def summarize_issues(issues: list[dict[str, Any]]) -> dict[str, Any]:
    severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
    by_status: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    for issue in issues:
        by_status[issue.get("status", "open")] = by_status.get(issue.get("status", "open"), 0) + 1
        by_severity[issue.get("severity", "low")] = by_severity.get(issue.get("severity", "low"), 0) + 1
    open_issues = [i for i in issues if i.get("status", "open") not in {"resolved", "waived"}]
    top_blockers = sorted(
        open_issues,
        key=lambda i: (
            -severity_order.get(i.get("severity", "low"), 0),
            i.get("id", ""),
        ),
    )[:5]
    return {
        "total": len(issues),
        "by_status": by_status,
        "by_severity": by_severity,
        "top_blockers": top_blockers,
    }
