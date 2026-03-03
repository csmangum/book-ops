from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .templates import apply_template_to_rules
from .utils import dump_yaml, ensure_dir, load_yaml


DEFAULT_CONFIG = {
    "version": 1,
    "project": {
        "chapters_dir": "chapters",
        "lore_dir": "lore",
        "guides": ["writing-guide.md", "editing-guide.md", "outline.md", "edits.md"],
    },
    "paths": {
        "bookops_dir": ".bookops",
        "index_dir": ".bookops/index",
        "semantic_index_dir": ".book_index",
        "snapshots_dir": ".bookops/snapshots",
        "issues_file": ".bookops/issues.json",
        "run_history_file": ".bookops/runs.json",
        "canon_latest": ".bookops/canon-latest.json",
    },
    "gates": {
        "fail_on_unresolved_severity": ["critical"],
        "allow_waivers_for": ["high", "medium", "low"],
    },
}


DEFAULT_RULES = {
    "version": 1,
    "policy": {
        "precedence": {"manuscript_over_lore": True},
        "gate": {
            "fail_on_unresolved_severity": ["critical"],
            "allow_waivers_for": ["high", "medium", "low"],
            "strict_mode_promotes": {"warning_to_fail": True},
        },
    },
    "rules": [
        {
            "id": "HARD.POV.LOCK",
            "kind": "hard",
            "severity": "critical",
            "scope": "chapter",
            "detector": "pov_lock",
            "params": {"allowed_pov": ["close_third_harry"], "max_violations": 0},
            "message": "POV lock violated.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "HARD.TENSE.CONSISTENCY",
            "kind": "hard",
            "severity": "high",
            "scope": "chapter",
            "detector": "tense_consistency",
            "params": {"primary_tense": "past", "max_violations": 2},
            "message": "Narrative tense drift exceeds threshold.",
            "gate_behavior": "fail",
            "waiver_allowed": True,
        },
        {
            "id": "HARD.TIMELINE.ANCHORS",
            "kind": "hard",
            "severity": "critical",
            "scope": "project",
            "detector": "timeline_anchor_check",
            "params": {"require_canonical_match": True},
            "message": "Absolute timeline anchor contradiction detected.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "HARD.TIMELINE.DAY_SEQUENCE",
            "kind": "hard",
            "severity": "high",
            "scope": "project",
            "detector": "chapter_day_sequence",
            "params": {"max_out_of_order_events": 0},
            "message": "Chapter day sequence is incoherent.",
            "gate_behavior": "fail",
            "waiver_allowed": True,
        },
        {
            "id": "HARD.STATE.OBJECT_TRANSITIONS",
            "kind": "hard",
            "severity": "critical",
            "scope": "project",
            "detector": "object_state_tracker",
            "params": {
                "tracked_objects": ["blessed_round", "webley", "key_mobius", "dead_mans_switch"],
                "allow_impossible_transitions": False,
            },
            "message": "Impossible state transition detected for tracked object.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "HARD.CHARACTER.INVARIANTS",
            "kind": "hard",
            "severity": "critical",
            "scope": "chapter",
            "detector": "character_invariants",
            "params": {"invariants": ["harry_no_digital_usage", "olive_has_scene_agency"]},
            "message": "Character invariant violation.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "HARD.PRECEDENCE.STORY_OVER_LORE",
            "kind": "hard",
            "severity": "critical",
            "scope": "lore_sync",
            "detector": "precedence_enforcer",
            "params": {"manuscript_over_lore": True},
            "message": "Lore patch attempts to override manuscript truth.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "HARD.ENTITY.IDENTITY",
            "kind": "hard",
            "severity": "high",
            "scope": "project",
            "detector": "entity_identity_check",
            "params": {"disallow_alias_collision": True, "disallow_role_conflicts": True},
            "message": "Entity identity/role conflict detected.",
            "gate_behavior": "fail",
            "waiver_allowed": True,
        },
        {
            "id": "HARD.CAUSAL.PRECONDITIONS",
            "kind": "hard",
            "severity": "high",
            "scope": "chapter",
            "detector": "causal_preconditions",
            "params": {"require_declared_preconditions": True},
            "message": "Event appears without required preconditions.",
            "gate_behavior": "fail",
            "waiver_allowed": True,
        },
        {
            "id": "HARD.ISSUE.CRITICAL_OPEN",
            "kind": "hard",
            "severity": "critical",
            "scope": "gate",
            "detector": "open_issue_guard",
            "params": {"block_if_open_severity_at_or_above": "critical"},
            "message": "Unresolved critical issues remain.",
            "gate_behavior": "fail",
            "waiver_allowed": False,
        },
        {
            "id": "SOFT.REPETITION.PHRASE_FAMILY",
            "kind": "soft",
            "severity": "medium",
            "scope": "chapter",
            "detector": "phrase_family_density",
            "params": {
                "families": ["not_yet", "the_way_construction", "warm_warmth"],
                "warn_threshold": 6,
                "high_threshold": 10,
            },
            "message": "Phrase-family repetition exceeds target.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.REPETITION.NEAR_VERBATIM",
            "kind": "soft",
            "severity": "high",
            "scope": "project",
            "detector": "near_verbatim_repeat",
            "params": {"similarity_threshold": 0.9, "min_tokens": 10},
            "message": "Near-verbatim repeat detected across chapters.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.MOTIF.DENSITY_BALANCE",
            "kind": "soft",
            "severity": "medium",
            "scope": "project",
            "detector": "motif_density",
            "params": {
                "motifs": {"copper": {"warn_per_chapter": 8}, "chrome": {"warn_per_chapter": 8}, "orchids": {"warn_per_chapter": 7}},
                "cluster_window_chapters": 3,
            },
            "message": "Motif density/cluster imbalance detected.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.STYLE.STRUCTURE_OVERUSE",
            "kind": "soft",
            "severity": "medium",
            "scope": "chapter",
            "detector": "structure_overuse",
            "params": {"patterns": ["not_x_not_y_z", "single_sentence_paragraph"], "warn_threshold": 8},
            "message": "Repeated structural pattern overuse.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.CHARACTER.TAG_STACKING",
            "kind": "soft",
            "severity": "low",
            "scope": "chapter",
            "detector": "descriptor_stack",
            "params": {"stacks": {"olive": ["gray_green_eyes", "paint_on_hands", "galaxies"]}, "max_stack_occurrences": 1},
            "message": "Character descriptor stack overused.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.DIALOGUE.VOICE_DRIFT",
            "kind": "soft",
            "severity": "medium",
            "scope": "chapter",
            "detector": "dialogue_voice_profile",
            "params": {"drift_threshold": 0.35, "min_lines_for_eval": 8},
            "message": "Dialogue voice drift risk detected.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.CHARACTER.AGENCY_DRIFT",
            "kind": "soft",
            "severity": "high",
            "scope": "chapter",
            "detector": "agency_heuristic",
            "params": {"target_characters": ["olive"], "max_passive_key_beats": 1},
            "message": "Character agency appears weaker than target.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.EXPOSITION.LOAD",
            "kind": "soft",
            "severity": "medium",
            "scope": "chapter",
            "detector": "exposition_action_ratio",
            "params": {"warn_ratio": 1.8, "high_ratio": 2.5, "min_window_paragraphs": 6},
            "message": "Exposition-heavy section detected.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.SENSORY.SATURATION",
            "kind": "soft",
            "severity": "low",
            "scope": "chapter",
            "detector": "sensory_density",
            "params": {"warn_threshold_per_paragraph": 5, "max_consecutive_saturated_paragraphs": 3},
            "message": "Sensory detail saturation may affect clarity/pacing.",
            "gate_behavior": "warn",
            "waiver_allowed": True,
        },
        {
            "id": "SOFT.ALERT.DEDUP",
            "kind": "soft",
            "severity": "low",
            "scope": "report",
            "detector": "alert_deduplication",
            "params": {"dedupe_by_root_cause": True, "max_low_priority_items_after_dedupe": 25},
            "message": "Alert volume deduplicated for report usability.",
            "gate_behavior": "info",
            "waiver_allowed": True,
        },
    ],
}


