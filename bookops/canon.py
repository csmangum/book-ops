from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .config import RuntimeConfig
from .ingest import extract_time_markers, load_chapters, load_lore
from .utils import dump_json, load_json, utc_now_iso


def build_canon(config: RuntimeConfig) -> dict[str, Any]:
    chapters = load_chapters(config.chapters_dir)
    lore_docs = load_lore(config.lore_dir)

    chapter_index = []
    timeline = {"chapter_days": {}, "dates": [], "times": []}
    entities: list[dict[str, Any]] = []

    for c in chapters:
        markers = extract_time_markers(c.lines)
        chapter_index.append(
            {
                "chapter_number": c.chapter_number,
                "path": str(c.path.relative_to(config.project_root)),
                "title": c.title,
                "markers": markers,
            }
        )
        if markers["day"]:
            first_day = markers["day"][0][1]
            day_num = re.sub(r"[^0-9]", "", first_day)
            if day_num:
                timeline["chapter_days"][str(c.chapter_number)] = int(day_num)
        timeline["dates"].extend(
            [{"chapter": c.chapter_number, "line": ln, "value": val} for ln, val in markers["date"]]
        )
        timeline["times"].extend(
            [{"chapter": c.chapter_number, "line": ln, "value": val} for ln, val in markers["time"]]
        )

    for lore in lore_docs:
        entities.append(
            {
                "id": f"lore::{lore.name.lower().replace(' ', '_')}",
                "type": "lore_entry",
                "name": lore.name,
                "path": str(lore.path.relative_to(config.project_root)),
            }
        )

    return {
        "version": 1,
        "generated_at": utc_now_iso(),
        "chapter_index": chapter_index,
        "timeline": timeline,
        "entities": entities,
    }


def save_canon_snapshot(config: RuntimeConfig, canon_payload: dict[str, Any]) -> Path:
    snapshot_name = f"canon-{canon_payload['generated_at'].replace(':', '-').replace('+00-00', 'Z')}.json"
    snapshot_path = config.snapshots_dir / snapshot_name
    dump_json(snapshot_path, canon_payload)
    dump_json(config.canon_latest, canon_payload)
    return snapshot_path


def validate_canon_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if "chapter_index" not in payload:
        errors.append("Missing chapter_index")
    if "timeline" not in payload:
        errors.append("Missing timeline")
    else:
        if "chapter_days" not in payload["timeline"]:
            errors.append("Missing timeline.chapter_days")
    if "entities" not in payload:
        errors.append("Missing entities")
    return errors


def load_snapshot(path: Path) -> dict[str, Any]:
    data = load_json(path, default={})
    if not isinstance(data, dict):
        return {}
    return data


def diff_canon(from_payload: dict[str, Any], to_payload: dict[str, Any]) -> dict[str, Any]:
    from_days = from_payload.get("timeline", {}).get("chapter_days", {})
    to_days = to_payload.get("timeline", {}).get("chapter_days", {})

    changed_days = {}
    all_keys = sorted(set(from_days.keys()) | set(to_days.keys()), key=lambda x: int(x) if x.isdigit() else 99999)
    for key in all_keys:
        if from_days.get(key) != to_days.get(key):
            changed_days[key] = {"from": from_days.get(key), "to": to_days.get(key)}

    from_entities = {e.get("id"): e for e in from_payload.get("entities", [])}
    to_entities = {e.get("id"): e for e in to_payload.get("entities", [])}
    added = sorted([k for k in to_entities if k not in from_entities])
    removed = sorted([k for k in from_entities if k not in to_entities])

    return {
        "changed_days": changed_days,
        "entities_added": added,
        "entities_removed": removed,
    }
