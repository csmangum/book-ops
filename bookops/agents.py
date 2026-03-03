from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config import RuntimeConfig


@dataclass
class AgentResult:
    name: str
    summary: str
    findings: list[dict[str, Any]]
    proposals: list[dict[str, Any]]
    confidence: float
    needs_human_decision: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def agent_findings_to_analysis_findings(
    agent_results: list[AgentResult],
    scope: str,
) -> list[dict[str, Any]]:
    """Convert agent findings to analyzer Finding shape for merge into issue store."""
    out: list[dict[str, Any]] = []
    for result in agent_results:
        for f in result.findings:
            out.append({
                "rule_id": f.get("rule_id", f"AGENT.{result.name}"),
                "severity": f.get("severity", "medium"),
                "message": f.get("message", ""),
                "scope": scope,
                "evidence": f.get("evidence", []),
                "title": f.get("title", f.get("message", "Agent finding")),
                "metadata": {"source_agent": result.name, **f.get("metadata", {})},
            })
    return out


AGENTS = {
    "story_architect": "Plan chapter against beat and canon constraints.",
    "drafter": "Generate/revise prose under hard rules.",
    "continuity_guardian": "Validate continuity and state transitions.",
    "lore_curator": "Propose lore updates from manuscript deltas.",
    "developmental_editor": "Assess structure, pacing, and stakes.",
    "line_editor": "Tighten prose and reduce repetition.",
    "proofreader": "Copy and proof consistency pass.",
    "release_manager": "Compile reports and gate recommendations.",
}

AGENT_PACK_VERSION = "0.1.0"


def list_agents() -> dict[str, str]:
    return AGENTS


def run_agent(
    name: str,
    scope: str,
    scope_id: int | None = None,
    config: RuntimeConfig | None = None,
) -> AgentResult:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent: {name}")

    import sys

    from .crewai_adapter import _has_llm_api_key, is_crewai_available, run_crewai_agent

    if config and is_crewai_available() and _has_llm_api_key():
        try:
            return run_crewai_agent(name, config, scope, scope_id)
        except Exception as exc:
            print(f"[bookops] CrewAI agent '{name}' failed: {exc}", file=sys.stderr)
            suffix = f" {scope_id}" if scope_id is not None else ""
            return AgentResult(
                name=name,
                summary=f"{name} failed for {scope}{suffix}: {exc}",
                findings=[],
                proposals=[],
                confidence=0.0,
                needs_human_decision=True,
            )

    suffix = f" {scope_id}" if scope_id is not None else ""
    return AgentResult(
        name=name,
        summary=f"{name} executed for {scope}{suffix}.",
        findings=[],
        proposals=[],
        confidence=0.62,
        needs_human_decision=False,
    )
