from __future__ import annotations

from copy import deepcopy
from typing import Any


TEMPLATE_RULE_PATCHES: dict[str, dict[str, Any]] = {
    "noir": {
        "soft_overrides": {
            "SOFT.MOTIF.DENSITY_BALANCE": {
                "params": {
                    "motifs": {
                        "copper": {"warn_per_chapter": 10},
                        "chrome": {"warn_per_chapter": 9},
                        "orchids": {"warn_per_chapter": 8},
                    }
                }
            }
        }
    },
    "epic_fantasy": {
        "soft_overrides": {
            "SOFT.EXPOSITION.LOAD": {"params": {"warn_ratio": 2.3, "high_ratio": 3.1}},
            "SOFT.MOTIF.DENSITY_BALANCE": {
                "params": {
                    "motifs": {
                        "copper": {"warn_per_chapter": 5},
                        "chrome": {"warn_per_chapter": 5},
                        "orchids": {"warn_per_chapter": 5},
                    }
                }
            },
        }
    },
    "thriller": {
        "soft_overrides": {
            "SOFT.STYLE.STRUCTURE_OVERUSE": {"params": {"warn_threshold": 6}},
            "SOFT.EXPOSITION.LOAD": {"params": {"warn_ratio": 1.5, "high_ratio": 2.0}},
        }
    },
}


def list_templates() -> list[str]:
    return sorted(TEMPLATE_RULE_PATCHES.keys())


def apply_template_to_rules(rules_payload: dict[str, Any], template: str | None) -> dict[str, Any]:
    if not template:
        return rules_payload
    if template not in TEMPLATE_RULE_PATCHES:
        import sys
        print(f"Warning: unknown template '{template}'. Available templates: {', '.join(list_templates())}", file=sys.stderr)
        return rules_payload

    updated = deepcopy(rules_payload)
    patch = TEMPLATE_RULE_PATCHES[template]
    overrides = patch.get("soft_overrides", {})
    by_id = {rule.get("id"): rule for rule in updated.get("rules", [])}
    for rule_id, update in overrides.items():
        rule = by_id.get(rule_id)
        if not rule:
            continue
        _merge_in_place(rule, update)
    return updated


def _merge_in_place(target: dict[str, Any], patch: dict[str, Any]) -> None:
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(target.get(key), dict):
            _merge_in_place(target[key], value)
        else:
            target[key] = value
