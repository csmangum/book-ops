from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .utils import dump_json, load_json, sha256_file, utc_now_iso


INDEX_VERSION = 2
DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "venv",
    ".bookops",
    "reports",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
}


def _is_excluded(path: Path, project_root: Path, excluded_dirs: set[str]) -> bool:
    rel = path.relative_to(project_root)
    return any(part in excluded_dirs for part in rel.parts)


def _collect_markdown_files(project_root: Path, excluded_dirs: set[str]) -> list[Path]:
    candidates = []
    for path in project_root.rglob("*.md"):
        if _is_excluded(path, project_root=project_root, excluded_dirs=excluded_dirs):
            continue
        candidates.append(path)
    return sorted(candidates, key=lambda p: str(p.relative_to(project_root)))


def _stable_corpus_hash(items: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for item in items:
        digest.update(item["path"].encode("utf-8"))
        digest.update(item["sha256"].encode("utf-8"))
    return digest.hexdigest()


def rebuild_index(
    project_root: Path,
    index_dir: Path,
    excluded_dirs: set[str] | None = None,
) -> dict[str, Any]:
    excludes = excluded_dirs or DEFAULT_EXCLUDED_DIRS
    files = _collect_markdown_files(project_root, excludes)
    symbolic = []
    for path in files:
        rel = str(path.relative_to(project_root))
        content = path.read_text(encoding="utf-8")
        symbolic.append(
            {
                "path": rel,
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
                "line_count": len(content.splitlines()),
                "modified_at": path.stat().st_mtime,
            }
        )
    corpus_hash = _stable_corpus_hash(symbolic)
    payload = {
        "index_version": INDEX_VERSION,
        "generated_at": utc_now_iso(),
        "project_root": str(project_root),
        "file_count": len(symbolic),
        "excluded_dirs": sorted(excludes),
        "corpus_hash": corpus_hash,
        "symbolic": symbolic,
    }
    dump_json(index_dir / "symbolic.json", payload)
    # semantic index is a stub for v1
    dump_json(
        index_dir / "semantic.json",
        {
            "index_version": INDEX_VERSION,
            "generated_at": payload["generated_at"],
            "status": "stub",
            "source_file_count": payload["file_count"],
            "corpus_hash": corpus_hash,
        },
    )
    return payload


def index_status(index_dir: Path) -> dict[str, Any]:
    symbolic = index_dir / "symbolic.json"
    semantic = index_dir / "semantic.json"
    payload: dict[str, Any] = {
        "symbolic_exists": symbolic.exists(),
        "semantic_exists": semantic.exists(),
        "symbolic_path": str(symbolic),
        "semantic_path": str(semantic),
    }
    if symbolic.exists():
        symbolic_data = load_json(symbolic, default={}) or {}
        payload.update(
            {
                "index_version": symbolic_data.get("index_version"),
                "generated_at": symbolic_data.get("generated_at"),
                "file_count": symbolic_data.get("file_count", 0),
                "corpus_hash": symbolic_data.get("corpus_hash", ""),
                "symbolic": symbolic_data.get("symbolic", []),
            }
        )
    if semantic.exists():
        semantic_data = load_json(semantic, default={}) or {}
        payload.update(
            {
                "semantic_status": semantic_data.get("status", "unknown"),
                "semantic_source_file_count": semantic_data.get("source_file_count", 0),
            }
        )
    return payload
