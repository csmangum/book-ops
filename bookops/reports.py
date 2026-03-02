from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .utils import dump_json, write_text


def _finding_md(item: dict[str, Any]) -> str:
    lines = [
        f"- **{item.get('rule_id', 'UNKNOWN')}** ({item.get('severity', 'low')})",
        f"  - {item.get('message', '')}",
    ]
    for ev in item.get("evidence", [])[:3]:
        lines.append(
            f"  - `{ev.get('file', '')}:{ev.get('line_start', 0)}` {ev.get('excerpt', '')}"
        )
    return "\n".join(lines)


def render_analysis_reports(output_dir: Path, scope: str, payload: dict[str, Any], fmt: str = "md") -> dict[str, Path]:
    paths: dict[str, Path] = {}
    findings = payload.get("generated_findings", [])
    md_lines = [f"# Analysis Report ({scope})", "", f"Total findings: {len(findings)}", ""]
    for finding in findings:
        md_lines.append(_finding_md(finding))
        md_lines.append("")

    md_path = output_dir / "analysis.md"
    json_path = output_dir / "analysis.json"
    if fmt in {"md", "both"}:
        write_text(md_path, "\n".join(md_lines))
        paths["md"] = md_path
    if fmt in {"json", "both"}:
        dump_json(json_path, payload)
        paths["json"] = json_path
    return paths


def render_gate_report(output_dir: Path, gate_payload: dict[str, Any], fmt: str = "md") -> dict[str, Path]:
    paths: dict[str, Path] = {}
    md = [
        "# Gate Result",
        "",
        f"- Status: **{gate_payload.get('status', 'unknown')}**",
        f"- Message: {gate_payload.get('message', '')}",
        f"- Blocking issues: {len(gate_payload.get('blocking_issue_ids', []))}",
        f"- Warnings: {len(gate_payload.get('warning_issue_ids', []))}",
        "",
    ]
    md_path = output_dir / "gate.md"
    json_path = output_dir / "gate.json"
    if fmt in {"md", "both"}:
        write_text(md_path, "\n".join(md))
        paths["md"] = md_path
    if fmt in {"json", "both"}:
        dump_json(json_path, gate_payload)
        paths["json"] = json_path
    return paths


def open_report(path: Path) -> str:
    return str(path.resolve())


