"""Tests for the embedding engine and search."""

import shutil
import tempfile
from pathlib import Path

import pytest

from indexer.embedder import BookIndex, _sanitize_metadata, _truncate_for_embedding


def test_sanitize_metadata_preserves_allowed_types():
    """ChromaDB accepts str, int, float, bool. These pass through unchanged."""
    meta = {"level": "paragraph", "chapter_num": 7, "score": 0.5, "flag": True}
    assert _sanitize_metadata(meta) == meta


def test_sanitize_metadata_converts_none():
    """None values become empty string for ChromaDB compatibility."""
    assert _sanitize_metadata({"x": None}) == {"x": ""}


def test_sanitize_metadata_converts_other_types():
    """Non-primitive types are stringified."""
    assert _sanitize_metadata({"path": Path("/tmp")}) == {"path": "/tmp"}


def test_truncate_short_text():
    text = "Short text."
    assert _truncate_for_embedding(text) == text


def test_truncate_long_text():
    text = "x" * 10000
    result = _truncate_for_embedding(text, max_chars=200)
    assert len(result) < 10000
    assert "[...]" in result


@pytest.mark.integration
class TestBookIndex:
    @pytest.fixture(scope="class")
    def index(self):
        tmpdir = Path(tempfile.mkdtemp())
        idx = BookIndex(persist_dir=tmpdir)
        idx.build(force=True)
        yield idx
        shutil.rmtree(tmpdir, ignore_errors=True)

    def test_stats_populated(self, index):
        stats = index.stats()
        assert stats["sentence"] > 5000
        assert stats["paragraph"] > 500
        assert stats["scene"] > 20
        assert stats["chapter"] == 26
        assert stats["act"] == 5

    def test_search_returns_results(self, index):
        results = index.query("Harry's revolver", level="sentence", n_results=5)
        assert len(results) > 0
        assert "text" in results[0]
        assert "metadata" in results[0]

    def test_search_level_filtering(self, index):
        results = index.query("the Egg", level="paragraph", n_results=3)
        for r in results:
            assert r["metadata"]["level"] == "paragraph"

    def test_search_chapter_filter(self, index):
        results = index.query("copper", level="sentence", n_results=5,
                              where={"chapter_num": 3})
        for r in results:
            assert r["metadata"]["chapter_num"] == 3

    def test_search_act_filter(self, index):
        results = index.query("Olive", level="paragraph", n_results=5,
                              where={"act": "Act I – The Hire"})
        for r in results:
            assert r["metadata"]["act"] == "Act I – The Hire"

    def test_hierarchical_search(self, index):
        results = index.query_hierarchical(
            "Tomás slug",
            top_level="chapter",
            drill_level="sentence",
            n_top=2,
            n_drill=3,
        )
        assert len(results) > 0
        assert "_parent" in results[0]

    def test_metadata_roundtrip(self, index):
        """Stored metadata is retrieved unchanged (ChromaDB compatibility)."""
        results = index.query("Harry", level="paragraph", n_results=5)
        for r in results:
            meta = r["metadata"]
            assert "chapter_num" in meta
            assert isinstance(meta["chapter_num"], int)
            assert "act" in meta
            assert isinstance(meta["act"], str)
