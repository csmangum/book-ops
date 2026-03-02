# BookOps Rule Authoring Guide

Rules live in `canon/rules.yaml`.

Each rule has:

- `id`: stable identifier
- `kind`: `hard` or `soft`
- `severity`: `critical|high|medium|low|info`
- `scope`: `chapter|project|lore_sync|gate|report`
- `detector`: analyzer hook name
- `params`: detector configuration
- `message`: issue text
- `gate_behavior`: `fail|warn|info`
- `waiver_allowed`: boolean

## Hard vs soft

- **Hard rules** block gates when violated.
- **Soft rules** produce warnings and trend signals.

## Adding a rule

1. Add rule entry to `canon/rules.yaml`.
2. Implement detector logic in `bookops/analyzers.py` (or relevant module).
3. Emit `Finding` objects with evidence where possible.
4. Add unit tests in `tests/`.

## Detector design recommendations

- deterministic and fast by default
- include line-level evidence spans
- use bounded comparisons for large corpora
- avoid expensive O(n²) scans without candidate reduction

## Rule evolution

- keep `id` stable
- tune thresholds incrementally
- record rationale in git commit messages
- prefer waivers over disabling useful rules
