from __future__ import annotations

from pathlib import Path
from typing import Any

from .agents import AgentResult
from .utils import dump_json, load_json, utc_now_iso, write_text


def load_run_history(path: Path) -> list[dict[str, Any]]:
    payload = load_json(path, default={"runs": []}) or {"runs": []}
    runs = payload.get("runs", [])
    return runs if isinstance(runs, list) else []


def save_run_history(path: Path, runs: list[dict[str, Any]]) -> None:
    dump_json(path, {"runs": runs})


def append_run_history(
    path: Path,
    *,
    run_id: str,
    scope: str,
    gate: dict[str, Any],
    report_dir: Path,
    decision_log_json: Path,
) -> dict[str, Any]:
    runs = load_run_history(path)
    entry = {
        "run_id": run_id,
        "scope": scope,
        "gate": gate.get("status", "unknown"),
        "created_at": utc_now_iso(),
        "report_dir": str(report_dir.resolve()),
        "decision_log_json": str(decision_log_json.resolve()),
    }
    runs = [entry] + [r for r in runs if r.get("run_id") != run_id]
    save_run_history(path, runs[:200])
    return entry


def get_run_entry(path: Path, run_id: str) -> dict[str, Any] | None:
    for entry in load_run_history(path):
        if entry.get("run_id") == run_id:
            return entry
    return None


def write_decision_log(
    output_dir: Path,
    scope: str,
    gate: dict[str, Any],
    analysis: dict[str, Any],
    lore_delta: dict[str, Any] | None = None,
    agent_results: list[AgentResult] | None = None,
) -> dict[str, Any]:
    run_id = utc_now_iso().replace(":", "-").replace("+00-00", "Z")
    findings = analysis.get("generated_findings", [])
    hard_count = sum(1 for f in findings if str(f.get("rule_id", "")).startswith("HARD."))
    soft_count = sum(1 for f in findings if str(f.get("rule_id", "")).startswith("SOFT."))
    agent_summaries = (
        [{"name": r.name, "summary": r.summary, "confidence": r.confidence, "needs_human_decision": r.needs_human_decision} for r in agent_results]
        if agent_results
        else []
    )
    payload = {
        "run_id": run_id,
        "scope": scope,
        "gate": gate,
        "analysis_counts": {
            "total_findings": len(findings),
            "hard_findings": hard_count,
            "soft_findings": soft_count,
        },
        "lore_proposal_count": len((lore_delta or {}).get("proposals", [])),
        "agent_summaries": list(agent_summaries),
        "generated_at": utc_now_iso(),
    }

    agent_line = f"- Agents: {len(agent_summaries)} ran" if agent_summaries else ""
    md_lines = [
        "# Decision Log",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Scope: `{scope}`",
        f"- Gate Status: **{gate.get('status', 'unknown')}**",
        f"- Gate Message: {gate.get('message', '')}",
        f"- Findings: {payload['analysis_counts']['total_findings']} (hard: {hard_count}, soft: {soft_count})",
        f"- Lore proposals: {payload['lore_proposal_count']}",
        agent_line,
        "",
    ]
    md_path = output_dir / "decision-log.md"
    json_path = output_dir / "decision-log.json"
    write_text(md_path, "\n".join(md_lines))
    dump_json(json_path, payload)
    return {"md": md_path, "json": json_path, "run_id": run_id}
