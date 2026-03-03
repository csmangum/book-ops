# BookOps Backend API Contract (Implemented)

BookOps ships a FastAPI backend (`bookops/api.py`) that exposes CLI-aligned
HTTP endpoints for the frontend.

**Base path:** When served (e.g. uvicorn), the app is typically mounted or prefixed so that all routes live under `/api`. Examples below use the full path `GET /api/version`, etc.

## Response envelope

All endpoints return a JSON envelope:

```json
{
  "ok": true,
  "exit_code": 0,
  "data": {},
  "stderr": ""
}
```

- **`ok`** — `true` when the operation completed without runtime error; `false` when the CLI or artifact read failed (e.g. `exit_code` 1).
- **`exit_code`** — `0` success; `1` runtime/command error; `2` gate fail; `3` pass with waivers. For pipeline/gate endpoints, 2 and 3 are treated as successful outcomes (`ok: true`) so the UI can show gate status.
- **`data`** — Operation result (CLI JSON output or artifact payload). Structure depends on endpoint; see below and OpenAPI/TS client for full schemas.
- **`stderr`** — CLI stderr or error message (e.g. "artifact not found: …").

## Error behavior

- **`ok: false`** — Returned when the CLI exits with code 1 (e.g. unknown command, missing project, validation failure) or when an artifact file is missing. `data` may be empty; `stderr` carries the message.
- **HTTP status** — The API typically returns HTTP 200 even when `ok: false`; the envelope carries the outcome. Unhandled server errors may return 5xx; for exact behavior see the FastAPI app and OpenAPI spec.

---

## Version / index / canon

| Method | Path | Request | Response `data` |
|--------|------|---------|------------------|
| GET | `/api/version` | — | Version metadata: `bookops_version`, `rules_schema_version`, `canon_schema_version`, `agent_pack_version`, `agent_count`. |
| POST | `/api/index/rebuild` | — | Index rebuild result (CLI JSON). |
| GET | `/api/index/status` | Query: `include_symbolic` (optional, default false) | Index status; with `include_symbolic=true`, full symbolic entries included. |
| POST | `/api/canon/build` | — | Canon build result (CLI JSON). |
| GET | `/api/canon/validate` | — | Validation result (CLI JSON). |
| POST | `/api/canon/diff` | Body: `{ "from_snapshot": "<path_or_id>", "to_snapshot": "<path_or_id>" }` | Diff result: `changed_days`, `entities_added`, `entities_removed`. |
| GET | `/api/canon/graph` | — | Graph payload for frontend (nodes/edges or equivalent). |

## Analysis / gate / pipeline

| Method | Path | Request | Response `data` |
|--------|------|---------|------------------|
| POST | `/api/analyze/chapter` | Body: `{ "chapter_id": number, "checks"?: string[], "since"?: string }` | Analysis payload: `scope`, `checks`, `generated_findings`. |
| POST | `/api/analyze/project` | Body (optional): `{ "since"?: string }` | Analysis payload: `scope: "project"`, `generated_findings`, `metrics`. |
| POST | `/api/gate/chapter` | Body: `{ "chapter_id": number, "strict"?: boolean }` | Gate result: `status`, `blocking_issue_ids`, `warning_issue_ids`, `message`. |
| POST | `/api/gate/project` | Body (optional): `{ "strict"?: boolean }` | Same gate result shape. |
| POST | `/api/pipeline/chapter` | Body: `{ "chapter_id": number, "strict"?: boolean }` | Pipeline result: `run_id`, `analysis`, `gate`, `run` (run entry with report_dir, decision_log path). |
| POST | `/api/pipeline/project` | Body (optional): `{ "strict"?: boolean }` | Pipeline result: `analysis`, `gate`, `run` (includes `run_id`). |

Pipeline responses include `run_id` so the UI can deep-link to run details.

## Issues / lore

