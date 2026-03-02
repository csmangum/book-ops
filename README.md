# BookOps

BookOps is a local-first editorial QA framework for long-form writing, with:

- CLI workflows for analysis, gating, lore sync, reports, and issue lifecycle
- FastAPI backend exposing `/api/*` endpoints for frontend orchestration
- Next.js frontend (`frontend/`) implementing the Writer Ops Console

## Quick start

## 1) Python environment + dependencies

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-bookops.txt
```

## 2) Initialize project scaffolding

```bash
python -m bookops init
```

## 3) Run API server

```bash
export BOOKOPS_PROJECT=/workspace
export BOOKOPS_OUTPUT_DIR=reports
uvicorn bookops.api:app --reload --host 0.0.0.0 --port 8000
```

## 4) Run frontend

```bash
cd frontend
npm install
cp .env.example .env.local
# set NEXT_PUBLIC_API_URL if needed, e.g. http://localhost:8000/api
npm run dev
```

## Useful docs

- `docs/bookops-operations-runbook.md`
- `docs/bookops-backend-api-contract.md`
- `docs/bookops-frontend-ui.md`
- `docs/bookops-frontend-component-tree.md`