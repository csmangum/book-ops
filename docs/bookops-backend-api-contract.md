# BookOps Backend API Contract (Implemented)

BookOps now ships a FastAPI backend (`bookops/api.py`) that exposes CLI-aligned
HTTP endpoints for the frontend.

## Response envelope

All endpoints return:

```json
{
  "ok": true,
  "exit_code": 0,
  "data": {},
  "stderr": ""
}
```

Exit code semantics:

- `0` success
- `1` runtime/command error
- `2` gate fail
- `3` pass with waivers

---

## Core endpoints

## Version / index / canon

- `GET /api/version`
- `POST /api/index/rebuild`
- `GET /api/index/status`
- `POST /api/canon/build`
- `GET /api/canon/validate`
- `POST /api/canon/diff`
- `GET /api/canon/graph` (new; graph payload for frontend)

## Analysis / gate / pipeline

- `POST /api/analyze/chapter`
- `POST /api/analyze/project`
- `POST /api/gate/chapter`
- `POST /api/gate/project`
- `POST /api/pipeline/chapter`
- `POST /api/pipeline/project`

Pipeline responses now include `run_id` so the UI can deep-link run details.

## Issues / lore

- `GET /api/issues`
- `PATCH /api/issues/{issueId}`
- `POST /api/issues/{issueId}/waive`
- `POST /api/lore/delta`
- `POST /api/lore/approve`
- `POST /api/lore/sync`

## Reports / artifacts

- `POST /api/reports/build`
- `GET /api/reports/open`
- `GET /api/artifacts/chapter/{chapterId}/analysis`
- `GET /api/artifacts/chapter/{chapterId}/gate`
- `GET /api/artifacts/chapter/{chapterId}/decision-log`
- `GET /api/artifacts/chapter/{chapterId}/continuity`
- `GET /api/artifacts/chapter/{chapterId}/style-audit`
- `GET /api/artifacts/chapter/{chapterId}/lore-delta`
- `GET /api/artifacts/project/gate`
- `GET /api/artifacts/project/open-issues`
- `GET /api/artifacts/project/resolved-issues`
- `GET /api/artifacts/project/timeline`
- `GET /api/artifacts/project/motifs`

---

## Newly implemented MVP endpoints

These were added to close the remaining frontend MVP blockers:

- `GET /api/runs` — run history list
- `GET /api/runs/{runId}` — run detail
- `GET /api/chapters/{chapterId}/content` — manuscript content for editor pane
- `GET /api/rules` — read rules payload
- `GET /api/settings` — read runtime config payload
- `PATCH /api/settings` — patch runtime config payload

---

## Backend implementation notes

- Most endpoints delegate to CLI (`bookops.cli.main`) with `--format json`.
- API reads/writes are rooted at:
  - `BOOKOPS_PROJECT` (defaults to current directory)
  - `BOOKOPS_OUTPUT_DIR` (defaults to `reports`)
- Artifact endpoints read generated JSON files directly from report paths.

---

## Source of truth

For exact request/response schemas and operation IDs, see:

- `openapi/bookops-api.openapi.yaml`
- generated TS client:
  - `clients/typescript/src/generated/schema.ts`
  - `clients/typescript/src/client.ts`
