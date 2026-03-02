from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import __version__
from .agents import AGENT_PACK_VERSION, list_agents, run_agent
from .analyzers import run_chapter_analysis, run_project_analysis
from .canon import build_canon, diff_canon, load_snapshot, save_canon_snapshot, validate_canon_payload
from .config import bootstrap, load_runtime_config, load_rules
from .gates import evaluate_gate
from .indexing import index_status, rebuild_index
from .issues import filter_issues, load_issue_store, update_issue_status, apply_analysis_findings, summarize_issues
from .lore import apply_lore_proposal, approve_lore_proposal, generate_lore_delta
from .pipeline import run_chapter_pipeline, run_project_pipeline
from .readmodels import (
    get_canon_graph,
    get_chapter_content,
    get_rules_payload,
    get_run,
    get_settings_payload,
    list_runs,
    patch_settings_payload,
)
from .reports import (
    open_report,
    render_analysis_reports,
    render_chapter_standard_reports,
    render_gate_report,
    render_issue_summary_report,
    render_project_standard_reports,
)
from .vcs import changed_paths_since
from .templates import list_templates
from .utils import dump_json, ensure_dir, load_json


def _print(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="bookops", description="BookOps CLI — agentic writing QA and continuity framework")
    parser.add_argument("--project", default=".", help="Project root")
    parser.add_argument("--config", default=None, help="Path to config yaml")
    parser.add_argument("--format", default="md", choices=["md", "json", "both"], help="Output format")
    parser.add_argument("--output-dir", default="reports", help="Reports output directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures at gate stage")

    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="Bootstrap BookOps files")
    p_init.add_argument("--template", default=None, help="Optional rules template")

    p_template = sub.add_parser("template", help="Template operations")
    p_template_sub = p_template.add_subparsers(dest="template_cmd")
    p_template_sub.add_parser("list", help="List available templates")

    p_index = sub.add_parser("index", help="Build/query retrieval indexes")
    p_index_sub = p_index.add_subparsers(dest="index_cmd")
    p_index_sub.add_parser("rebuild", help="Rebuild symbolic + semantic indexes")
    p_index_sub.add_parser("status", help="Show index status")

    p_canon = sub.add_parser("canon", help="Build/validate/diff canonical graph")
    p_canon_sub = p_canon.add_subparsers(dest="canon_cmd")
    p_canon_sub.add_parser("build", help="Build canon snapshot")
    p_canon_sub.add_parser("validate", help="Validate latest canon snapshot")
    p_canon_sub.add_parser("graph", help="Return canon graph payload for UI")
    p_canon_diff = p_canon_sub.add_parser("diff", help="Diff canon snapshots")
    p_canon_diff.add_argument("--from", dest="from_snapshot", required=True)
    p_canon_diff.add_argument("--to", dest="to_snapshot", required=True)

    p_analyze = sub.add_parser("analyze", help="Run analyzer suites")
    p_analyze_sub = p_analyze.add_subparsers(dest="analyze_cmd")
    p_chapter = p_analyze_sub.add_parser("chapter", help="Analyze one chapter")
    p_chapter.add_argument("chapter_id", type=int)
    p_chapter.add_argument("--checks", default="")
    p_chapter.add_argument("--since", default=None)
    p_analyze_project = p_analyze_sub.add_parser("project", help="Analyze full project")
    p_analyze_project.add_argument("--since", default=None, help="Git ref for changed chapter filtering")

    p_chapter_ops = sub.add_parser("chapter", help="Chapter read operations")
    p_chapter_ops_sub = p_chapter_ops.add_subparsers(dest="chapter_cmd")
    p_chapter_content = p_chapter_ops_sub.add_parser("content", help="Read chapter manuscript content")
    p_chapter_content.add_argument("chapter_id", type=int)

    p_agent = sub.add_parser("agent", help="Run or list agents")
    p_agent_sub = p_agent.add_subparsers(dest="agent_cmd")
    p_agent_sub.add_parser("list", help="List available agents")
    p_agent_run = p_agent_sub.add_parser("run", help="Run one agent")
    p_agent_run.add_argument("agent_name")
    p_agent_run.add_argument("--scope", required=True, choices=["chapter", "project"])
    p_agent_run.add_argument("--id", type=int, default=None)

    p_issue = sub.add_parser("issue", help="List/update/waive issues")
    p_issue_sub = p_issue.add_subparsers(dest="issue_cmd")
    p_issue_list = p_issue_sub.add_parser("list", help="List issues")
    p_issue_list.add_argument("--status", default=None)
    p_issue_list.add_argument("--severity", default=None)
    p_issue_list.add_argument("--scope", default=None)
    p_issue_update = p_issue_sub.add_parser("update", help="Update issue status")
    p_issue_update.add_argument("issue_id")
    p_issue_update.add_argument("--status", required=True, choices=["open", "in_progress", "resolved", "waived"])
    p_issue_update.add_argument("--note", default="")
    p_issue_waive = p_issue_sub.add_parser("waive", help="Waive issue")
    p_issue_waive.add_argument("issue_id")
    p_issue_waive.add_argument("--reason", required=True)
    p_issue_waive.add_argument("--reviewer", required=True)

    p_lore = sub.add_parser("lore", help="Generate/apply lore sync proposals")
    p_lore_sub = p_lore.add_subparsers(dest="lore_cmd")
    p_lore_delta = p_lore_sub.add_parser("delta", help="Generate lore proposals")
    p_lore_delta.add_argument("--scope", choices=["chapter", "project"], default="project")
    p_lore_delta.add_argument("--id", type=int, default=None)
    p_lore_delta.add_argument("--since", default=None, help="Git ref for changed chapter filtering")
    p_lore_sync = p_lore_sub.add_parser("sync", help="Apply proposal")
    p_lore_sync.add_argument("--proposal", required=True)
    p_lore_sync.add_argument("--apply", action="store_true")
    p_lore_approve = p_lore_sub.add_parser("approve", help="Approve proposal for apply")
    p_lore_approve.add_argument("--proposal", required=True)
    p_lore_approve.add_argument("--reviewer", required=True)
    p_lore_approve.add_argument("--note", default="")

    p_gate = sub.add_parser("gate", help="Evaluate chapter/project gates")
    p_gate_sub = p_gate.add_subparsers(dest="gate_cmd")
    p_gate_ch = p_gate_sub.add_parser("chapter", help="Evaluate chapter gate")
    p_gate_ch.add_argument("chapter_id", type=int)
    p_gate_sub.add_parser("project", help="Evaluate project gate")

    p_pipeline = sub.add_parser("pipeline", help="Run orchestrated full workflows")
    p_pipe_sub = p_pipeline.add_subparsers(dest="pipeline_cmd")
    p_pipe_run = p_pipe_sub.add_parser("run", help="Run pipeline")
    p_pipe_run_sub = p_pipe_run.add_subparsers(dest="pipeline_scope")
    p_pipe_ch = p_pipe_run_sub.add_parser("chapter", help="Run full chapter pipeline")
    p_pipe_ch.add_argument("chapter_id", type=int)
    p_pipe_run_sub.add_parser("project", help="Run full project pipeline")

    p_report = sub.add_parser("report", help="Build/open report bundles")
    p_report_sub = p_report.add_subparsers(dest="report_cmd")
    p_report_build = p_report_sub.add_parser("build", help="Build report from latest artifacts")
    p_report_build.add_argument("--scope", choices=["chapter", "project"], required=True)
    p_report_build.add_argument("--id", type=int, default=None)
    p_report_open = p_report_sub.add_parser("open", help="Open latest report location")
    p_report_open.add_argument("--scope", choices=["chapter", "project"], required=True)
    p_report_open.add_argument("--id", type=int, default=None)

    p_run = sub.add_parser("run", help="List and inspect pipeline runs")
    p_run_sub = p_run.add_subparsers(dest="run_cmd")
    p_run_sub.add_parser("list", help="List recorded runs")
    p_run_show = p_run_sub.add_parser("show", help="Show one recorded run")
    p_run_show.add_argument("run_id")

    p_rules = sub.add_parser("rules", help="Read rule configuration")
    p_rules_sub = p_rules.add_subparsers(dest="rules_cmd")
    p_rules_sub.add_parser("get", help="Read rules payload")

    p_settings = sub.add_parser("settings", help="Read/update config settings")
    p_settings_sub = p_settings.add_subparsers(dest="settings_cmd")
    p_settings_sub.add_parser("get", help="Read settings payload")
    p_settings_patch = p_settings_sub.add_parser("patch", help="Patch settings with JSON object")
    p_settings_patch.add_argument("--patch-json", required=True)

    sub.add_parser("version", help="Show CLI and schema versions")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1

    project_root = Path(args.project).resolve()
    output_dir = (project_root / args.output_dir).resolve()
    ensure_dir(output_dir)
    if args.command == "init":
        bootstrap(project_root, template=getattr(args, "template", None))
        print(f"Initialized BookOps in {project_root}")
        return 0

    if args.command == "template":
        if args.template_cmd == "list":
            _print({"templates": list_templates()})
            return 0
        return 1

    config = load_runtime_config(
        project_root=project_root,
        config_path=Path(args.config).resolve() if args.config else None,
        output_dir=output_dir,
    )
    ensure_dir(config.bookops_dir)
    ensure_dir(config.index_dir)
    ensure_dir(config.snapshots_dir)

    if args.command == "index":
        if args.index_cmd == "rebuild":
            payload = rebuild_index(config.project_root, config.index_dir)
            _print(payload)
            return 0
        if args.index_cmd == "status":
            _print(index_status(config.index_dir))
            return 0
        return 1

    if args.command == "canon":
        if args.canon_cmd == "build":
            canon_payload = build_canon(config)
            snapshot_path = save_canon_snapshot(config, canon_payload)
            _print({"snapshot": str(snapshot_path), "chapter_count": len(canon_payload.get("chapter_index", []))})
            return 0
        if args.canon_cmd == "validate":
            payload = load_json(config.canon_latest, default={}) or {}
            errors = validate_canon_payload(payload)
            _print({"valid": len(errors) == 0, "errors": errors})
            return 0 if not errors else 1
        if args.canon_cmd == "graph":
            _print(get_canon_graph(config))
            return 0
        if args.canon_cmd == "diff":
            from_payload = load_snapshot((config.snapshots_dir / args.from_snapshot).resolve() if not Path(args.from_snapshot).is_absolute() else Path(args.from_snapshot))
            to_payload = load_snapshot((config.snapshots_dir / args.to_snapshot).resolve() if not Path(args.to_snapshot).is_absolute() else Path(args.to_snapshot))
            _print(diff_canon(from_payload, to_payload))
            return 0
        return 1

    if args.command == "chapter":
        if args.chapter_cmd == "content":
            _print(get_chapter_content(config, args.chapter_id))
            return 0
        return 1

    if args.command == "analyze":
        if args.analyze_cmd == "chapter":
            if args.since:
                changed = changed_paths_since(config.project_root, args.since)
                chapter_path = str((config.chapters_dir / f"{args.chapter_id}_").relative_to(config.project_root))  # prefix hint
                changed_chapters = [p for p in changed if p.startswith("chapters/")]
                if not any(p.startswith(chapter_path) for p in changed_chapters):
                    _print(
                        {
                            "scope": f"chapter:{args.chapter_id}",
                            "findings": 0,
                            "checks": [],
                            "skipped": True,
                            "reason": f"Chapter {args.chapter_id} not changed since {args.since}",
                        }
                    )
                    return 0
            requested_checks: set[str] | None = None
            if args.checks:
                requested_checks = {part.strip() for part in args.checks.split(",") if part.strip()}
            payload = run_chapter_analysis(config, args.chapter_id, checks=requested_checks)
            apply_analysis_findings(config.issues_file, payload.get("generated_findings", []))
            out_dir = config.output_dir / f"chapter-{args.chapter_id}"
            ensure_dir(out_dir)
            render_analysis_reports(out_dir, f"chapter:{args.chapter_id}", payload, fmt=args.format)
            render_chapter_standard_reports(out_dir, analysis_payload=payload, lore_delta=None, fmt=args.format)
            _print(
                {
                    "scope": f"chapter:{args.chapter_id}",
                    "findings": len(payload.get("generated_findings", [])),
                    "checks": payload.get("checks", []),
                }
            )
            return 0
        if args.analyze_cmd == "project":
            chapter_filter_paths = None
            if args.since:
                changed = changed_paths_since(config.project_root, args.since)
                chapter_filter_paths = {p for p in changed if p.startswith("chapters/")}
            payload = run_project_analysis(config, chapter_filter_paths=chapter_filter_paths)
            store = apply_analysis_findings(config.issues_file, payload.get("generated_findings", []))
            out_dir = config.output_dir / "project"
            ensure_dir(out_dir)
            render_analysis_reports(out_dir, "project", payload, fmt=args.format)
            render_project_standard_reports(out_dir, payload, store.get("issues", []), fmt=args.format)
            _print(
                {
                    "scope": "project",
                    "findings": len(payload.get("generated_findings", [])),
                    "chapter_filter_count": len(chapter_filter_paths or []),
                }
            )
            return 0
        return 1

    if args.command == "agent":
        if args.agent_cmd == "list":
            _print(list_agents())
            return 0
        if args.agent_cmd == "run":
            result = run_agent(args.agent_name, scope=args.scope, scope_id=args.id)
            _print(result.__dict__)
            return 0
        return 1

    if args.command == "issue":
        store = load_issue_store(config.issues_file)
        if args.issue_cmd == "list":
            issues = filter_issues(store, status=args.status, severity=args.severity, scope=args.scope)
            _print({"count": len(issues), "issues": issues})
            return 0
        if args.issue_cmd == "update":
            updated = update_issue_status(config.issues_file, args.issue_id, args.status, note=args.note)
            _print({"updated": args.issue_id, "issue_count": len(updated.get("issues", []))})
            return 0
        if args.issue_cmd == "waive":
            note = f"waived by {args.reviewer}: {args.reason}"
            updated = update_issue_status(config.issues_file, args.issue_id, "waived", note=note)
            _print({"waived": args.issue_id, "issue_count": len(updated.get("issues", []))})
            return 0
        return 1

    if args.command == "lore":
        if args.lore_cmd == "delta":
            chapter_id = args.id if args.scope == "chapter" else None
            payload = generate_lore_delta(config, chapter_id=chapter_id, since_ref=args.since)
            _print(
                {
                    "scope": payload["scope"],
                    "proposals": len(payload.get("proposals", [])),
                    "chapter_count_evaluated": payload.get("chapter_count_evaluated", 0),
                }
            )
            return 0
        if args.lore_cmd == "sync":
            if not args.apply:
                print("Refusing to sync without --apply")
                return 1
            proposal = apply_lore_proposal(config, args.proposal)
            _print({"applied": proposal.get("id"), "target": proposal.get("target_lore_file")})
            return 0
        if args.lore_cmd == "approve":
            proposal = approve_lore_proposal(
                config,
                args.proposal,
                reviewer=args.reviewer,
                note=args.note,
            )
            _print({"approved": proposal.get("id"), "reviewer": proposal.get("approved_by")})
            return 0
        return 1

    if args.command == "gate":
        store = load_issue_store(config.issues_file)
        rules = load_rules(config.rules_path)
        fail_on = rules.get("policy", {}).get("gate", {}).get("fail_on_unresolved_severity", ["critical"])
        if args.gate_cmd == "chapter":
            issues = [i for i in store.get("issues", []) if str(i.get("scope", "")).startswith(f"chapter:{args.chapter_id}")]
            result = evaluate_gate(issues, fail_on_severities=fail_on, strict=args.strict)
            out_dir = config.output_dir / f"chapter-{args.chapter_id}"
            ensure_dir(out_dir)
            render_gate_report(out_dir, result.to_dict(), fmt=args.format)
            _print(result.to_dict())
            if result.status == "fail":
                return 2
            if result.status == "pass_with_waivers":
                return 3
            return 0
        if args.gate_cmd == "project":
            issues = store.get("issues", [])
            result = evaluate_gate(issues, fail_on_severities=fail_on, strict=args.strict)
            out_dir = config.output_dir / "project"
            ensure_dir(out_dir)
            render_gate_report(out_dir, result.to_dict(), fmt=args.format)
            _print(result.to_dict())
            if result.status == "fail":
                return 2
            if result.status == "pass_with_waivers":
                return 3
            return 0
        return 1

    if args.command == "pipeline":
        if args.pipeline_cmd == "run":
            if args.pipeline_scope == "chapter":
                payload = run_chapter_pipeline(config, args.chapter_id, output_format=args.format, strict=args.strict)
                _print(
                    {
                        "gate": payload["gate"]["status"],
                        "scope": f"chapter:{args.chapter_id}",
                        "run_id": payload.get("run", {}).get("run_id"),
                    }
                )
                if payload["gate"]["status"] == "fail":
                    return 2
                if payload["gate"]["status"] == "pass_with_waivers":
                    return 3
                return 0
            if args.pipeline_scope == "project":
                payload = run_project_pipeline(config, output_format=args.format, strict=args.strict)
                _print(
                    {
                        "gate": payload["gate"]["status"],
                        "scope": "project",
                        "run_id": payload.get("run", {}).get("run_id"),
                    }
                )
                if payload["gate"]["status"] == "fail":
                    return 2
                if payload["gate"]["status"] == "pass_with_waivers":
                    return 3
                return 0
        return 1

    if args.command == "report":
        if args.report_cmd == "build":
            if args.scope == "chapter":
                if args.id is None:
                    print("Error: --id is required when --scope is chapter")
                    return 1
                out_dir = config.output_dir / f"chapter-{args.id}"
                scope_key = f"chapter:{args.id}"
            else:
                out_dir = config.output_dir / "project"
                scope_key = "project"
            ensure_dir(out_dir)
            store = load_issue_store(config.issues_file)
            if scope_key == "project":
                scoped_issues = store.get("issues", [])
            else:
                scoped_issues = [i for i in store.get("issues", []) if str(i.get("scope", "")).startswith(scope_key)]
            summary = summarize_issues(scoped_issues)
            render_issue_summary_report(out_dir, scope=scope_key, summary=summary, fmt=args.format)
            _print({"report_dir": str(out_dir.resolve()), "top_blockers": len(summary.get("top_blockers", []))})
            return 0
        if args.report_cmd == "open":
            if args.scope == "chapter":
                if args.id is None:
                    print("Error: --id is required when --scope is chapter")
                    return 1
                out_dir = config.output_dir / f"chapter-{args.id}"
            else:
                out_dir = config.output_dir / "project"
            _print({"path": open_report(out_dir)})
            return 0
        return 1

    if args.command == "run":
        if args.run_cmd == "list":
            runs = list_runs(config)
            _print({"count": len(runs), "runs": runs})
            return 0
        if args.run_cmd == "show":
            entry = get_run(config, args.run_id)
            if not entry:
                _print({"error": f"run {args.run_id} not found"})
                return 1
            _print(entry)
            return 0
        return 1

    if args.command == "rules":
        if args.rules_cmd == "get":
            _print(get_rules_payload(config))
            return 0
        return 1

    if args.command == "settings":
        if args.settings_cmd == "get":
            _print(get_settings_payload(config))
            return 0
        if args.settings_cmd == "patch":
            try:
                patch = json.loads(args.patch_json)
            except json.JSONDecodeError:
                print("Error: --patch-json must be valid JSON")
                return 1
            if not isinstance(patch, dict):
                print("Error: --patch-json must decode to an object")
                return 1
            _print(patch_settings_payload(config, patch))
            return 0
        return 1

    if args.command == "version":
        _print(
            {
                "bookops_version": __version__,
                "rules_schema_version": 1,
                "canon_schema_version": 1,
                "agent_pack_version": AGENT_PACK_VERSION,
                "agent_count": len(list_agents()),
            }
        )
        return 0

    return 1
