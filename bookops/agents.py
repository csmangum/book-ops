from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResult:
    name: str
    summary: str
    findings: list[dict[str, Any]]
    proposals: list[dict[str, Any]]
    confidence: float
    needs_human_decision: bool


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


def run_agent(name: str, scope: str, scope_id: int | None = None) -> AgentResult:
    if name not in AGENTS:
        raise ValueError(f"Unknown agent: {name}")
    suffix = f" {scope_id}" if scope_id is not None else ""
    return AgentResult(
        name=name,
        summary=f"{name} executed for {scope}{suffix}.",
        findings=[],
        proposals=[],
        confidence=0.62,
        needs_human_decision=False,
    )
