"""
Multi-level manuscript parser.

Splits the novel into a hierarchy: acts > chapters > scenes > paragraphs > sentences.
Each unit carries metadata about its position in the hierarchy.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import nltk

from .book_config import get_act_map

CHAPTER_DIR = Path(__file__).resolve().parent.parent / "chapters"

ACT_CHAPTER_RANGES: dict[str, tuple[int, int]] = {
    "Prologue": (0, 0),
    "Act I – The Hire": (1, 6),
    "Act II – The Descent": (7, 18),
    "Act III – The Gate": (19, 24),
    "Epilogue": (25, 25),
}

ACT_MAP: dict[int, str] = {
    ch: act for act, (start, end) in ACT_CHAPTER_RANGES.items() for ch in range(start, end + 1)
}


@dataclass
class TextUnit:
    """A piece of text at any level of the hierarchy."""

    level: str  # "sentence", "paragraph", "scene", "chapter", "act"
    text: str
    chapter_num: int
    chapter_title: str
    act: str
    scene_idx: int = 0  # 0-based within chapter
    paragraph_idx: int = 0  # 0-based within scene
    sentence_idx: int = 0  # 0-based within paragraph
    char_offset: int = 0
    source_file: str = ""

    @property
    def id(self) -> str:
        if self.level == "act":
            return f"act_{self.act.lower().replace(' ', '_').replace('–', '')}"
        parts = [f"ch{self.chapter_num}"]
        if self.level in ("scene", "paragraph", "sentence"):
            parts.append(f"sc{self.scene_idx}")
        if self.level in ("paragraph", "sentence"):
            parts.append(f"p{self.paragraph_idx}")
        if self.level == "sentence":
            parts.append(f"s{self.sentence_idx}")
        return "_".join(parts)

    @property
    def metadata(self) -> dict:
        return {
            "level": self.level,
            "act": self.act,
            "chapter_num": self.chapter_num,
            "chapter_title": self.chapter_title,
            "scene_idx": self.scene_idx,
            "paragraph_idx": self.paragraph_idx,
            "sentence_idx": self.sentence_idx,
            "source_file": self.source_file,
            "char_offset": self.char_offset,
        }


def _chapter_title_from_filename(filename: str) -> str:
    """Extract chapter title from filename (e.g. 7_The Egg and the Bullet.md -> The Egg...)."""
    base = filename.replace(".md", "")
    if "_" in base:
        return base.split("_", 1)[-1].strip()
    return base.strip()


def _chapter_number(filename: str) -> int:
    match = re.match(r"(\d+)_", filename)
    if match:
        return int(match.group(1))
    raise ValueError(f"Cannot parse chapter number from {filename}")


def _strip_header(text: str) -> str:
    """Remove the markdown heading and title lines, return body text."""
    lines = text.split("\n")
    body_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and stripped != "---":
            body_start = i
            break
    return "\n".join(lines[body_start:])


def _split_scenes(body: str) -> list[str]:
    """Split chapter body on scene-break markers (---, ***, ___)."""
    parts = re.split(r"\n\s*(?:---|\*\*\*|___)\s*\n", body)
    return [p.strip() for p in parts if p.strip()]


def _split_paragraphs(scene_text: str) -> list[str]:
    """Split on double newlines (standard paragraph breaks)."""
    parts = re.split(r"\n\s*\n", scene_text)
    return [p.strip() for p in parts if p.strip()]


def _ensure_nltk_punkt() -> None:
    """Ensure the NLTK sentence tokenizer data is available.

    Raises RuntimeError if data is missing, directing users to run
    'python -m indexer setup' or set INDEXER_AUTO_DOWNLOAD=1 to allow
    automatic downloads.
    """
    import os

    try:
        nltk.sent_tokenize("Test.")
    except LookupError:
        if os.environ.get("INDEXER_AUTO_DOWNLOAD", "").strip() == "1":
            nltk.download("punkt", quiet=True)
            nltk.download("punkt_tab", quiet=True)
        else:
            raise RuntimeError(
                "NLTK sentence tokenizer data is missing. "
                "Run 'python -m indexer setup' to download it, "
                "or set INDEXER_AUTO_DOWNLOAD=1 to allow automatic downloads."
            )


# Sentences matching this pattern are markdown artifacts (e.g. italic markers)
# and should not be indexed as standalone units.
_DEGENERATE_SENTENCE_RE = re.compile(r'^\s*["\']?\*["\']?\s*$')


def _split_sentences(paragraph_text: str) -> list[str]:
    """Tokenize into sentences using NLTK. Filters out markdown artifacts."""
    clean = re.sub(r"\s+", " ", paragraph_text).strip()
    if not clean:
        return []
    _ensure_nltk_punkt()
    raw = nltk.sent_tokenize(clean)
    return [s for s in raw if not _DEGENERATE_SENTENCE_RE.match(s)]


def parse_chapter(
    filepath: Path,
    act_map: dict[int, str] | None = None,
    act_ranges: dict[str, tuple[int, int]] | None = None,
) -> list[TextUnit]:
    """Parse a single chapter file into TextUnits at all levels."""
    text = filepath.read_text(encoding="utf-8")
    filename = filepath.name
    chapter_num = _chapter_number(filename)
    act_map = act_map or ACT_MAP
    act = act_map.get(chapter_num, "Full Book")

    chapter_title = _chapter_title_from_filename(filename)

    body = _strip_header(text)
    units: list[TextUnit] = []

    scenes = _split_scenes(body)

    for scene_idx, scene_text in enumerate(scenes):
        paragraphs = _split_paragraphs(scene_text)

        for para_idx, para_text in enumerate(paragraphs):
            sentences = _split_sentences(para_text)

            for sent_idx, sent in enumerate(sentences):
                units.append(TextUnit(
                    level="sentence",
                    text=sent,
                    chapter_num=chapter_num,
                    chapter_title=chapter_title,
                    act=act,
                    scene_idx=scene_idx,
                    paragraph_idx=para_idx,
                    sentence_idx=sent_idx,
                    source_file=filename,
                ))

            units.append(TextUnit(
                level="paragraph",
                text=para_text,
                chapter_num=chapter_num,
                chapter_title=chapter_title,
                act=act,
                scene_idx=scene_idx,
                paragraph_idx=para_idx,
                source_file=filename,
            ))

        units.append(TextUnit(
            level="scene",
            text=scene_text,
            chapter_num=chapter_num,
            chapter_title=chapter_title,
            act=act,
            scene_idx=scene_idx,
            source_file=filename,
        ))

    units.append(TextUnit(
        level="chapter",
        text=body,
        chapter_num=chapter_num,
        chapter_title=chapter_title,
        act=act,
        source_file=filename,
    ))

    return units


def parse_all_chapters(
    chapters_dir: Path | None = None,
    book_id: str | None = None,
) -> list[TextUnit]:
    """Parse every chapter in the chapters/ directory."""
    dir_path = chapters_dir if chapters_dir is not None else CHAPTER_DIR
    if not dir_path.exists():
        raise FileNotFoundError(f"Chapters directory not found: {dir_path}")
    files = sorted(dir_path.glob("*.md"), key=lambda f: _chapter_number(f.name))
    if not files:
        raise FileNotFoundError(f"No .md files found in {dir_path}")

    act_map = get_act_map(book_id) if book_id else None
    if act_map and not act_map:
        act_map = None  # Unknown book_id, fall back to default ACT_MAP

    all_units: list[TextUnit] = []
    for f in files:
        all_units.extend(parse_chapter(f, act_map=act_map))
    return all_units


def build_act_units(
    chapter_units: list[TextUnit],
    act_ranges: dict[str, tuple[int, int]] | None = None,
) -> list[TextUnit]:
    """Build act-level units by concatenating chapter texts."""
    act_ranges = act_ranges or ACT_CHAPTER_RANGES
    act_texts: dict[str, list[str]] = {}
    act_meta: dict[str, tuple[int, str]] = {}

    for u in chapter_units:
        if u.level == "chapter":
            act_texts.setdefault(u.act, []).append(u.text)
            if u.act not in act_meta:
                act_meta[u.act] = (u.chapter_num, u.source_file)

    units = []
    for act_name, texts in act_texts.items():
        combined = "\n\n".join(texts)
        first_ch, first_file = act_meta[act_name]
        start_ch, end_ch = act_ranges.get(act_name, (first_ch, first_ch))
        units.append(TextUnit(
            level="act",
            text=combined,
            chapter_num=start_ch,
            chapter_title=f"Chapters {start_ch}–{end_ch}",
            act=act_name,
            source_file=first_file,
        ))
    return units
