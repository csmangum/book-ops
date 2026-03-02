from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def dump_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def dump_yaml(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def load_yaml(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def iter_markdown_files(root: Path) -> list[Path]:
    return sorted(
        [p for p in root.rglob("*.md") if ".git" not in p.parts],
        key=lambda p: str(p),
    )


def chapter_number_from_name(filename: str) -> int:
    name = os.path.basename(filename)
    prefix = name.split("_", 1)[0]
    if prefix.isdigit():
        return int(prefix)
    return 10_000


def sorted_chapter_paths(chapter_dir: Path) -> list[Path]:
    return sorted(chapter_dir.glob("*.md"), key=lambda p: chapter_number_from_name(p.name))
