from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal


Severity = Literal["critical", "high", "medium", "low", "info"]
IssueStatus = Literal["open", "in_progress", "resolved", "waived"]
GateStatus = Literal["pass", "pass_with_waivers", "fail"]


@dataclass
class Evidence:
    file: str
    line_start: int
    line_end: int
    excerpt: str


@dataclass
class Finding:
    rule_id: str
    title: str
    severity: Severity
    message: str
    scope: str
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Issue:
    id: str
    rule_id: str
    title: str
    severity: Severity
    status: IssueStatus
    scope: str
    message: str
    evidence: list[Evidence] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    resolution_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    status: GateStatus
    blocking_issue_ids: list[str] = field(default_factory=list)
    warning_issue_ids: list[str] = field(default_factory=list)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
