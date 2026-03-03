# BookOps Rule Authoring Guide

A **rule** is a named, configurable check that BookOps runs over book content, project metadata, or pipeline artifacts. Each rule encodes a single policy or quality constraint (e.g. “no broken cross-references”, “chapters must have summaries”, “gate must not regress”).

**Purpose:** Rules give you consistent, automated enforcement of standards across chapters and projects. They power gates (pass/fail), reports, and trend signals so you can catch issues early, keep quality predictable, and avoid manual review for known patterns.

## Where rules live

- **Project rules file:** `canon/rules.yaml` under the project root. This is the source of truth at runtime; `RuntimeConfig.rules_path` points here.
- **Defaults:** If the file does not exist, `bookops init` (bootstrap) creates it by writing the built-in default rules (optionally via a template, e.g. `--template noir`). The codebase defines `DEFAULT_RULES` in `bookops/config.py`; loading falls back to that if the YAML file is missing or empty. You can override or extend the defaults by editing `canon/rules.yaml` after init.

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

## Example rule (YAML)

Copy and adapt this block when adding a new rule:

```yaml
- id: HARD.TENSE.CONSISTENCY
  kind: hard
  severity: high
  scope: chapter
  detector: tense_consistency
  params:
    primary_tense: past
    max_violations: 2
  message: Narrative tense drift exceeds threshold.
  gate_behavior: fail
  waiver_allowed: true
```

The `rules` key in `canon/rules.yaml` is a list of such entries; the file also has a top-level `version` and `policy` (e.g. gate and precedence settings).

## gate_behavior vs gate semantics

- **`gate_behavior`** on a rule describes how that rule's findings affect the gate: `fail` means "an unresolved finding at this rule's severity can make the gate fail"; `warn` means it contributes to warnings; `info` is informational.
- Gate evaluation uses **policy** (e.g. `fail_on_unresolved_severity`) to decide which severities are blocking. So a rule with `gate_behavior: fail` and `severity: critical` will cause a fail when the gate policy includes `critical` in `fail_on_unresolved_severity`. For full semantics (issue status, waivers, strict mode), see [bookops-architecture.md](bookops-architecture.md) § Gate semantics.

## Built-in detectors

These detector names are used by the default rules in `bookops/config.py`. Implementations live in `bookops/analyzers.py` (and related modules). Use these names in `detector` when adding or tuning rules.

| Detector | Scope | Description | Main params (typical) |
|----------|--------|-------------|------------------------|
| `tense_consistency` | chapter | Past/present tense drift | `primary_tense`, `max_violations` |
| `character_invariants` | chapter | Character invariant violations | `invariants` (list of invariant names) |
| `phrase_family_density` | chapter | Phrase-family repetition | `families`, `warn_threshold`, `high_threshold` |
| `motif_density` | chapter | Motif count per chapter | `motifs` (e.g. warn_per_chapter), `cluster_window_chapters` |
| `dialogue_voice_profile` | chapter | Dialogue voice drift | `drift_threshold`, `min_lines_for_eval` |
| `structure_overuse` | chapter | Structural pattern overuse | `patterns`, `warn_threshold` |
| `descriptor_stack` | chapter | Character descriptor stacking | `stacks` (char to list of phrases), `max_stack_occurrences` |
| `agency_heuristic` | chapter | Character agency drift | `target_characters`, `max_passive_key_beats` |
| `exposition_action_ratio` | chapter | Exposition vs action ratio | `warn_ratio`, `high_ratio`, `min_window_paragraphs` |
| `sensory_density` | chapter | Sensory saturation | `warn_threshold_per_paragraph`, `max_consecutive_saturated_paragraphs` |
| `chapter_day_sequence` | project | Day sequence across chapters | `max_out_of_order_events` |
| `near_verbatim_repeat` | project | Near-verbatim repetition across chapters | `similarity_threshold`, `min_tokens` |
| `timeline_anchor_check` | project | Absolute timeline anchor consistency | `require_canonical_match` |
| `object_state_tracker` | project | Tracked object state transitions | `tracked_objects`, `allow_impossible_transitions` |
| `pov_lock` | chapter | POV consistency | `allowed_pov`, `max_violations` |
| `entity_identity_check` | project | Entity identity/role conflicts | `disallow_alias_collision`, `disallow_role_conflicts` |
| `precedence_enforcer` | lore_sync | Manuscript-over-lore precedence | `manuscript_over_lore` |
| `open_issue_guard` | gate | Block on open issues above severity | `block_if_open_severity_at_or_above` |
| `causal_preconditions` | chapter | Event preconditions | `require_declared_preconditions` |
| `alert_deduplication` | report | Dedupe alerts for report | `dedupe_by_root_cause`, `max_low_priority_items_after_dedupe` |

Not all detectors are wired in every analysis run; chapter analysis uses a fixed set of checks (tense, invariants, repetition, motifs, voice). Project analysis runs timeline, near-verbatim, and lore-conflict checks. When adding a new rule, implement or hook the detector in the appropriate analysis path.

## Hard vs soft

- **Hard rules** block gates when violated (their severity is in `fail_on_unresolved_severity` and issue is open/in_progress).
- **Soft rules** produce warnings and trend signals; they do not make the gate fail unless `--strict` is used (which can promote lower severities to blocking).

## Adding a rule

1. Add rule entry to `canon/rules.yaml`.
2. Implement detector logic in `bookops/analyzers.py` (or relevant module) and wire it into `run_chapter_analysis` / `run_project_analysis` as needed.
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