@dataclass
class RuntimeConfig:
    project_root: Path
    config_path: Path
    output_dir: Path
    bookops_dir: Path
    index_dir: Path
    semantic_index_dir: Path
    snapshots_dir: Path
    issues_file: Path
    run_history_file: Path
    canon_latest: Path
    chapters_dir: Path
    lore_dir: Path
    guides: list[Path]
    rules_path: Path
    entities_path: Path
    timeline_path: Path


def bootstrap(project_root: Path, template: str | None = None) -> None:
    config_path = project_root / ".bookops" / "config.yaml"
    rules_path = project_root / "canon" / "rules.yaml"
    entities_path = project_root / "canon" / "entities.yaml"
    timeline_path = project_root / "canon" / "timeline.yaml"

    ensure_dir(config_path.parent)
    ensure_dir(rules_path.parent)
    ensure_dir((project_root / "reports"))

    if not config_path.exists():
        dump_yaml(config_path, DEFAULT_CONFIG)
    if not rules_path.exists():
        rules_payload = apply_template_to_rules(DEFAULT_RULES, template)
        dump_yaml(rules_path, rules_payload)
    if not entities_path.exists():
        dump_yaml(entities_path, {"version": 1, "entities": []})
    if not timeline_path.exists():
        dump_yaml(timeline_path, {"version": 1, "anchors": [], "chapter_days": {}})


