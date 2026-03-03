"""CrewAI adapter for model-backed editorial agents."""

from __future__ import annotations

import json
import os
from typing import Any

from .agents import AGENTS, AgentResult
from .context_pack import build_context_pack
from .config import RuntimeConfig

_CREWAI_AVAILABLE = False
try:
    from crewai import Agent, Crew, Task
    from pydantic import BaseModel, Field

    _CREWAI_AVAILABLE = True
except ImportError:
    pass


def is_crewai_available() -> bool:
    return _CREWAI_AVAILABLE


def _has_llm_api_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"))


# Pydantic models for structured agent output (only when CrewAI available)
if _CREWAI_AVAILABLE:

    class EvidenceItem(BaseModel):
        file: str = Field(default="", description="Source file path")
        line_start: int = Field(default=0, description="Start line number")
        line_end: int = Field(default=0, description="End line number")
        excerpt: str = Field(default="", description="Text excerpt")

    class AgentFindingOutput(BaseModel):
        rule_id: str = Field(..., description="Rule identifier, e.g. HARD.TIMELINE.DAY_SEQUENCE")
        severity: str = Field(default="medium", description="critical, high, medium, low")
        message: str = Field(..., description="Human-readable finding description")
        evidence: list[EvidenceItem] = Field(default_factory=list, description="Evidence for the finding")

    class AgentProposalOutput(BaseModel):
        kind: str = Field(default="lore_update", description="Proposal type")
        content: str = Field(default="", description="Proposal description or content")

    class AgentResultOutput(BaseModel):
        summary: str = Field(..., description="Short human-readable summary of the run")
        findings: list[AgentFindingOutput] = Field(default_factory=list, description="Structured observations")
        proposals: list[AgentProposalOutput] = Field(default_factory=list, description="Suggested edits or actions")
        confidence: float = Field(default=0.5, ge=0, le=1, description="Confidence in this analysis 0-1")
        needs_human_decision: bool = Field(default=False, description="Whether this requires human review")


def _format_context_pack(pack: dict[str, Any]) -> str:
    """Format context pack as readable text for the LLM."""
    parts = []

    if pack.get("chapter_excerpts"):
        parts.append("## Chapter excerpts\n")
        for ex in pack["chapter_excerpts"]:
            parts.append(f"### Chapter {ex.get('chapter_id')}: {ex.get('title')} ({ex.get('path')})\n")
            parts.append(ex.get("text", "")[:8000])
            parts.append("\n")

    if pack.get("canon_slices"):
        cs = pack["canon_slices"]
        parts.append("## Canon (timeline)\n")
        parts.append(f"Chapter days: {json.dumps(cs.get('chapter_days', {}))}\n")
        if cs.get("dates"):
            parts.append(f"Dates: {json.dumps(cs.get('dates', [])[:15])}\n")
        if cs.get("entities"):
            parts.append(f"Entities: {json.dumps([e.get('name') for e in cs.get('entities', [])[:20]])}\n")

    if pack.get("open_issues"):
        parts.append("## Open issues (avoid duplicating)\n")
        for i in pack["open_issues"]:
            parts.append(f"- [{i.get('id')}] {i.get('rule_id')}: {i.get('message')}\n")

    if pack.get("rule_snippets"):
        parts.append("## Rule snippets (use these rule_ids for findings)\n")
        for r in pack["rule_snippets"]:
            parts.append(f"- {r.get('id')}: {r.get('message')} (severity: {r.get('severity')})\n")

    return "\n".join(parts) if parts else "No context available."


def run_crewai_agent(
    agent_name: str,
    config: RuntimeConfig,
    scope: str,
    scope_id: int | None = None,
) -> AgentResult:
    """Run a CrewAI-backed agent and return AgentResult."""
    if not _CREWAI_AVAILABLE:
        raise RuntimeError("CrewAI is not installed. pip install crewai")

    if agent_name not in AGENTS:
        raise ValueError(f"Unknown agent: {agent_name}")

    pack = build_context_pack(config, scope, scope_id)
    context_text = _format_context_pack(pack)

    role_map = {
        "developmental_editor": ("Developmental Editor", "Assess structure, pacing, and stakes in manuscript chapters.", "Expert editor focused on narrative structure."),
        "continuity_guardian": ("Continuity Guardian", "Validate timeline continuity and state transitions across the manuscript.", "Expert at continuity and fact-checking."),
        "line_editor": ("Line Editor", "Tighten prose and reduce repetition.", "Expert at line-level editing."),
        "proofreader": ("Proofreader", "Copy and proof consistency pass.", "Expert proofreader."),
    }
    role, goal, backstory = role_map.get(
        agent_name,
        ("Editorial Agent", AGENTS[agent_name], "Expert editorial assistant."),
    )

    agent = Agent(
        role=role,
        goal=goal,
        backstory=backstory,
        verbose=False,
    )

    task_desc = f"""Review the manuscript context below and produce editorial findings.

You are {role}. {goal}

Context:
{context_text}

For each issue you find, provide a finding with rule_id (use rule IDs from the rule snippets when applicable, or AGENT.{agent_name} for custom findings), severity (critical/high/medium/low), message, and evidence with file, line_start, line_end, excerpt.
If you find no issues, return an empty findings list.
For lore_update proposals: include the target file in content (e.g. "Update lore/Harry.md with...") so the system can route the proposal. Proposals flow through the approve/sync path.
Provide a brief summary and confidence (0-1). Set needs_human_decision true if any finding requires human review."""

    task = Task(
        description=task_desc,
        expected_output="Structured editorial analysis with findings, proposals, summary, confidence, and needs_human_decision.",
        agent=agent,
        output_pydantic=AgentResultOutput,
    )

    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()

    if not result.tasks_output or not result.tasks_output[0].pydantic:
        return AgentResult(
            name=agent_name,
            summary=f"{agent_name} completed but produced no structured output.",
            findings=[],
            proposals=[],
            confidence=0.5,
            needs_human_decision=False,
        )

    out = result.tasks_output[0].pydantic
    findings = [
        {
            "rule_id": f.rule_id,
            "severity": f.severity,
            "message": f.message,
            "evidence": [{"file": e.file, "line_start": e.line_start, "line_end": e.line_end, "excerpt": e.excerpt} for e in f.evidence],
        }
        for f in out.findings
    ]
    proposals = [
        {"kind": p.kind, "content": p.content}
        for p in out.proposals
    ]

    return AgentResult(
        name=agent_name,
        summary=out.summary,
        findings=findings,
        proposals=proposals,
        confidence=out.confidence,
        needs_human_decision=out.needs_human_decision,
    )
