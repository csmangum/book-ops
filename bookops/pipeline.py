from __future__ import annotations

from typing import Any

from .agents import agent_findings_to_analysis_findings, run_agent
from .analyzers import run_chapter_analysis, run_project_analysis
from .config import RuntimeConfig, load_rules
from .gates import evaluate_gate
from .issues import apply_analysis_findings, load_issue_store
from .lore import generate_lore_delta
from .reports import (
    render_analysis_reports,
    render_chapter_standard_reports,
    render_gate_report,
    render_project_standard_reports,
)
from .runlog import write_decision_log
from .runlog import append_run_history
from .utils import dump_json, ensure_dir


DEFAULT_CHAPTER_AGENT_FLOW = [
    "developmental_editor",
    "continuity_guardian",
    "line_editor",
    "proofreader",
]


def run_chapter_pipeline(config: RuntimeConfig, chapter_id: int, output_format: str = "both", strict: bool = False) -> dict[str, Any]:
    chapter_report_dir = config.output_dir / f"chapter-{chapter_id}"
    ensure_dir(chapter_report_dir)
    scope = f"chapter:{chapter_id}"

    agent_results = []
    for agent_name in DEFAULT_CHAPTER_AGENT_FLOW:
        result = run_agent(agent_name, scope="chapter", scope_id=chapter_id, config=config)
        agent_results.append(result)

    dump_json(chapter_report_dir / "agent-results.json", [r.to_dict() for r in agent_results])

    agent_findings = agent_findings_to_analysis_findings(agent_results, scope)
    analysis = run_chapter_analysis(config, chapter_id=chapter_id)
    all_findings = agent_findings + analysis.get("generated_findings", [])
    apply_analysis_findings(config.issues_file, all_findings)
    render_analysis_reports(chapter_report_dir, scope, analysis, fmt=output_format)

    lore_delta = generate_lore_delta(config, chapter_id=chapter_id, agent_results=agent_results)
    render_chapter_standard_reports(chapter_report_dir, analysis_payload=analysis, lore_delta=lore_delta, fmt=output_format)

    store = load_issue_store(config.issues_file)
    chapter_issues = [i for i in store.get("issues", []) if str(i.get("scope", "")).startswith(f"chapter:{chapter_id}")]
    rules = load_rules(config.rules_path)
    fail_on = rules.get("policy", {}).get("gate", {}).get("fail_on_unresolved_severity", ["critical"])
    gate = evaluate_gate(chapter_issues, fail_on_severities=fail_on, strict=strict)
    render_gate_report(chapter_report_dir, gate.to_dict(), fmt=output_format)
    decision_log = write_decision_log(
        chapter_report_dir,
        scope=scope,
        gate=gate.to_dict(),
        analysis=analysis,
        lore_delta=lore_delta,
        agent_results=agent_results,
    )
    run_entry = append_run_history(
        config.run_history_file,
        run_id=decision_log["run_id"],
        scope=scope,
        gate=gate.to_dict(),
        report_dir=chapter_report_dir,
        decision_log_json=decision_log["json"],
    )

    return {
        "analysis": analysis,
        "agent_results": [r.to_dict() for r in agent_results],
        "lore_delta": lore_delta,
        "gate": gate.to_dict(),
        "run": run_entry,
    }


def run_project_pipeline(config: RuntimeConfig, output_format: str = "both", strict: bool = False) -> dict[str, Any]:
    project_report_dir = config.output_dir / "project"
    ensure_dir(project_report_dir)

    analysis = run_project_analysis(config)
    store = apply_analysis_findings(config.issues_file, analysis.get("generated_findings", []))
    render_analysis_reports(project_report_dir, "project", analysis, fmt=output_format)
    render_project_standard_reports(project_report_dir, analysis, store.get("issues", []), fmt=output_format)

    all_issues = store.get("issues", [])
    rules = load_rules(config.rules_path)
    fail_on = rules.get("policy", {}).get("gate", {}).get("fail_on_unresolved_severity", ["critical"])
    gate = evaluate_gate(all_issues, fail_on_severities=fail_on, strict=strict)
    render_gate_report(project_report_dir, gate.to_dict(), fmt=output_format)
    decision_log = write_decision_log(
        project_report_dir,
        scope="project",
        gate=gate.to_dict(),
        analysis=analysis,
        lore_delta=None,
    )
    run_entry = append_run_history(
        config.run_history_file,
        run_id=decision_log["run_id"],
        scope="project",
        gate=gate.to_dict(),
        report_dir=project_report_dir,
        decision_log_json=decision_log["json"],
    )

    return {"analysis": analysis, "gate": gate.to_dict(), "run": run_entry}
