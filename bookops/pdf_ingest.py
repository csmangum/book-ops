"""
PDF extraction and chapter detection for book ingest.

Extracts text from PDFs, handles common artifacts (hyphenation, ligatures),
preserves paragraph boundaries, and detects chapter boundaries.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .utils import ensure_dir, write_text


# Common ligatures and their replacements
LIGATURE_MAP = {
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬀ": "ff",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬆ": "st",
    "ﬅ": "ft",
}


def _clean_text(text: str) -> str:
    """Fix ligatures and common PDF artifacts."""
    result = text
    for lig, repl in LIGATURE_MAP.items():
        result = result.replace(lig, repl)
    return result


def _fix_hyphenation(text: str) -> str:
    """
    Rejoin words broken by hyphenation at line breaks.
    E.g. "some-\nthing" -> "something"
    """
    # Match hyphen at end of line followed by newline and optional whitespace
    return re.sub(r"-\s*\n\s*", "", text)


def _strip_page_headers(text: str, chapter_num: int | None = None) -> str:
    """
    Remove running headers like "14 CHAPTER 1. DOWN THE RABBIT-HOLE" and standalone page numbers.
    """
    lines = text.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        # Skip standalone page numbers
        if stripped.isdigit() and len(stripped) <= 4:
            continue
        # Skip "N CHAPTER N. TITLE" running headers
        if re.match(r"^\d+\s+CHAPTER\s+\d+\.\s+[A-Z\s\-]+$", stripped, re.IGNORECASE):
            continue
        out.append(line)
    return "\n".join(out)


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract raw text from a PDF, page by page, with basic cleanup.
    """
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        raw = page.extract_text()
        if raw:
            cleaned = _clean_text(raw)
            parts.append(cleaned)
    return "\n\n".join(parts)


def extract_text_with_structure(pdf_path: Path) -> str:
    """
    Extract text and apply hyphenation fix and paragraph preservation.
    Double newlines (page breaks) are preserved as paragraph cues.
    """
    full = extract_text_from_pdf(pdf_path)
    fixed = _fix_hyphenation(full)
    return fixed


@dataclass
class ChapterInfo:
    """Chapter boundary info from TOC or heading detection."""

    number: int
    title: str
    start_page: int  # 1-based


# Alice in Wonderland TOC structure: "1 Down the Rabbit-Hole 13"
_ALICE_TOC_RE = re.compile(
    r"^(\d+)\s+(.+?)\s+(\d+)\s*$",
    re.MULTILINE,
)


def _parse_alice_toc(toc_text: str) -> list[ChapterInfo]:
    """Parse Alice TOC format: '1 Down the Rabbit-Hole 13'."""
    chapters = []
    for m in _ALICE_TOC_RE.finditer(toc_text):
        num = int(m.group(1))
        title = m.group(2).strip()
        page = int(m.group(3))
        # Filter: page number should be reasonable (13-100 for this book)
        if 10 <= page <= 100 and 1 <= num <= 20:
            chapters.append(ChapterInfo(number=num, title=title, start_page=page))
    return chapters


# Generic chapter heading: "Chapter N" or "CHAPTER N" followed by title
_CHAPTER_HEADING_RE = re.compile(
    r"^Chapter\s+(\d+)\s*\n(.+?)(?=\n|$)",
    re.IGNORECASE | re.MULTILINE,
)


def detect_chapters_from_pdf(
    pdf_path: Path,
    skip_pages: int = 12,
    toc_page: int = 11,
) -> list[ChapterInfo]:
    """
    Detect chapter boundaries from PDF.
    Uses TOC page if available, else scans for "Chapter N" headings.
    """
    reader = PdfReader(str(pdf_path))
    # Try TOC first (Alice has it on page 11)
    if toc_page <= len(reader.pages):
        toc_text = reader.pages[toc_page - 1].extract_text() or ""
        chapters = _parse_alice_toc(toc_text)
        if chapters:
            return chapters

    # Fallback: scan for "Chapter N" headings
    chapters = []
    for i in range(skip_pages, len(reader.pages)):
        text = reader.pages[i].extract_text() or ""
        for m in _CHAPTER_HEADING_RE.finditer(text):
            num = int(m.group(1))
            title = m.group(2).strip()
            chapters.append(ChapterInfo(number=num, title=title, start_page=i + 1))
            break  # One chapter per page in this scan
    return chapters


def extract_chapter_text(
    pdf_path: Path,
    start_page: int,
    end_page: int,
) -> str:
    """Extract text for a chapter from start_page to end_page (1-based, inclusive)."""
    reader = PdfReader(str(pdf_path))
    parts = []
    for i in range(start_page - 1, min(end_page, len(reader.pages))):
        raw = reader.pages[i].extract_text()
        if raw:
            cleaned = _clean_text(raw)
            fixed = _fix_hyphenation(cleaned)
            parts.append(_strip_page_headers(fixed))
    return "\n\n".join(parts)


def _slugify_title(title: str) -> str:
    """Convert title to filename-safe slug."""
    slug = re.sub(r"[^\w\s-]", "", title)
    slug = re.sub(r"[-\s]+", " ", slug).strip()
    return slug.replace(" ", "-")[:80]


def ingest_pdf_to_chapters(
    pdf_path: Path,
    output_dir: Path,
    skip_pages: int = 12,
    toc_page: int = 11,
) -> list[Path]:
    """
    Full pipeline: extract PDF, detect chapters, write Markdown files.

    Returns list of written chapter paths.
    """
    pdf_path = Path(pdf_path).resolve()
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    chapters = detect_chapters_from_pdf(pdf_path, skip_pages=skip_pages, toc_page=toc_page)
    if not chapters:
        raise ValueError("No chapters detected in PDF")

    ensure_dir(output_dir)
    written: list[Path] = []

    for i, ch in enumerate(chapters):
        start = ch.start_page
        end = chapters[i + 1].start_page - 1 if i + 1 < len(chapters) else 999
        text = extract_chapter_text(pdf_path, start, end)

        # Remove "Chapter N" and title line from start (we'll add as markdown header)
        text = _strip_chapter_header_from_body(text, ch.number, ch.title)

        # Normalize paragraph breaks: ensure double newline between paragraphs
        paragraphs = re.split(r"\n\s*\n", text)
        body = "\n\n".join(p.strip() for p in paragraphs if p.strip())

        filename = f"{ch.number}_{ch.title}.md"
        # Sanitize filename for filesystem
        safe_title = _slugify_title(ch.title) or f"chapter-{ch.number}"
        filename = f"{ch.number}_{safe_title}.md"

        content = f"# Chapter {ch.number}\n\n{ch.title}\n\n{body}\n"
        out_path = output_dir / filename
        write_text(out_path, content)
        written.append(out_path)

    return written


def _strip_chapter_header_from_body(text: str, chapter_num: int, title: str) -> str:
    """Remove the 'Chapter N' and title lines from the start of extracted body."""
    lines = text.split("\n")
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r"^Chapter\s+" + str(chapter_num) + r"\s*$", stripped, re.IGNORECASE):
            start = i + 1
            continue
        if stripped == title and i < 3:
            start = i + 1
            continue
        if stripped and start > 0:
            break
    return "\n".join(lines[start:]).strip()