| Method | Path | Request | Response `data` |
|--------|------|---------|------------------|
| GET | `/api/issues` | Query: `status`, `severity`, `scope` (all optional) | Issue list (CLI output, typically `{ "issues": [...] }` or equivalent). |
| PATCH | `/api/issues/{issueId}` | Body: `{ "status": "open"|"in_progress"|"resolved", "note"?: string }` | Updated issue store or confirmation. |
| POST | `/api/issues/{issueId}/waive` | Body: `{ "reason": string, "reviewer": string }` | Result of waive command. |
| POST | `/api/lore/delta` | Body: `{ "scope": "chapter"|"project", "id"?: number, "since"?: string }` | Lore delta payload: `proposals`, `scope`, `chapter_count_evaluated`, etc. |
| POST | `/api/lore/approve` | Body: `{ "proposal": string, "reviewer": string, "note"?: string }` | Approval result. |
| POST | `/api/lore/sync` | Body: `{ "proposal": string, "apply"?: boolean }` | Sync result. |

## Reports / artifacts

| Method | Path | Request | Response `data` |
|--------|------|---------|------------------|
| POST | `/api/reports/build` | Body: `{ "scope": "chapter"|"project", "id"?: number }` | Report build result (paths or CLI output). |
| GET | `/api/reports/open` | Query: `scope` (required: `chapter` or `project`), `id` (optional, chapter number) | Open report path or payload. |
| GET | `/api/artifacts/chapter/{chapterId}/analysis` | — | Contents of `reports/chapter-{id}/analysis.json`. 404 → `ok: false`, `exit_code: 1`, `stderr` "artifact not found: …". |
| GET | `/api/artifacts/chapter/{chapterId}/gate` | — | `gate.json` for that chapter. |
| GET | `/api/artifacts/chapter/{chapterId}/decision-log` | — | `decision-log.json`. |
| GET | `/api/artifacts/chapter/{chapterId}/continuity` | — | `continuity.json`. |
| GET | `/api/artifacts/chapter/{chapterId}/style-audit` | — | `style-audit.json`. |
| GET | `/api/artifacts/chapter/{chapterId}/lore-delta` | — | `lore-delta.json`. |
| GET | `/api/artifacts/project/gate` | — | `reports/project/gate.json`. |
| GET | `/api/artifacts/project/open-issues` | — | `open-issues.json`. |
| GET | `/api/artifacts/project/resolved-issues` | — | `resolved-issues.json`. |
| GET | `/api/artifacts/project/timeline` | — | `timeline-status.json`. |
| GET | `/api/artifacts/project/motifs` | — | `motif-dashboard.json`. |

## Runs / chapters / rules / settings (MVP)

| Method | Path | Request | Response `data` |
|--------|------|---------|------------------|
| GET | `/api/runs` | — | Run history: `{ "runs": [ { "run_id", "scope", "gate", "created_at", "report_dir", "decision_log_json" }, ... ] }`. |
| GET | `/api/runs/{runId}` | — | Single run detail (CLI `run show` output). |
| GET | `/api/chapters/{chapterId}/content` | — | Manuscript content for editor pane (chapter text or structured payload). |
| GET | `/api/rules` | — | Rules payload (from project rules YAML / default rules). |
| GET | `/api/settings` | — | Runtime config payload (paths, project, gates, etc.). |
| PATCH | `/api/settings` | Body: partial config object (e.g. `{ "project": { "chapters_dir": "chapters" } }`) | Patched settings result. |

---

## Backend implementation notes

- Most endpoints delegate to the CLI (`bookops.cli.main`) with `--format json`; request body and query params are translated to CLI args.
- API reads/writes are rooted at `BOOKOPS_PROJECT` (default current directory) and `BOOKOPS_OUTPUT_DIR` (default `reports`). Artifact endpoints read generated JSON files from `{output_dir}/chapter-{id}/` or `{output_dir}/project/`.
- One global lock serializes CLI invocations so concurrent requests do not interleave.

## Source of truth

For exact request/response schemas and operation IDs, see:

- `openapi/bookops-api.openapi.yaml`
- Generated TS client: `clients/typescript/src/generated/schema.ts`, `clients/typescript/src/client.ts`
