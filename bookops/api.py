from __future__ import annotations

import io
import json
import os
import threading
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query

from . import __version__
from .agents import AGENT_PACK_VERSION, list_agents, run_agent
from .cli import main as cli_main
from .config import load_runtime_config
from .utils import load_json


app = FastAPI(title="BookOps API", version="1.0.0")

_cli_lock = threading.Lock()


def _api_context() -> tuple[Path, Path]:
    project_root = Path(os.getenv("BOOKOPS_PROJECT", ".")).resolve()
    output_dir = Path(os.getenv("BOOKOPS_OUTPUT_DIR", "reports"))
    if not output_dir.is_absolute():
        output_dir = (project_root / output_dir).resolve()
    return project_root, output_dir


def _envelope(ok: bool, data: Any, exit_code: int = 0, stderr: str = "") -> dict[str, Any]:
    return {"ok": ok, "exit_code": exit_code, "data": data, "stderr": stderr}


def _run_cli(command_args: list[str], *, strict: bool = False) -> dict[str, Any]:
    project_root, output_dir = _api_context()
    stdout = io.StringIO()
    stderr = io.StringIO()
    argv = [
        "--project",
        str(project_root),
        "--format",
        "json",
        "--output-dir",
        str(output_dir),
    ]
    if strict:
        argv.append("--strict")
    argv.extend(command_args)

    with _cli_lock:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = cli_main(argv)

        stdout_text = stdout.getvalue().strip()
        stderr_text = stderr.getvalue().strip()

    payload: Any = {}
    if stdout_text:
        try:
            payload = json.loads(stdout_text)
        except json.JSONDecodeError:
            payload = {"output": stdout_text}

    ok = exit_code in {0, 2, 3}
    return _envelope(ok=ok, data=payload, exit_code=exit_code, stderr=stderr_text)


def _read_artifact(path: Path) -> dict[str, Any]:
    if not path.exists():
        return _envelope(ok=False, data={}, exit_code=1, stderr=f"artifact not found: {path}")
    payload = load_json(path, default={}) or {}
    return _envelope(ok=True, data=payload, exit_code=0, stderr="")


@app.get("/version")
def get_version() -> dict[str, Any]:
    return _envelope(
        ok=True,
        exit_code=0,
        stderr="",
        data={
            "bookops_version": __version__,
            "rules_schema_version": 1,
            "canon_schema_version": 1,
            "agent_pack_version": AGENT_PACK_VERSION,
            "agent_count": len(list_agents()),
        },
    )


@app.get("/agents")
def get_agents() -> dict[str, Any]:
    return _envelope(ok=True, exit_code=0, stderr="", data=list_agents())


@app.post("/agent/run")
def run_agent_endpoint(body: dict[str, Any]) -> dict[str, Any]:
    try:
        project_root, output_dir = _api_context()
        config = load_runtime_config(project_root=project_root, output_dir=output_dir)
        result = run_agent(
            body["agent_name"],
            scope=body["scope"],
            scope_id=body.get("scope_id"),
            config=config,
        )
        return _envelope(ok=True, exit_code=0, stderr="", data=result.to_dict())
    except (ValueError, KeyError) as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))


@app.post("/index/rebuild")
def rebuild_index() -> dict[str, Any]:
    return _run_cli(["index", "rebuild"])


@app.get("/index/status")
def get_index_status(include_symbolic: bool = Query(default=False)) -> dict[str, Any]:
    args = ["index", "status"]
    if include_symbolic:
        args.append("--include-symbolic")
    return _run_cli(args)


@app.post("/canon/build")
def build_canon() -> dict[str, Any]:
    return _run_cli(["canon", "build"])


@app.get("/canon/validate")
def validate_canon() -> dict[str, Any]:
    return _run_cli(["canon", "validate"])


@app.post("/canon/diff")
def diff_canon(body: dict[str, str]) -> dict[str, Any]:
    return _run_cli(
        [
            "canon",
            "diff",
            "--from",
            body["from_snapshot"],
            "--to",
            body["to_snapshot"],
        ]
    )


@app.get("/canon/graph")
def get_canon_graph() -> dict[str, Any]:
    return _run_cli(["canon", "graph"])


@app.post("/analyze/chapter")
def analyze_chapter(body: dict[str, Any]) -> dict[str, Any]:
    args = ["analyze", "chapter", str(body["chapter_id"])]
    checks = body.get("checks") or []
    if checks:
        args.extend(["--checks", ",".join(checks)])
    if body.get("since") is not None:
        args.extend(["--since", str(body["since"])])
    return _run_cli(args)


@app.post("/analyze/project")
def analyze_project(body: dict[str, Any] | None = None) -> dict[str, Any]:
    args = ["analyze", "project"]
    body = body or {}
    if body.get("since") is not None:
        args.extend(["--since", str(body["since"])])
    return _run_cli(args)


