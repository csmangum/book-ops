"""Unit tests for bookops.ingest."""
import tempfile
import unittest
from pathlib import Path

from bookops.ingest import (
    chapter_title_from_lines,
    extract_dialogue_lines,
    extract_time_markers,
    load_chapters,
    load_lore,
)


class TestChapterTitleFromLines(unittest.TestCase):
    def test_returns_first_non_header_line(self) -> None:
        lines = ["# Chapter 1", "", "The Beginning", "More text"]
        self.assertEqual(chapter_title_from_lines(lines, "fallback"), "The Beginning")

    def test_returns_fallback_when_empty(self) -> None:
        self.assertEqual(chapter_title_from_lines([], "fallback"), "fallback")

    def test_skips_header_lines(self) -> None:
        lines = ["# Header", "## Sub", "First real line"]
        self.assertEqual(chapter_title_from_lines(lines, "fallback"), "First real line")


class TestExtractTimeMarkers(unittest.TestCase):
    def test_day_markers(self) -> None:
        lines = ["It was Day 5 when it happened.", "Day 10 came next."]
        markers = extract_time_markers(lines)
        self.assertEqual(len(markers["day"]), 2)
        self.assertEqual(markers["day"][0], (1, "Day 5"))
        self.assertEqual(markers["day"][1], (2, "Day 10"))

    def test_date_markers(self) -> None:
        lines = ["March 15, 2024 was the day."]
        markers = extract_time_markers(lines)
        self.assertEqual(len(markers["date"]), 1)
        self.assertIn("March", markers["date"][0][1])

    def test_empty_lines(self) -> None:
        markers = extract_time_markers([])
        self.assertEqual(markers["day"], [])
        self.assertEqual(markers["date"], [])
        self.assertEqual(markers["time"], [])


class TestExtractDialogueLines(unittest.TestCase):
    def test_extracts_quoted_lines(self) -> None:
        lines = ['"Hello," he said.', "Not dialogue", '"Goodbye."']
        result = extract_dialogue_lines(lines)
        self.assertIn('"Hello," he said.', result)
        self.assertIn('"Goodbye."', result)


class TestLoadChapters(unittest.TestCase):
    def test_loads_chapters_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "3_Three.md").write_text("# Three\n\nContent")
            (root / "1_One.md").write_text("# One\n\nContent")
            docs = load_chapters(root)
            self.assertEqual(len(docs), 2)
            self.assertEqual(docs[0].chapter_number, 1)
            self.assertEqual(docs[1].chapter_number, 3)


class TestLoadLore(unittest.TestCase):
    def test_loads_lore_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Harry.md").write_text("# Harry\n\nWizard.")
            (root / "Hermione.md").write_text("# Hermione\n\nStudent.")
            docs = load_lore(root)
            self.assertEqual(len(docs), 2)
            names = [d.name for d in docs]
            self.assertIn("Harry", names)
            self.assertIn("Hermione", names)

    def test_returns_empty_for_missing_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_lore(Path(tmp) / "nonexistent")
            self.assertEqual(result, [])
