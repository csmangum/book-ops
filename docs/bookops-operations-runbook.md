# BookOps Operations Runbook

## Prerequisites

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements-bookops.txt
```

## First-time setup

```bash
python -m bookops init
python -m bookops init --template noir
python -m bookops template list
python -m bookops index rebuild
python -m bookops canon build
python -m bookops canon validate
```

## Daily chapter workflow

```bash
python -m bookops --format both analyze chapter <N>
python -m bookops --format both analyze chapter <N> --checks repetition,motifs
python -m bookops --format both pipeline run chapter <N>
python -m bookops --format both gate chapter <N>
python -m bookops --format both report build --scope chapter --id <N>

# Pipeline writes decision log:
# - reports/chapter-<N>/decision-log.md
```

## Project health workflow

```bash
python -m bookops --format both analyze project
python -m bookops --format both analyze project --since origin/main
python -m bookops --format both gate project
python -m bookops --format both report build --scope project
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

## Gate exit codes (CI-friendly)

- `0` pass
- `2` fail (blocking)
- `3` pass with waivers

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
