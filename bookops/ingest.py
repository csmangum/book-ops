from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .utils import chapter_number_from_name, read_text, sorted_chapter_paths


@dataclass
class ChapterDoc:
    path: Path
    chapter_number: int
    title: str
    lines: list[str]
    text: str


@dataclass
class LoreDoc:
    path: Path
    name: str
    lines: list[str]
    text: str


def chapter_title_from_lines(lines: list[str], fallback: str) -> str:
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return fallback


def load_chapters(chapters_dir: Path) -> list[ChapterDoc]:
    docs: list[ChapterDoc] = []
    for path in sorted_chapter_paths(chapters_dir):
        text = read_text(path)
        lines = text.splitlines()
        docs.append(
            ChapterDoc(
                path=path,
                chapter_number=chapter_number_from_name(path.name),
                title=chapter_title_from_lines(lines, fallback=path.stem),
                lines=lines,
                text=text,
            )
        )
    return docs


def load_lore(lore_dir: Path) -> list[LoreDoc]:
    docs: list[LoreDoc] = []
    if not lore_dir.exists():
        return docs
    for path in sorted(lore_dir.glob("*.md"), key=lambda p: p.name):
        text = read_text(path)
        lines = text.splitlines()
        docs.append(LoreDoc(path=path, name=path.stem, lines=lines, text=text))
    return docs


DAY_RE = re.compile(r"\bDay\s+(\d+)\b", re.IGNORECASE)
ABS_DATE_RE = re.compile(r"\b(March|September)\s+\d{1,2},\s+20\d{2}\b", re.IGNORECASE)
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:a\.m\.|p\.m\.|AM|PM|PDT|UTC)?(?=\W|$)")


def extract_time_markers(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    markers: dict[str, list[tuple[int, str]]] = {"day": [], "date": [], "time": []}
    for idx, line in enumerate(lines, start=1):
        for day in DAY_RE.finditer(line):
            markers["day"].append((idx, day.group(0)))
        for date in ABS_DATE_RE.finditer(line):
            markers["date"].append((idx, date.group(0)))
        for time in TIME_RE.finditer(line):
            markers["time"].append((idx, time.group(0)))
    return markers


def extract_dialogue_lines(lines: list[str]) -> list[str]:
    result: list[str] = []
    for line in lines:
        stripped = line.strip()
        if '"' in stripped or "“" in stripped or "”" in stripped:
            result.append(stripped)
    return result
