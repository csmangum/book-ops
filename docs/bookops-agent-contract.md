# BookOps Agent Contract

BookOps supports role-based editorial agents.

Current implementation includes agent registry and execution stubs in
`bookops/agents.py`. This contract defines the expected I/O shape for expanding
to model-backed agents.

## Input contract

- `name`: agent identifier
- `scope`: `chapter|project`
- `scope_id`: optional chapter id
- `context_pack` (future expansion):
  - chapter excerpts
  - canon slices
  - open issues
  - rule snippets

## Output contract (`AgentResult`)

- `name`: agent identifier
- `summary`: short human-readable summary of the run
- `findings`: list of structured observations (each with rule_id, severity, message, evidence, etc.)
- `proposals`: list of concrete suggested edits/actions (e.g. lore update proposals, text edits)
- `confidence`: float 0..1
- `needs_human_decision`: bool

**Example `AgentResult` (JSON-friendly):**

```json
{
  "name": "continuity_guardian",
  "summary": "continuity_guardian executed for chapter 3. One timeline inconsistency suggested.",
  "findings": [
    {
      "rule_id": "HARD.TIMELINE.DAY_SEQUENCE",
      "severity": "high",
      "message": "Day 4 appears after Day 5 in chapter.",
      "evidence": [
        { "file": "chapters/ch03.md", "line_start": 12, "line_end": 12, "excerpt": "Day 4 dawned." }
      ]
    }
  ],
  "proposals": [],
  "confidence": 0.85,
  "needs_human_decision": true
}
```

## Pipeline integration

- **Default chapter pipeline** runs four agents in order: `developmental_editor` → `continuity_guardian` → `line_editor` → `proofreader` (see `DEFAULT_CHAPTER_AGENT_FLOW` in `bookops/pipeline.py`). The project pipeline does not run agents.
- **Current behavior:** These are **stubs**. `run_agent` returns a placeholder `AgentResult` (e.g. empty findings/proposals, fixed confidence); no files are written and the pipeline does not yet merge agent findings into the issue store or agent proposals into lore.
- **Model-backed extension:** When adding real agents, findings should be converted to the same shape as analyzer findings and merged into the issue store (e.g. via the same fingerprint/merge logic in `bookops/issues.py`). Proposals (e.g. lore updates) flow through the existing lore proposal/approve/sync path so that manuscript-over-lore policy and auditability are preserved.
- **Agent proposals → lore:** Proposals with `kind: "lore_update"` are converted by `agent_proposals_to_lore_proposals` in `bookops/lore.py` and merged into the lore delta. Target lore file is inferred from content (e.g. "lore/Harry.md") when possible.

## Context pack (future)

The input contract reserves a **context_pack** for future use. Intended contents so implementers can design against a stable shape:

- **chapter excerpts:** Selected passages from the target chapter (e.g. by section or line range) as plain text or structured spans, for context without sending the full manuscript.
- **canon slices:** Subset of the canon payload relevant to the scope (e.g. timeline entries for the chapter’s days, entities mentioned in the chapter) so the agent can check continuity without loading the full canon.
- **open issues:** List of open (and optionally in_progress) issues for the scope (chapter or project) so the agent can avoid duplicating known issues and can reference them in summaries.
- **rule snippets:** Relevant rule definitions (id, message, params) for the detectors that apply to this scope, so the agent can align findings with rule IDs and severities.

## Operational rules

- agents do not directly mutate chapters or lore
- lore changes must flow through proposal + approval path
- all agent outputs are auditable
- gate decisions are deterministic and separate from agent opinion

## Extending with model-backed agents

1. Keep `AgentResult` schema stable.
2. Add adapter layer for model provider calls.
3. Enforce strict max context and deterministic post-processing.
4. Require evidence snippets for high-severity findings.

## CrewAI integration

BookOps includes a CrewAI adapter (`bookops/crewai_adapter.py`) for model-backed agents:

- **When used:** If `crewai` is installed and `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is set, `run_agent` uses CrewAI to execute agents with full context.
- **Context pack:** Built by `bookops/context_pack.py` from chapter excerpts, canon slices, open issues, and rule snippets.
- **Fallback:** Without CrewAI or API key, agents run as stubs (empty findings/proposals).
- **Install:** `pip install crewai`
