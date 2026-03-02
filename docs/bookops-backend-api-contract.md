# BookOps Minimal Backend API Contract (CLI-aligned)

This API contract is intentionally thin and maps directly to existing `bookops` CLI commands and generated JSON artifacts.

## Design goals

1. Keep backend logic minimal.
2. Preserve existing CLI behavior and exit codes.
3. Return CLI JSON payloads with minimal transformation.
4. Support frontend orchestration and artifact retrieval.

## Uniform response envelope

```json
{
  "ok": true,
  "exit_code": 0,
  "data": {},
  "stderr": ""
}
```

- `exit_code` follows BookOps semantics:
  - `0` success
  - `1` runtime/command error
  - `2` gate fail
  - `3` pass with waivers

---

## Core endpoints

## Version / index / canon

### `GET /api/version`
CLI: `bookops version`

`data`:

```json
{
  "bookops_version": "0.1.0",
  "rules_schema_version": 1,
  "canon_schema_version": 1,
  "agent_pack_version": "v1",
  "agent_count": 4
}
```

### `POST /api/index/rebuild`
CLI: `bookops index rebuild`

`data` (example shape):

```json
{
  "index_version": 2,
  "generated_at": "2026-03-01T00:00:00Z",
  "project_root": "/workspace",
  "file_count": 55,
  "excluded_dirs": [".bookops", ".git", "reports"],
  "corpus_hash": "sha256...",
  "symbolic": [
    {
      "path": "chapters/1_The Last Man Who Still Used a Door Key.md",
      "sha256": "sha256...",
      "size": 12007,
      "line_count": 125,
      "modified_at": 1772328195.366
    }
  ]
}
```

### `GET /api/index/status`
CLI: `bookops index status`

`data`:

```json
{
  "symbolic_exists": true,
  "semantic_exists": true,
  "symbolic_path": "/workspace/.bookops/index/symbolic.json",
  "semantic_path": "/workspace/.bookops/index/semantic.json",
  "index_version": 2,
  "generated_at": "2026-03-01T00:00:00Z",
  "file_count": 55,
  "corpus_hash": "sha256...",
  "semantic_status": "stub",
  "semantic_source_file_count": 55
}
```

### `POST /api/canon/build`
CLI: `bookops canon build`

`data`:

```json
{
  "snapshot": "/workspace/.bookops/snapshots/canon-....json",
  "chapter_count": 26
}
```

### `GET /api/canon/validate`
CLI: `bookops canon validate`

`data`:

```json
{
  "valid": true,
  "errors": []
}
```

### `POST /api/canon/diff`
CLI: `bookops canon diff --from <snapshot> --to <snapshot>`

Request:

```json
{
  "from_snapshot": "canon-a.json",
  "to_snapshot": "canon-b.json"
}
```

`data`: direct CLI diff JSON.

---

## Analysis, gate, pipeline

### `POST /api/analyze/chapter`
CLI: `bookops analyze chapter <chapter_id> [--checks ...] [--since ...]`

Request:

```json
{
  "chapter_id": 14,
  "checks": ["repetition", "motifs"],
  "since": "HEAD~1"
}
```

`data`:

```json
{
  "scope": "chapter:14",
  "findings": 5,
  "checks": ["motifs", "repetition"],
  "skipped": false
}
```

### `POST /api/analyze/project`
CLI: `bookops analyze project [--since ...]`

Request:

```json
{
  "since": "HEAD~1"
}
```

`data`:

```json
{
  "scope": "project",
  "findings": 12,
  "chapter_filter_count": 3
}
```

### `POST /api/gate/chapter`
CLI: `bookops gate chapter <chapter_id> [--strict]`

Request:

```json
{
  "chapter_id": 14,
  "strict": true
}
```

`data`:

```json
{
  "status": "fail",
  "blocking_issue_ids": ["ISSUE-abc123"],
  "warning_issue_ids": ["ISSUE-def456"],
  "message": "Blocking issues detected."
}
```

### `POST /api/gate/project`
CLI: `bookops gate project [--strict]`

Request:

```json
{
  "strict": false
}
```

`data`: same shape as chapter gate.

### `POST /api/pipeline/chapter`
CLI: `bookops pipeline run chapter <chapter_id> [--strict]`

Request:

```json
{
  "chapter_id": 14,
  "strict": false
}
```

`data`:

```json
{
  "gate": "pass_with_waivers",
  "scope": "chapter:14"
}
```

### `POST /api/pipeline/project`
CLI: `bookops pipeline run project [--strict]`

Request:

