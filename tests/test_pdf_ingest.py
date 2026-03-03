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


def _write_raw_pdf(pages: list[list[str]], out_path: Path) -> None:
    """Write a minimal valid multi-page PDF with text using raw PDF syntax.

    Uses no private or internal pypdf APIs, making the fixture stable across
    pypdf releases.
    """
    buf = io.BytesIO()
    n_pages = len(pages)
    # Object layout: 1=Catalog, 2=Pages, 3=Font, then pairs (page dict, content stream)
    CATALOG, PAGES, FONT = 1, 2, 3
    FIRST_PAGE_OBJ = 4
    offsets: dict[int, int] = {}
    buf.write(b"%PDF-1.4\n")

    def write_obj(num: int, data: bytes) -> None:
        offsets[num] = buf.tell()
        buf.write(f"{num} 0 obj\n".encode())
        buf.write(data)
        buf.write(b"\nendobj\n")

    def write_stream_obj(num: int, stream_data: bytes) -> None:
        offsets[num] = buf.tell()
        buf.write(f"{num} 0 obj\n".encode())
        buf.write(f"<< /Length {len(stream_data)} >>\nstream\n".encode())
        buf.write(stream_data)
        buf.write(b"\nendstream\nendobj\n")

    page_obj_nums = [FIRST_PAGE_OBJ + i * 2 for i in range(n_pages)]
    kids_str = " ".join(f"{k} 0 R" for k in page_obj_nums)

    write_obj(CATALOG, f"<< /Type /Catalog /Pages {PAGES} 0 R >>".encode())
    write_obj(PAGES, f"<< /Type /Pages /Kids [{kids_str}] /Count {n_pages} >>".encode())
    write_obj(FONT, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    for i, text_lines in enumerate(pages):
        page_num = FIRST_PAGE_OBJ + i * 2
        content_num = page_num + 1
        content_parts = []
        y = 730
        for line in text_lines:
            safe = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            content_parts.append(f"BT /F1 10 Tf 50 {y} Td ({safe}) Tj ET")
            y -= 14
            if y < 50:
                break
        content_bytes = "\n".join(content_parts).encode("latin-1")
        page_dict = (
            f"<< /Type /Page /Parent {PAGES} 0 R "
            f"/MediaBox [0 0 612 792] "
            f"/Contents {content_num} 0 R "
            f"/Resources << /Font << /F1 {FONT} 0 R >> >> >>"
        ).encode()
        write_obj(page_num, page_dict)
        write_stream_obj(content_num, content_bytes)

    n_objects = FIRST_PAGE_OBJ + n_pages * 2
    xref_offset = buf.tell()
    buf.write(b"xref\n")
    buf.write(f"0 {n_objects}\n".encode())
    buf.write(b"0000000000 65535 f \n")  # object 0 is always free (PDF spec requirement)
    for num in range(1, n_objects):
        buf.write(f"{offsets[num]:010d} 00000 n \n".encode())
    buf.write(b"trailer\n")
    buf.write(f"<< /Size {n_objects} /Root {CATALOG} 0 R >>\n".encode())
    buf.write(b"startxref\n")
    buf.write(f"{xref_offset}\n".encode())
    buf.write(b"%%EOF\n")
    out_path.write_bytes(buf.getvalue())


def _make_alice_fixture_pdf(out_path: Path) -> None:
    """Create a minimal multi-page PDF that mimics Alice in Wonderland structure.

    Produces a TOC on page 11 and chapter content pages starting at page 13,
    matching the structure expected by the ingest pipeline.
    """
    pages: list[list[str]] = []

    # Pages 1-10: front matter
    for _ in range(10):
        pages.append(["Front matter"])

    # Page 11: TOC
    pages.append(
        ["Table of Contents"] + [f"{num} {title} {page}" for num, title, page in _FIXTURE_CHAPTERS]
    )

    # Page 12: separator
    pages.append([""])

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
        pages.append(lines)

    _write_raw_pdf(pages, out_path)


def _get_alice_pdf(tmp_dir: Path) -> Path:
    """Return a fixture PDF for testing.

    Uses the real Alice PDF only when the ``USE_REAL_PDF_TESTS`` environment
    variable is set to a non-empty value, so that unit tests are deterministic
    by default.
    """
    import os

    real = Path(__file__).resolve().parent.parent / "carroll-1865.pdf"
    if os.environ.get("USE_REAL_PDF_TESTS") and real.exists():
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
