"""
Book-specific configuration: act mapping and chapter ranges.

Supports multiple books via a registry. The indexer uses this to resolve
act names for each chapter.
"""

from __future__ import annotations

from pathlib import Path

# Default chapters dir (for The Last Pure Thing)
CHAPTER_DIR = Path(__file__).resolve().parent.parent / "chapters"

# Book ID -> act chapter ranges
# Format: { "act_name": (start_chapter, end_chapter) } inclusive
BOOK_ACT_RANGES: dict[str, dict[str, tuple[int, int]]] = {
    "last_pure_thing": {
        "Prologue": (0, 0),
        "Act I – The Hire": (1, 6),
        "Act II – The Descent": (7, 18),
        "Act III – The Gate": (19, 24),
        "Epilogue": (25, 25),
    },
    "alice": {
        "Full Book": (1, 12),
    },
    "alice_three_acts": {
        "Act I": (1, 4),
        "Act II": (5, 8),
        "Act III": (9, 12),
    },
}


def get_act_map(book_id: str) -> dict[int, str]:
    """Build chapter_num -> act_name mapping for a book."""
    ranges = BOOK_ACT_RANGES.get(book_id)
    if not ranges:
        return {}
    result: dict[int, str] = {}
    for act_name, (start, end) in ranges.items():
        for ch in range(start, end + 1):
            result[ch] = act_name
    return result


def get_act_chapter_ranges(book_id: str) -> dict[str, tuple[int, int]]:
    """Get act ranges for a book."""
    return BOOK_ACT_RANGES.get(book_id, {})
