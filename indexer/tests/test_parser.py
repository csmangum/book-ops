"""Tests for the manuscript parser."""

import pytest
from indexer.parser import (
    parse_all_chapters,
    build_act_units,
    _split_scenes,
    _split_paragraphs,
    _split_sentences,
    _strip_header,
    _chapter_number,
    _chapter_title_from_filename,
    ACT_MAP,
    CHAPTER_DIR,
)


def test_chapter_number_parsing():
    assert _chapter_number("0_The City That Forgot.md") == 0
    assert _chapter_number("7_The Egg and the Bullet.md") == 7
    assert _chapter_number("25_Eggs, Tomatoes, and the Quiet After.md") == 25


def test_chapter_number_bad_input():
    with pytest.raises(ValueError):
        _chapter_number("no_number_here.md")


def test_chapter_title_from_filename():
    assert _chapter_title_from_filename("7_The Egg and the Bullet.md") == "The Egg and the Bullet"
    assert _chapter_title_from_filename("0_The City That Forgot How to Sleep.md") == (
        "The City That Forgot How to Sleep"
    )


def test_strip_header():
    text = "# Chapter One\n\nThe Last Man\n\nNine days until the equinox."
    body = _strip_header(text)
    assert body.startswith("The Last Man")
    assert "# Chapter" not in body


def test_split_scenes_with_breaks():
    text = "Scene one text.\n\n---\n\nScene two text."
    scenes = _split_scenes(text)
    assert len(scenes) == 2
    assert "Scene one" in scenes[0]
    assert "Scene two" in scenes[1]


def test_split_scenes_no_breaks():
    text = "Just one continuous scene.\n\nWith multiple paragraphs."
    scenes = _split_scenes(text)
    assert len(scenes) == 1


def test_split_paragraphs():
    text = "First paragraph.\n\nSecond paragraph.\n\nThird."
    paras = _split_paragraphs(text)
    assert len(paras) == 3


def test_split_sentences():
    text = "Harry walked in. The rain was cold. He didn't care."
    sents = _split_sentences(text)
    assert len(sents) == 3


def test_split_sentences_filters_markdown_artifacts():
    """Markdown italic markers (*, "*) are not indexed as sentence units."""
    # Standalone "*" or '"*' are filtered out
    assert _split_sentences("*") == []
    assert _split_sentences('"*') == []
    assert _split_sentences('*"') == []
    # Real sentences are preserved; "*" alone is filtered
    sents = _split_sentences("Hello. * Bye.")
    assert "Hello." in sents
    assert "*" not in sents


def test_act_map_coverage():
    for ch in range(26):
        assert ch in ACT_MAP, f"Chapter {ch} missing from ACT_MAP"


def test_parse_all_chapters_raises_when_dir_missing(tmp_path):
    """parse_all_chapters raises FileNotFoundError when directory does not exist."""
    missing = tmp_path / "nonexistent"
    with pytest.raises(FileNotFoundError, match="not found"):
        parse_all_chapters(chapters_dir=missing)


def test_parse_all_chapters_raises_when_no_files(tmp_path):
    """parse_all_chapters raises FileNotFoundError when directory has no .md files."""
    with pytest.raises(FileNotFoundError, match="No .md files"):
        parse_all_chapters(chapters_dir=tmp_path)


@pytest.mark.skipif(
    not CHAPTER_DIR.exists() or not list(CHAPTER_DIR.glob("*.md")),
    reason="Chapters directory with .md files required",
)
class TestFullParse:
    @pytest.fixture(scope="class")
    def all_units(self):
        return parse_all_chapters()

    def test_has_all_levels(self, all_units):
        levels = {u.level for u in all_units}
        assert levels == {"sentence", "paragraph", "scene", "chapter"}

    def test_has_all_chapters(self, all_units):
        chapter_nums = {u.chapter_num for u in all_units if u.level == "chapter"}
        assert chapter_nums == set(range(26))

    def test_sentence_count_reasonable(self, all_units):
        sentences = [u for u in all_units if u.level == "sentence"]
        assert len(sentences) > 5000

    def test_paragraph_count_reasonable(self, all_units):
        paragraphs = [u for u in all_units if u.level == "paragraph"]
        assert len(paragraphs) > 500

    def test_act_units(self, all_units):
        acts = build_act_units(all_units)
        act_names = {a.act for a in acts}
        assert "Prologue" in act_names
        assert "Act I – The Hire" in act_names
        assert "Act II – The Descent" in act_names
        assert "Act III – The Gate" in act_names
        assert "Epilogue" in act_names

    def test_metadata_structure(self, all_units):
        u = all_units[0]
        meta = u.metadata
        assert "level" in meta
        assert "act" in meta
        assert "chapter_num" in meta
        assert "chapter_title" in meta
        assert "source_file" in meta


@pytest.mark.skipif(
    not (CHAPTER_DIR.parent / "chapters_alice").exists()
    or not list((CHAPTER_DIR.parent / "chapters_alice").glob("*.md")),
    reason="chapters_alice with .md files required",
)
def test_parse_alice_with_book_id():
    """Parse Alice chapters with book_id=alice uses Full Book act."""
    from pathlib import Path

    alice_dir = CHAPTER_DIR.parent / "chapters_alice"
    units = parse_all_chapters(chapters_dir=alice_dir, book_id="alice")
    chapter_units = [u for u in units if u.level == "chapter"]
    assert len(chapter_units) == 12
    for u in chapter_units:
        assert u.act == "Full Book"