@app.post("/gate/chapter")
def gate_chapter(body: dict[str, Any]) -> dict[str, Any]:
    return _run_cli(["gate", "chapter", str(body["chapter_id"])], strict=bool(body.get("strict", False)))


@app.post("/gate/project")
def gate_project(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    return _run_cli(["gate", "project"], strict=bool(body.get("strict", False)))


@app.post("/pipeline/chapter")
def pipeline_chapter(body: dict[str, Any]) -> dict[str, Any]:
    return _run_cli(
        ["pipeline", "run", "chapter", str(body["chapter_id"])],
        strict=bool(body.get("strict", False)),
    )


@app.post("/pipeline/project")
def pipeline_project(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    return _run_cli(["pipeline", "run", "project"], strict=bool(body.get("strict", False)))


@app.get("/issues")
def list_issues(
    status: str | None = Query(default=None),
    severity: str | None = Query(default=None),
    scope: str | None = Query(default=None),
) -> dict[str, Any]:
    args = ["issue", "list"]
    if status:
        args.extend(["--status", status])
    if severity:
        args.extend(["--severity", severity])
    if scope:
        args.extend(["--scope", scope])
    return _run_cli(args)


@app.patch("/issues/{issue_id}")
def update_issue(issue_id: str, body: dict[str, Any]) -> dict[str, Any]:
    args = ["issue", "update", issue_id, "--status", body["status"]]
    if body.get("note"):
        args.extend(["--note", str(body["note"])])
    return _run_cli(args)


@app.post("/issues/{issue_id}/waive")
def waive_issue(issue_id: str, body: dict[str, Any]) -> dict[str, Any]:
    return _run_cli(
        [
            "issue",
            "waive",
            issue_id,
            "--reason",
            str(body["reason"]),
            "--reviewer",
            str(body["reviewer"]),
        ]
    )


@app.post("/lore/delta")
def lore_delta(body: dict[str, Any]) -> dict[str, Any]:
    args = ["lore", "delta", "--scope", str(body["scope"])]
    if body.get("id") is not None:
        args.extend(["--id", str(body["id"])])
    if body.get("since") is not None:
        args.extend(["--since", str(body["since"])])
    return _run_cli(args)


@app.post("/lore/approve")
def lore_approve(body: dict[str, Any]) -> dict[str, Any]:
    args = [
        "lore",
        "approve",
        "--proposal",
        str(body["proposal"]),
        "--reviewer",
        str(body["reviewer"]),
    ]
    if body.get("note"):
        args.extend(["--note", str(body["note"])])
    return _run_cli(args)


@app.post("/lore/sync")
def lore_sync(body: dict[str, Any]) -> dict[str, Any]:
    args = ["lore", "sync", "--proposal", str(body["proposal"])]
    if bool(body.get("apply")):
        args.append("--apply")
    return _run_cli(args)


@app.post("/reports/build")
def report_build(body: dict[str, Any]) -> dict[str, Any]:
    args = ["report", "build", "--scope", str(body["scope"])]
    if body.get("id") is not None:
        args.extend(["--id", str(body["id"])])
    return _run_cli(args)


@app.get("/reports/open")
def report_open(
    scope: str = Query(..., pattern="^(chapter|project)$"),
    id: int | None = Query(default=None),
) -> dict[str, Any]:
    args = ["report", "open", "--scope", scope]
    if id is not None:
        args.extend(["--id", str(id)])
    return _run_cli(args)


@app.get("/runs")
def runs_list() -> dict[str, Any]:
    return _run_cli(["run", "list"])


@app.get("/runs/{run_id}")
def run_get(run_id: str) -> dict[str, Any]:
    return _run_cli(["run", "show", run_id])


@app.get("/chapters/{chapter_id}/content")
def chapter_content(chapter_id: int) -> dict[str, Any]:
    return _run_cli(["chapter", "content", str(chapter_id)])


@app.get("/rules")
def rules_get() -> dict[str, Any]:
    return _run_cli(["rules", "get"])


@app.get("/settings")
def settings_get() -> dict[str, Any]:
    return _run_cli(["settings", "get"])


@app.patch("/settings")
def settings_patch(body: dict[str, Any]) -> dict[str, Any]:
    return _run_cli(["settings", "patch", "--patch-json", json.dumps(body)])


@app.get("/artifacts/chapter/{chapter_id}/analysis")
def artifact_chapter_analysis(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "analysis.json")


@app.get("/artifacts/chapter/{chapter_id}/gate")
def artifact_chapter_gate(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "gate.json")


@app.get("/artifacts/chapter/{chapter_id}/decision-log")
def artifact_chapter_decision_log(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "decision-log.json")


@app.get("/artifacts/chapter/{chapter_id}/continuity")
def artifact_chapter_continuity(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "continuity.json")


@app.get("/artifacts/chapter/{chapter_id}/style-audit")
def artifact_chapter_style(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "style-audit.json")


@app.get("/artifacts/chapter/{chapter_id}/lore-delta")
def artifact_chapter_lore_delta(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / f"chapter-{chapter_id}" / "lore-delta.json")


@app.get("/artifacts/chapter/{chapter_id}/agent-results")
def artifact_chapter_agent_results(chapter_id: int) -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    path = output_dir / f"chapter-{chapter_id}" / "agent-results.json"
    if not path.exists():
        return _envelope(ok=False, data=[], exit_code=1, stderr=f"artifact not found: {path}")
    payload = load_json(path, default=[])
    return _envelope(ok=True, data=payload if isinstance(payload, list) else [], exit_code=0, stderr="")


@app.get("/artifacts/project/gate")
def artifact_project_gate() -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / "project" / "gate.json")


@app.get("/artifacts/project/open-issues")
def artifact_project_open_issues() -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / "project" / "open-issues.json")