def render_issue_summary_report(
    output_dir: Path,
    scope: str,
    summary: dict[str, Any],
    fmt: str = "md",
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    md_lines = [
        f"# Issue Summary ({scope})",
        "",
        f"- Total issues: **{summary.get('total', 0)}**",
        "",
        "## By status",
    ]
    for k, v in sorted(summary.get("by_status", {}).items()):
        md_lines.append(f"- {k}: {v}")
    md_lines.extend(["", "## By severity"])
    severity_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    for k, v in sorted(summary.get("by_severity", {}).items(), key=lambda kv: severity_rank.get(kv[0], 99)):
        md_lines.append(f"- {k}: {v}")
    md_lines.extend(["", "## Top blockers"])
    blockers = summary.get("top_blockers", [])
    if not blockers:
        md_lines.append("- None")
    else:
        for item in blockers:
            md_lines.append(f"- **{item.get('id','')}** ({item.get('severity','low')}) {item.get('message','')}")

    md_path = output_dir / "summary.md"
    json_path = output_dir / "summary.json"
    if fmt in {"md", "both"}:
        write_text(md_path, "\n".join(md_lines))
        paths["md"] = md_path
    if fmt in {"json", "both"}:
        dump_json(json_path, summary)
        paths["json"] = json_path
    return paths


def render_project_standard_reports(
    output_dir: Path,
    analysis_payload: dict[str, Any],
    issues: list[dict[str, Any]],
    fmt: str = "md",
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    open_issues = [i for i in issues if i.get("status") not in {"resolved", "waived"}]
    resolved_issues = [i for i in issues if i.get("status") in {"resolved", "waived"}]

    open_md = ["# Open Issues", "", f"Total: {len(open_issues)}", ""]
    for issue in open_issues:
        open_md.append(f"- **{issue.get('id','')}** ({issue.get('severity','low')}) {issue.get('message','')}")
    resolved_md = ["# Resolved/Waived Issues", "", f"Total: {len(resolved_issues)}", ""]
    for issue in resolved_issues:
        resolved_md.append(
            f"- **{issue.get('id','')}** ({issue.get('status','resolved')}) {issue.get('message','')}"
        )

    timeline_markers = analysis_payload.get("metrics", {}).get("timeline_markers", [])
    timeline_md = ["# Timeline Status", ""]
    for marker in timeline_markers:
        day_repr = ", ".join(marker.get("day_markers", [])) if marker.get("day_markers") else "none"
        date_repr = ", ".join(marker.get("date_markers", [])) if marker.get("date_markers") else "none"
        timeline_md.append(
            f"- Ch {marker.get('chapter')}: day markers [{day_repr}] | date markers [{date_repr}]"
        )

    motif_rows = analysis_payload.get("metrics", {}).get("motifs", [])
    motif_md = ["# Motif Dashboard", "", "| Chapter | copper | chrome | orchids |", "|---:|---:|---:|---:|"]
    for row in motif_rows:
        motif_md.append(
            f"| {row.get('chapter')} | {row.get('copper',0)} | {row.get('chrome',0)} | {row.get('orchids',0)} |"
        )

    open_path = output_dir / "open-issues.md"
    resolved_path = output_dir / "resolved-issues.md"
    timeline_path = output_dir / "timeline-status.md"
    motif_path = output_dir / "motif-dashboard.md"

    if fmt in {"md", "both"}:
        write_text(open_path, "\n".join(open_md))
        write_text(resolved_path, "\n".join(resolved_md))
        write_text(timeline_path, "\n".join(timeline_md))
        write_text(motif_path, "\n".join(motif_md))
        paths["open_issues_md"] = open_path
        paths["resolved_issues_md"] = resolved_path
        paths["timeline_md"] = timeline_path
        paths["motif_md"] = motif_path
    if fmt in {"json", "both"}:
        dump_json(output_dir / "open-issues.json", {"issues": open_issues})
        dump_json(output_dir / "resolved-issues.json", {"issues": resolved_issues})
        dump_json(output_dir / "timeline-status.json", {"timeline_markers": timeline_markers})
        dump_json(output_dir / "motif-dashboard.json", {"motifs": motif_rows})
    return paths


def render_chapter_standard_reports(
    output_dir: Path,
    analysis_payload: dict[str, Any],
    lore_delta: dict[str, Any] | None = None,
    fmt: str = "md",
) -> dict[str, Path]:
    paths: dict[str, Path] = {}
    findings = analysis_payload.get("generated_findings", [])
    continuity_findings = [f for f in findings if str(f.get("rule_id", "")).startswith("HARD.")]
    style_findings = [f for f in findings if str(f.get("rule_id", "")).startswith("SOFT.")]

    continuity_md = ["# Continuity Report", "", f"Total hard findings: {len(continuity_findings)}", ""]
    for finding in continuity_findings:
        continuity_md.append(_finding_md(finding))
        continuity_md.append("")

    style_md = ["# Style Audit", "", f"Total soft findings: {len(style_findings)}", ""]
    for finding in style_findings:
        style_md.append(_finding_md(finding))
        style_md.append("")

    lore_md = ["# Lore Delta", ""]
    proposals = (lore_delta or {}).get("proposals", [])
    lore_md.append(f"Total proposals: {len(proposals)}")
    lore_md.append("")
    for proposal in proposals:
        lore_md.append(
            f"- **{proposal.get('id','')}** -> `{proposal.get('target_lore_file','')}`: {proposal.get('reason','')}"
        )

    continuity_path = output_dir / "continuity.md"
    style_path = output_dir / "style-audit.md"
    lore_path = output_dir / "lore-delta.md"

    if fmt in {"md", "both"}:
        write_text(continuity_path, "\n".join(continuity_md))
        write_text(style_path, "\n".join(style_md))
        write_text(lore_path, "\n".join(lore_md))
        paths["continuity_md"] = continuity_path
        paths["style_md"] = style_path
        paths["lore_md"] = lore_path
    if fmt in {"json", "both"}:
        dump_json(output_dir / "continuity.json", {"findings": continuity_findings})
        dump_json(output_dir / "style-audit.json", {"findings": style_findings})
        dump_json(output_dir / "lore-delta.json", lore_delta or {"proposals": []})
    return paths
