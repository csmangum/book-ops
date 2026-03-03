# BookOps

BookOps is a local-first agentic framework for book-writing with continuity enforcement, lore synchronization, and editorial workflow automation. **Local-first** means your manuscript, canon, and runtime state live on disk; no cloud is required, and the API/CLI operate on the directory set in `BOOKOPS_PROJECT`. A Next.js frontend (`frontend/`) provides the Writer Ops Console; a FastAPI backend serves `/api/*` and the CLI covers analysis, gating, lore sync, reports, and issue lifecycle.

## Prerequisites

- Python 3.12
- Node.js and npm (only if you run the frontend)

## Backend: install and run

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-bookops.txt
```

Set environment (e.g. project root and report output):

```bash
export BOOKOPS_PROJECT=/path/to/your/project
export BOOKOPS_OUTPUT_DIR=reports
```

Bootstrap project files, then start the API:

```bash
python -m bookops init
# optional: python -m bookops init --template noir
uvicorn bookops.api:app --reload --host 0.0.0.0 --port 8000
```

## Frontend: install and run

```bash
cd frontend
npm install
cp .env.example .env.local
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` if needed (e.g. `http://localhost:8000/api`), then:

```bash
npm run dev
```

## Testing

```bash
# Backend (from repo root, with venv activated)
pytest tests/ -v

# Frontend unit tests
cd frontend && npm run test

# E2E (Playwright; uses backend + frontend)
cd frontend && npm run test:e2e
```

## Documentation

- [bookops-operations-runbook.md](docs/bookops-operations-runbook.md) — Prerequisites, first-time setup, daily CLI workflows (analyze, gate, report, lore, issues, runs)
- [bookops-architecture.md](docs/bookops-architecture.md) — System layout, modules, execution flow, gate semantics
- [bookops-backend-api-contract.md](docs/bookops-backend-api-contract.md) — FastAPI endpoints and response envelope for the frontend
- [bookops-frontend-ui.md](docs/bookops-frontend-ui.md) — Writer Ops Console UI blueprint and route overview
- [bookops-frontend-component-tree.md](docs/bookops-frontend-component-tree.md) — Next.js App Router component tree
- [bookops-rule-authoring.md](docs/bookops-rule-authoring.md) — Rules in `canon/rules.yaml`: kinds, thresholds, templates
- [bookops-agent-contract.md](docs/bookops-agent-contract.md) — Role-based editorial agents: registry, I/O contract, stubs

