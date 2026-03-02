from __future__ import annotations

from typing import Any

from .models import GateResult


SEVERITY_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}


def evaluate_gate(
    issues: list[dict[str, Any]],
    fail_on_severities: list[str] | None = None,
    strict: bool = False,
) -> GateResult:
    fail_on = set(fail_on_severities or ["critical"])
    blocking: list[str] = []
    warnings: list[str] = []
    has_waivers = False

    for issue in issues:
        status = issue.get("status", "open")
        severity = issue.get("severity", "low")
        issue_id = issue.get("id", "")

        if status == "waived":
            has_waivers = True
            continue
        if status in {"resolved"}:
            continue

        if severity in fail_on:
            blocking.append(issue_id)
            continue
        if strict and severity in {"high", "medium", "low"}:
            blocking.append(issue_id)
            continue
        warnings.append(issue_id)

    if blocking:
        return GateResult(status="fail", blocking_issue_ids=blocking, warning_issue_ids=warnings, message="Blocking issues detected.")
    if has_waivers:
        return GateResult(status="pass_with_waivers", blocking_issue_ids=[], warning_issue_ids=warnings, message="Passed with waivers.")
    return GateResult(status="pass", blocking_issue_ids=[], warning_issue_ids=warnings, message="Gate passed.")
