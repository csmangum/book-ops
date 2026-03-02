# BookOps Architecture

BookOps is a local-first agentic framework for book writing quality assurance,
continuity enforcement, lore synchronization, and editorial workflow automation.

## System layout

- **Control plane**
  - CLI command routing (`bookops.cli`)
  - Pipeline orchestration (`bookops.pipeline`)
  - Gate evaluation (`bookops.gates`)
- **Data plane**
  - Source corpus (`chapters/`, `lore/`, guide docs)
  - Canon store (`canon/*.yaml`)
  - Runtime state (`.bookops/*`)
  - Reports (`reports/*`)

## Major modules

- `bookops/config.py`
  - bootstraps config and default rule set
  - loads runtime paths and policies
- `bookops/ingest.py`
  - chapter/lore loading and marker extraction
- `bookops/canon.py`
  - canon snapshot build, validate, diff
- `bookops/analyzers.py`
  - deterministic continuity/style analyzers
- `bookops/issues.py`
  - issue lifecycle persistence and summaries
- `bookops/lore.py`
  - proposal-based lore sync with precedence guardrails
- `bookops/reports.py`
  - markdown/json report rendering
- `bookops/pipeline.py`
  - chapter/project end-to-end orchestrated runs

## Execution flow

### Chapter flow
1. Analyze chapter
2. Persist issues
3. Run editorial agent stubs
4. Generate lore proposals
5. Evaluate gate
6. Render chapter reports

### Project flow
1. Analyze project
2. Persist issues
3. Evaluate global gate
4. Render project reports and blocker summary

## Gate semantics

- `pass`: no blocking issues
- `pass_with_waivers`: non-blocking issues present with at least one waiver
- `fail`: blocking severity unresolved

Exit codes:
- `0` pass
- `2` fail
- `3` pass_with_waivers

## Source-of-truth policy

BookOps enforces **manuscript-over-lore precedence** in lore sync operations.
Lore writes are blocked if policy is disabled or contradictory.
