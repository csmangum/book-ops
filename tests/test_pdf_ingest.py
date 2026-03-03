"""Unit tests for bookops.pdf_ingest."""

import io
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

# Chapters used in the synthetic fixture PDF (number, title, start_page)
_FIXTURE_CHAPTERS = [
    (1, "Down the Rabbit-Hole", 13),
    (2, "The Pool of Tears", 19),
    (3, "A Caucus-Race and a Long Tale", 24),
    (4, "The Rabbit Sends in a Little Bill", 29),
    (5, "Advice from a Caterpillar", 35),
    (6, "Pig and Pepper", 41),
    (7, "A Mad Tea-Party", 51),
    (8, "The Queen's Croquet-Ground", 57),
    (9, "The Mock Turtle's Story", 63),
    (10, "The Lobster Quadrille", 70),
    (11, "Who Stole the Tarts", 76),
    (12, "Alice's Evidence", 82),
]


def _make_alice_fixture_pdf(out_path: Path) -> None:
    """Create a minimal multi-page PDF that mimics Alice in Wonderland structure.

    Produces a TOC on page 11 and chapter content pages starting at page 13,
    matching the structure expected by the ingest pipeline.
    """
    from pypdf import PdfWriter
    from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject

    def _add_text_page(writer: PdfWriter, text_lines: list[str]) -> None:
        content_parts = []
        y = 730
        for line in text_lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content_parts.append(f"BT /F1 10 Tf 50 {y} Td ({safe}) Tj ET")
            y -= 14
            if y < 50:
                break
        content = "\n".join(content_parts)
        page = writer.add_blank_page(width=612, height=792)
        stream = DecodedStreamObject()
        stream.set_data(content.encode("latin-1"))
        font_dict = DictionaryObject({
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        })
        stream_ref = writer._add_object(stream)
        font_ref = writer._add_object(font_dict)
        page[NameObject("/Contents")] = stream_ref
        page[NameObject("/Resources")] = DictionaryObject({
            NameObject("/Font"): DictionaryObject({NameObject("/F1"): font_ref})
        })

    writer = PdfWriter()

    # Pages 1-10: front matter
    for _ in range(10):
        _add_text_page(writer, ["Front matter"])

    # Page 11: TOC
    toc_lines = ["Table of Contents"] + [
        f"{num} {title} {page}" for num, title, page in _FIXTURE_CHAPTERS
    ]
    _add_text_page(writer, toc_lines)

    # Page 12: separator
    _add_text_page(writer, [""])

    # Pages 13-89: chapter content
    chapter_by_page = {page: (num, title) for num, title, page in _FIXTURE_CHAPTERS}
    for p in range(13, 90):
        if p in chapter_by_page:
            num, title = chapter_by_page[p]
            lines = [
                f"Chapter {num}",
                title,
                "Alice was beginning to get very tired of sitting by her sister.",
                f"This is chapter {num}. Alice continued her adventure.",
                "She wondered what would happen next in this curious place.",
            ]
        else:
            lines = [
                "Alice had many more adventures to come.",
                "She was curious about everything around her.",
            ]
        _add_text_page(writer, lines)

    buf = io.BytesIO()
    writer.write(buf)
    out_path.write_bytes(buf.getvalue())


def _get_alice_pdf(tmp_dir: Path) -> Path:
    """Return the real Alice PDF if present, else create and return a fixture."""
    real = Path(__file__).resolve().parent.parent / "carroll-1865.pdf"
    if real.exists():
        return real
    fixture = tmp_dir / "alice-fixture.pdf"
    _make_alice_fixture_pdf(fixture)
    return fixture


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
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = _get_alice_pdf(Path(tmp))
            chapters = detect_chapters_from_pdf(pdf_path, skip_pages=12, toc_page=11)
        self.assertEqual(len(chapters), 12)
        self.assertEqual(chapters[0].title, "Down the Rabbit-Hole")
        self.assertEqual(chapters[6].title, "A Mad Tea-Party")
        self.assertEqual(chapters[0].start_page, 13)


class TestExtractTextFromPdf(unittest.TestCase):
    def test_extracts_non_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pdf_path = _get_alice_pdf(Path(tmp))
            text = extract_text_from_pdf(pdf_path)
        self.assertGreater(len(text), 1000)
        self.assertIn("Alice", text)


class TestIngestPdfToChapters(unittest.TestCase):
    def test_ingest_creates_markdown_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pdf_path = _get_alice_pdf(tmp_path)
            out_dir = tmp_path / "chapters"
            written = ingest_pdf_to_chapters(pdf_path, out_dir)
            self.assertEqual(len(written), 12)
            for p in written:
                self.assertTrue(p.exists())
                content = p.read_text()
                self.assertIn("# Chapter", content)
                self.assertIn("Alice", content)

    def test_raises_when_pdf_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                ingest_pdf_to_chapters(Path(tmp) / "nonexistent.pdf", Path(tmp))