@app.get("/artifacts/project/resolved-issues")
def artifact_project_resolved_issues() -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / "project" / "resolved-issues.json")


@app.get("/artifacts/project/timeline")
def artifact_project_timeline() -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / "project" / "timeline-status.json")


@app.get("/artifacts/project/motifs")
def artifact_project_motifs() -> dict[str, Any]:
    _project_root, output_dir = _api_context()
    return _read_artifact(output_dir / "project" / "motif-dashboard.json")


# ---------------------------------------------------------------------------
# Semantic search (indexer) — lazy-import BookIndex to avoid loading model at startup
# ---------------------------------------------------------------------------


def _semantic_index_context() -> tuple[Path, Path]:
    """Return (chapters_dir, persist_dir) for the semantic index."""
    project_root, _ = _api_context()
    config = load_runtime_config(project_root=project_root)
    persist_dir = project_root / ".book_index"
    return config.chapters_dir, persist_dir


@app.post("/search/semantic")
def search_semantic(body: dict[str, Any]) -> dict[str, Any]:
    """Semantic search at a given level."""
    try:
        chapters_dir, persist_dir = _semantic_index_context()
        from indexer.embedder import BookIndex

        idx = BookIndex(persist_dir=persist_dir, chapters_dir=chapters_dir)
        where = {}
        if body.get("act"):
            where["act"] = body["act"]
        if body.get("chapter_num") is not None:
            where["chapter_num"] = body["chapter_num"]
        if body.get("hybrid"):
            results = idx.query_hybrid(
                text=body["query"],
                level=body.get("level", "paragraph"),
                n_results=body.get("n_results", 10),
                where=where or None,
            )
        else:
            results = idx.query(
                text=body["query"],
                level=body.get("level", "paragraph"),
                n_results=body.get("n_results", 10),
                where=where or None,
            )
        return _envelope(ok=True, data={"results": results}, exit_code=0, stderr="")
    except FileNotFoundError as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))
    except (ValueError, KeyError) as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))


@app.post("/search/semantic/drill")
def search_semantic_drill(body: dict[str, Any]) -> dict[str, Any]:
    """Hierarchical drill-down search."""
    try:
        chapters_dir, persist_dir = _semantic_index_context()
        from indexer.embedder import BookIndex

        idx = BookIndex(persist_dir=persist_dir, chapters_dir=chapters_dir)
        results = idx.query_hierarchical(
            text=body["query"],
            top_level=body.get("top_level", "chapter"),
            drill_level=body.get("drill_level", "paragraph"),
            n_top=body.get("n_top", 3),
            n_drill=body.get("n_drill", 5),
        )
        return _envelope(ok=True, data={"results": results}, exit_code=0, stderr="")
    except FileNotFoundError as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))
    except (ValueError, KeyError) as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))


@app.get("/search/semantic/stats")
def search_semantic_stats() -> dict[str, Any]:
    """Return index statistics."""
    try:
        chapters_dir, persist_dir = _semantic_index_context()
        from indexer.embedder import BookIndex

        idx = BookIndex(persist_dir=persist_dir, chapters_dir=chapters_dir)
        counts = idx.stats()
        if sum(counts.values()) == 0:
            return _envelope(
                ok=False,
                data={},
                exit_code=1,
                stderr="Index is empty. Run POST /search/semantic/build first.",
            )
        return _envelope(ok=True, data={"counts": counts}, exit_code=0, stderr="")
    except FileNotFoundError as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))


@app.post("/search/semantic/build")
def search_semantic_build(body: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build or rebuild the semantic index."""
    try:
        chapters_dir, persist_dir = _semantic_index_context()
        from indexer.embedder import BookIndex

        idx = BookIndex(persist_dir=persist_dir, chapters_dir=chapters_dir)
        body = body or {}
        counts = idx.build(force=bool(body.get("force", False)))
        return _envelope(ok=True, data={"counts": counts}, exit_code=0, stderr="")
    except FileNotFoundError as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))
    except (ValueError, KeyError) as e:
        return _envelope(ok=False, data={}, exit_code=1, stderr=str(e))
