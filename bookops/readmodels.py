from __future__ import annotations

from pathlib import Path
from typing import Any

from .canon import build_canon, load_snapshot
from .config import RuntimeConfig
from .ingest import load_chapters
from .runlog import get_run_entry, load_run_history
from .utils import dump_yaml, load_yaml


def list_runs(config: RuntimeConfig) -> list[dict[str, Any]]:
    return load_run_history(config.run_history_file)


def get_run(config: RuntimeConfig, run_id: str) -> dict[str, Any] | None:
    return get_run_entry(config.run_history_file, run_id)


def get_chapter_content(config: RuntimeConfig, chapter_id: int) -> dict[str, Any]:
    chapters = load_chapters(config.chapters_dir)
    chapter = next((c for c in chapters if c.chapter_number == chapter_id), None)
    if not chapter:
        raise ValueError(f"Chapter {chapter_id} not found")
    return {
        "chapter_id": chapter_id,
        "path": str(chapter.path.relative_to(config.project_root)),
        "title": chapter.title,
        "content": chapter.text,
        "line_count": len(chapter.lines),
    }


def get_canon_graph(config: RuntimeConfig) -> dict[str, Any]:
    payload: dict[str, Any]
    if config.canon_latest.exists():
        payload = load_snapshot(config.canon_latest)
    else:
        payload = build_canon(config)
    entities = payload.get("entities", [])
    nodes = [
        {
            "id": str(entity.get("id", f"entity-{idx}")),
            "label": str(entity.get("name", entity.get("id", f"Entity {idx}"))),
            "type": str(entity.get("type", "entity")),
            "path": entity.get("path"),
        }
        for idx, entity in enumerate(entities, start=1)
    ]
    # Relationship extraction is not yet modeled in canon payload.
    edges: list[dict[str, Any]] = []
    return {
        "generated_at": payload.get("generated_at"),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }


def get_rules_payload(config: RuntimeConfig) -> dict[str, Any]:
    payload = load_yaml(config.rules_path, default={}) or {}
    return payload if isinstance(payload, dict) else {}


def get_settings_payload(config: RuntimeConfig) -> dict[str, Any]:
    payload = load_yaml(config.config_path, default={}) or {}
    return payload if isinstance(payload, dict) else {}


def patch_settings_payload(config: RuntimeConfig, patch: dict[str, Any]) -> dict[str, Any]:
    current = get_settings_payload(config)
    merged = _deep_merge(current, patch)
    dump_yaml(config.config_path, merged)
    return merged


def _deep_merge(current: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    output = dict(current)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(output.get(key), dict):
            output[key] = _deep_merge(output[key], value)
        else:
            output[key] = value
    return output
