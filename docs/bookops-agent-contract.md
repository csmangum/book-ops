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

- `name`
- `summary`
- `findings`: structured observations
- `proposals`: concrete suggested edits/actions
- `confidence`: float 0..1
- `needs_human_decision`: bool

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
