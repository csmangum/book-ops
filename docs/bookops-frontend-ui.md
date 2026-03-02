# BookOps Frontend UI Blueprint

This document captures a practical frontend UI for a larger BookOps agentic application.

## Product shape: Writer Ops Console

BookOps should be evidence-first and approval-driven, not chat-first:

- Diff-first workflow
- Evidence attached to every finding
- Human approval for sensitive actions (lore apply, hard-rule edits)
- Fast triage loops (resolve/waive/escalate)

## Core screens

## 1) Command Center (`/`)

Purpose: get operational status and next actions in under 30 seconds.

Primary blocks:

- Gate status cards (project/chapter)
- Top blockers
- Recent runs
- Changed since last run
- Quick actions:
  - Analyze chapter
  - Run chapter pipeline
  - Run project pipeline
  - Open latest report

## 2) Chapters (`/chapters`, `/chapters/:chapterId`)

### Chapter list (`/chapters`)

- Table columns: chapter #, title, last run, gate, criticals/highs, last edited
- Filters: gate status, severity, changed since ref
- Bulk analyze action

### Chapter workbench (`/chapters/:chapterId`)

Three-pane layout:

- Left: chapter navigator + section anchors
- Center: manuscript view/editor with diff toggle
- Right: findings panel
  - continuity
  - style
  - voice
  - lore impact
  - suggestions

Each finding should include rule ID, severity, evidence spans, and triage actions.

## 3) Lore Sync Studio (`/lore`, `/lore/:proposalId`)

- Proposal queue by status (`pending_review`, `approved`, `applied`, `rejected`)
- Side-by-side lore diff
- Evidence panel from chapter source
- Actions:
  - approve
  - reject
  - apply (only after approval)

Guardrail: warn/block on story-over-lore conflicts.

## 4) Timeline (`/timeline`)

- Horizontal chapter/day timeline rail
- Anchor markers and conflict overlays
- Marker details with source links
- Layer toggles (chapter markers, entity events, contradictions)

## 5) Canon Graph (`/canon`)

- Interactive entity relationship graph
- Filters by type (character/object/event/faction/location)
- Inspector panel with provenance
- Path tracing between entities

## 6) Rules (`/rules`)

- Hard and soft rule lists
- Rule details and threshold editing
- Sandbox run against a selected chapter
- Rule version comparison

Hard-rule edits require explicit confirmation and changelog note.

## 7) Runs (`/runs`, `/runs/:runId`)

- Pipeline run history
- Detailed run breakdown:
  - summary
  - findings
  - gate result
  - artifacts
  - decision log

## 8) Issues (`/issues`)

- Kanban + table modes
- Filters by scope/severity/status/rule/chapter
- Bulk actions for triage

## 9) Settings (`/settings`)

- Project paths/config
- Provider toggles
- Excluded dirs
- Report defaults
- Reviewer identity defaults
- CI status

## UX principles

1. Diff-first everywhere
2. Evidence-first findings (file + line references)
3. Low-noise interface and keyboard-driven triage
4. Strong write safety (no silent apply paths)
5. Consistent severity and gate badges across pages

## Suggested frontend stack

- Next.js + React
- Tailwind CSS + shadcn/ui
- TanStack Query for server state
- Monaco editor for chapter editing + diagnostics
- Cytoscape.js (graph) + visx (timeline)

## Route map

- `/`
- `/chapters`
- `/chapters/:id`
- `/lore`
- `/lore/:proposalId`
- `/timeline`
- `/canon`
- `/rules`
- `/runs`
- `/runs/:runId`
- `/issues`
- `/settings`

## MVP build order

1. Home
2. Chapters list + chapter workbench
3. Issues board
4. Lore sync studio
5. Runs
6. Timeline
7. Rules
8. Canon graph
