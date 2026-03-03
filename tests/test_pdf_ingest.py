"""Unit tests for bookops.pdf_ingest."""

import tempfile
import unittest
from pathlib import Path

from bookops.pdf_ingest import (
    _clean_text,
    _fix_hyphenation,
    _parse_alice_toc,
    _strip_page_headers,
    detect_chapters_from_pdf,
    extract_text_from_pdf,
    ingest_pdf_to_chapters,
)


class TestCleanText(unittest.TestCase):
    def test_fixes_ligatures(self) -> None:
        self.assertEqual(_clean_text("ﬁsh"), "fish")
        self.assertEqual(_clean_text("ﬂower"), "flower")
        self.assertEqual(_clean_text("oﬃce"), "office")

    def test_preserves_plain_text(self) -> None:
        self.assertEqual(_clean_text("Hello world"), "Hello world")


class TestFixHyphenation(unittest.TestCase):
    def test_rejoins_hyphenated_words(self) -> None:
        self.assertEqual(_fix_hyphenation("some-\nthing"), "something")
        self.assertEqual(_fix_hyphenation("well-\n  known"), "wellknown")

    def test_preserves_normal_hyphens(self) -> None:
        self.assertEqual(_fix_hyphenation("twenty-one"), "twenty-one")


class TestStripPageHeaders(unittest.TestCase):
    def test_removes_standalone_page_numbers(self) -> None:
        text = "14\nContent here.\n15\nMore content."
        result = _strip_page_headers(text)
        self.assertNotIn("\n14\n", result)
        self.assertIn("Content here", result)

    def test_removes_chapter_running_headers(self) -> None:
        text = "14 CHAPTER 1. DOWN THE RABBIT-HOLE\nAlice was beginning"
        result = _strip_page_headers(text)
        self.assertNotIn("CHAPTER 1", result)
        self.assertIn("Alice", result)


class TestParseAliceToc(unittest.TestCase):
    def test_parses_toc_format(self) -> None:
        toc = "1 Down the Rabbit-Hole 13\n2 The Pool of Tears 19\n7 A Mad Tea-Party 51"
        chapters = _parse_alice_toc(toc)
        self.assertEqual(len(chapters), 3)
        self.assertEqual(chapters[0].number, 1)
        self.assertEqual(chapters[0].title, "Down the Rabbit-Hole")
        self.assertEqual(chapters[0].start_page, 13)
        self.assertEqual(chapters[2].number, 7)
        self.assertEqual(chapters[2].title, "A Mad Tea-Party")
        self.assertEqual(chapters[2].start_page, 51)


class TestDetectChaptersFromPdf(unittest.TestCase):
    def test_detects_alice_chapters(self) -> None:
        pdf_path = Path(__file__).resolve().parent.parent / "carroll-1865.pdf"
        if not pdf_path.exists():
            self.skipTest("carroll-1865.pdf not found")
        chapters = detect_chapters_from_pdf(pdf_path, skip_pages=12, toc_page=11)
        self.assertEqual(len(chapters), 12)
        self.assertEqual(chapters[0].title, "Down the Rabbit-Hole")
        self.assertEqual(chapters[6].title, "A Mad Tea-Party")
        self.assertEqual(chapters[0].start_page, 13)


class TestExtractTextFromPdf(unittest.TestCase):
    def test_extracts_non_empty_text(self) -> None:
        pdf_path = Path(__file__).resolve().parent.parent / "carroll-1865.pdf"
        if not pdf_path.exists():
            self.skipTest("carroll-1865.pdf not found")
        text = extract_text_from_pdf(pdf_path)
        self.assertGreater(len(text), 1000)
        self.assertIn("Alice", text)


class TestIngestPdfToChapters(unittest.TestCase):
    def test_ingest_creates_markdown_files(self) -> None:
        pdf_path = Path(__file__).resolve().parent.parent / "carroll-1865.pdf"
        if not pdf_path.exists():
            self.skipTest("carroll-1865.pdf not found")
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            written = ingest_pdf_to_chapters(pdf_path, out_dir)
            self.assertEqual(len(written), 12)
            for p in written:
                self.assertTrue(p.exists())
                content = p.read_text()
                self.assertIn("# Chapter", content)
                self.assertIn("Alice", content or "")

    def test_raises_when_pdf_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                ingest_pdf_to_chapters(Path(tmp) / "nonexistent.pdf", Path(tmp))