def load_runtime_config(project_root: Path, config_path: Path | None = None, output_dir: Path | None = None) -> RuntimeConfig:
    if config_path is None:
        config_path = project_root / ".bookops" / "config.yaml"
    if not config_path.exists():
        bootstrap(project_root)
    data = load_yaml(config_path, default=DEFAULT_CONFIG) or DEFAULT_CONFIG

    paths = data.get("paths", {})
    proj = data.get("project", {})

    bookops_dir = project_root / paths.get("bookops_dir", ".bookops")
    index_dir = project_root / paths.get("index_dir", ".bookops/index")
    semantic_index_dir = project_root / paths.get("semantic_index_dir", ".book_index")
    snapshots_dir = project_root / paths.get("snapshots_dir", ".bookops/snapshots")
    issues_file = project_root / paths.get("issues_file", ".bookops/issues.json")
    run_history_file = project_root / paths.get("run_history_file", ".bookops/runs.json")
    canon_latest = project_root / paths.get("canon_latest", ".bookops/canon-latest.json")
    out = output_dir or (project_root / "reports")

    guides = [project_root / p for p in proj.get("guides", [])]

    return RuntimeConfig(
        project_root=project_root,
        config_path=config_path,
        output_dir=out,
        bookops_dir=bookops_dir,
        index_dir=index_dir,
        semantic_index_dir=semantic_index_dir,
        snapshots_dir=snapshots_dir,
        issues_file=issues_file,
        run_history_file=run_history_file,
        canon_latest=canon_latest,
        chapters_dir=project_root / proj.get("chapters_dir", "chapters"),
        lore_dir=project_root / proj.get("lore_dir", "lore"),
        guides=guides,
        rules_path=project_root / "canon" / "rules.yaml",
        entities_path=project_root / "canon" / "entities.yaml",
        timeline_path=project_root / "canon" / "timeline.yaml",
    )


def load_rules(path: Path) -> dict[str, Any]:
    rules = load_yaml(path, default=DEFAULT_RULES)
    if not rules:
        rules = DEFAULT_RULES
    return rules