```json
{
  "strict": false
}
```

`data`:

```json
{
  "gate": "pass",
  "scope": "project"
}
```

---

## Issues and lore workflows

### `GET /api/issues`
CLI: `bookops issue list [--status ...] [--severity ...] [--scope ...]`

Query params:

- `status`: `open|in_progress|resolved|waived`
- `severity`: `critical|high|medium|low|info`
- `scope`: `chapter|project|chapter:14`

`data`:

```json
{
  "count": 17,
  "issues": [
    {
      "id": "ISSUE-abc123",
      "rule_id": "HARD.TIMELINE.DAY_SEQUENCE",
      "severity": "high",
      "status": "open",
      "scope": "chapter:12",
      "message": "..."
    }
  ]
}
```

### `PATCH /api/issues/{issue_id}`
CLI: `bookops issue update <issue_id> --status <...> --note "..."`

Request:

```json
{
  "status": "resolved",
  "note": "fixed in chapter rewrite"
}
```

`data`:

```json
{
  "updated": "ISSUE-abc123",
  "issue_count": 17
}
```

### `POST /api/issues/{issue_id}/waive`
CLI: `bookops issue waive <issue_id> --reason "..." --reviewer "..."`

Request:

```json
{
  "reason": "intentional style choice",
  "reviewer": "cmangum"
}
```

`data`:

```json
{
  "waived": "ISSUE-abc123",
  "issue_count": 17
}
```

### `POST /api/lore/delta`
CLI: `bookops lore delta --scope <chapter|project> [--id ...] [--since ...]`

Request:

```json
{
  "scope": "chapter",
  "id": 14,
  "since": null
}
```

`data`:

```json
{
  "scope": "chapter:14",
  "proposals": 3,
  "chapter_count_evaluated": 1
}
```

### `POST /api/lore/approve`
CLI: `bookops lore approve --proposal <id> --reviewer <name> [--note ...]`

Request:

```json
{
  "proposal": "proposal-14-olive-greer",
  "reviewer": "cmangum",
  "note": "looks right"
}
```

`data`:

```json
{
  "approved": "proposal-14-olive-greer",
  "reviewer": "cmangum"
}
```

### `POST /api/lore/sync`
CLI: `bookops lore sync --proposal <id> --apply`

Request:

```json
{
  "proposal": "proposal-14-olive-greer",
  "apply": true
}
```

`data`:

```json
{
  "applied": "proposal-14-olive-greer",
  "target": "lore/Olive Greer.md"
}
```

---

## Reports and artifacts

Because BookOps writes report artifacts to disk, expose read endpoints for frontend rendering.

### `POST /api/reports/build`
CLI: `bookops report build --scope <chapter|project> [--id ...]`

Request:

```json
{
  "scope": "chapter",
  "id": 14
}
```

### `GET /api/reports/open`
CLI: `bookops report open --scope <chapter|project> [--id ...]`

Query:

- `scope=chapter|project`
- `id` (required for chapter scope)

`data`:

```json
{
  "path": "/workspace/reports/chapter-14"
}
```

### Suggested artifact-read endpoints

- `GET /api/artifacts/chapter/:id/analysis` → `reports/chapter-:id/analysis.json`
- `GET /api/artifacts/chapter/:id/gate` → `reports/chapter-:id/gate.json`
- `GET /api/artifacts/chapter/:id/decision-log` → `reports/chapter-:id/decision-log.json`
- `GET /api/artifacts/chapter/:id/continuity` → `reports/chapter-:id/continuity.json`
- `GET /api/artifacts/chapter/:id/style-audit` → `reports/chapter-:id/style-audit.json`
- `GET /api/artifacts/chapter/:id/lore-delta` → `reports/chapter-:id/lore-delta.json`
- `GET /api/artifacts/project/gate` → `reports/project/gate.json`
- `GET /api/artifacts/project/open-issues` → `reports/project/open-issues.json`
- `GET /api/artifacts/project/resolved-issues` → `reports/project/resolved-issues.json`
- `GET /api/artifacts/project/timeline` → `reports/project/timeline-status.json`
- `GET /api/artifacts/project/motifs` → `reports/project/motif-dashboard.json`

---

## Implementation note

Recommended backend pattern:

- Endpoint handler builds CLI args.
- Executes `python -m bookops --format json ...`.
- Captures `stdout`, `stderr`, and process exit code.
- Wraps parsed output in uniform envelope.
- Uses direct file reads for artifact endpoints.

This keeps the app fully aligned with current BookOps behavior while enabling a rich frontend.
