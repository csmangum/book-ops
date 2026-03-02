from __future__ import annotations

from pathlib import Path
from typing import Any

from .utils import dump_json, utc_now_iso, write_text


def write_decision_log(
    output_dir: Path,
    scope: str,
    gate: dict[str, Any],
    analysis: dict[str, Any],
    lore_delta: dict[str, Any] | None = None,
) -> dict[str, Path]:
    run_id = utc_now_iso().replace(":", "-").replace("+00-00", "Z")
    findings = analysis.get("generated_findings", [])
    hard_count = sum(1 for f in findings if str(f.get("rule_id", "")).startswith("HARD."))
    soft_count = sum(1 for f in findings if str(f.get("rule_id", "")).startswith("SOFT."))
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
        "generated_at": utc_now_iso(),
    }

    md_lines = [
        "# Decision Log",
        "",
        f"- Run ID: `{payload['run_id']}`",
        f"- Scope: `{scope}`",
        f"- Gate Status: **{gate.get('status', 'unknown')}**",
        f"- Gate Message: {gate.get('message', '')}",
        f"- Findings: {payload['analysis_counts']['total_findings']} (hard: {hard_count}, soft: {soft_count})",
        f"- Lore proposals: {payload['lore_proposal_count']}",
        "",
    ]
    md_path = output_dir / "decision-log.md"
    json_path = output_dir / "decision-log.json"
    write_text(md_path, "\n".join(md_lines))
    dump_json(json_path, payload)
    return {"md": md_path, "json": json_path}
