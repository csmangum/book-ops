# BookOps Operations Runbook

An **operations runbook** is a step-by-step reference for running and maintaining BookOps in production or development. It covers setup, daily workflows (chapters, project health, lore sync), issue handling, and troubleshooting so operators can run gates, build reports, and fix problems without hunting through code or docs.

## Prerequisites

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-bookops.txt
```

## Run backend API service

```bash
export BOOKOPS_PROJECT=/workspace
export BOOKOPS_OUTPUT_DIR=reports
uvicorn bookops.api:app --reload --host 0.0.0.0 --port 8000
```

- API base path: `/api`
- Response envelope: `{ ok, exit_code, data, stderr }`

## First-time setup

```bash
python -m bookops init
python -m bookops init --template noir
python -m bookops template list
python -m bookops index rebuild
python -m bookops canon build
python -m bookops canon validate
python -m bookops canon graph
```

## Daily chapter workflow

```bash
python -m bookops --format both analyze chapter <N>
python -m bookops --format both analyze chapter <N> --checks repetition,motifs
python -m bookops --format both pipeline run chapter <N>
python -m bookops --format both gate chapter <N>
python -m bookops --format both report build --scope chapter --id <N>
python -m bookops chapter content <N>

# Pipeline writes decision log:
# - reports/chapter-<N>/decision-log.md
```

## Project health workflow

```bash
python -m bookops --format both analyze project
python -m bookops --format both analyze project --since origin/main
python -m bookops --format both gate project
python -m bookops --format both report build --scope project
python -m bookops run list
```

## Lore sync workflow

```bash
python -m bookops lore delta --scope chapter --id <N>
python -m bookops lore delta --scope project --since origin/main
python -m bookops lore approve --proposal <proposal-id> --reviewer <name>
python -m bookops lore sync --proposal <proposal-id> --apply
```

## Issue lifecycle

```bash
python -m bookops issue list --scope chapter:<N>
python -m bookops issue update <issue-id> --status in_progress --note "Investigating"
python -m bookops issue update <issue-id> --status resolved --note "Fixed in chapter revision"
python -m bookops issue waive <issue-id> --reason "Intentional stylistic choice" --reviewer "<name>"
```

## Run history and inspection

```bash
python -m bookops run list
python -m bookops run show <run-id>
```

## Rules and settings read/write

```bash
python -m bookops rules get
python -m bookops settings get
python -m bookops settings patch --patch-json '{"project":{"chapters_dir":"chapters"}}'
```

## Multi-book semantic index

The API uses `paths.semantic_index_dir` (default `.book_index`) for semantic search. To query a different book's index (e.g. Alice):

```bash
python -m bookops settings patch --patch-json '{"paths":{"semantic_index_dir":".book_index_alice"}}'
```

Ensure `chapters_alice/` and `.book_index_alice/` exist (see "PDF ingest and manual testing").

## Gate exit codes (CI-friendly)

- `0` pass
- `2` fail (blocking)
- `3` pass with waivers

## When to use `--strict`

Use `--strict` when the gate should treat **warnings as blocking** (e.g. CI or pre-release). Normally only issues at severities in `fail_on_unresolved_severity` (e.g. `critical`) block the gate; with `--strict`, open issues at `high`, `medium`, or `low` also count as blocking. Example:

```bash
python -m bookops --format both pipeline run project --strict
```

## Expected output (snippets)

**Pipeline run chapter (success):** With `--format json`, stdout is JSON. You should see a payload with `run_id`, `gate` (e.g. `"status": "pass"` or `"fail"`), and `run` (report_dir, decision_log path). Example shape:

```json
{ "analysis": { ... }, "lore_delta": { ... }, "gate": { "status": "pass", "message": "Gate passed." }, "run": { "run_id": "...", "report_dir": "...", ... } }
```

**Issue list:** With `--format json`, output includes an `issues` array (or equivalent from the CLI). Each issue has `id`, `rule_id`, `severity`, `status`, `scope`, `message`. Use `--scope chapter:<N>` or `--status open` to narrow.

## Report build output

`report build --scope chapter --id <N>` (or `--scope project` without `--id`) (re)generates the standard reports for that scope. Outputs are written under:

- **Chapter:** `reports/chapter-<N>/` — analysis.md/json, gate.md/json, continuity.md/json, style-audit.md/json, lore-delta.md/json, decision-log.md/json.
- **Project:** `reports/project/` — analysis, gate, open-issues, resolved-issues, timeline-status, motif-dashboard, decision-log (md/json per `--format`).

Paths are relative to `BOOKOPS_OUTPUT_DIR` (default `reports`). Running the pipeline for that scope also produces these same files.

## Common troubleshooting

### `venv` creation fails (`ensurepip` missing)
- Install Python venv package:
  - Ubuntu: `sudo apt-get install -y python3.12-venv`

### Project analysis is slow
- Use chapter scope for fast iteration.
- Keep near-verbatim detectors candidate-reduced and bounded.

### Unexpected gate failures
- Run `issue list` with severity filters.
- Confirm unresolved `critical` issues.
- Use waiver only with explicit rationale.

### PDF ingest and manual testing

To test PDF ingest with a real PDF (e.g. Alice in Wonderland), download the public-domain text from [Project Gutenberg](https://www.gutenberg.org/ebooks/11) and save as `carroll-1865.pdf` in the project root. Then:

```bash
python -m indexer ingest-pdf carroll-1865.pdf --chapters-dir chapters_alice --book-id alice --build --index-dir .book_index_alice
python -m indexer search "rabbit hole" --index-dir .book_index_alice
```

**Note:** When using `--chapters-dir` with ingest-pdf, pass the same path to `build --chapters-dir` if you run build separately. The default for build is the project's `chapters/` directory.

Unit tests use a synthetic PDF fixture by default. Set `USE_REAL_PDF_TESTS=1` to run tests against the real PDF when present.

### `canon build` or `index rebuild` fails
- **Missing chapters dir:** Ensure `chapters/` exists under the project root (or the path set in config `project.chapters_dir`). Run `bookops init` if the project is new.
- **Invalid or missing YAML:** If `canon/rules.yaml` or other canon config is malformed, fix or remove the file and run `bookops init` again to regenerate defaults. For `index rebuild`, ensure no permission errors on project directories; check that excluded dirs (e.g. `.git`, `reports`) are correct.
