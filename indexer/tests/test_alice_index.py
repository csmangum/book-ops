"""Scripted tests for the Alice in Wonderland semantic index.

Runs the evaluation queries from the test plan and asserts on chapter presence
and minimum result counts. Requires the Alice index to exist (built via
`bookops ingest-pdf carroll-1865.pdf --chapters-dir chapters --book-id alice --build`).

Run with: INDEXER_INTEGRATION_TESTS=1 pytest indexer/tests/test_alice_index.py -v
"""

from __future__ import annotations

from pathlib import Path

import pytest

from indexer.embedder import BookIndex, INDEX_DIR

# Project root: indexer/embedder.py -> indexer/ -> project root
PROJECT_ROOT = INDEX_DIR.parent
ALICE_CHAPTERS = PROJECT_ROOT / "chapters"
ALICE_INDEX = PROJECT_ROOT / ".book_index"


def _is_alice_index() -> bool:
    """Check if the index at ALICE_INDEX is the Alice index (12 chapters)."""
    if not (ALICE_INDEX / "chromadb").exists():
        return False
    idx = BookIndex(persist_dir=ALICE_INDEX)
    stats = idx.stats()
    return stats["chapter"] == 12 and sum(stats.values()) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not _is_alice_index(),
    reason="Alice index required (12 chapters). Run: bookops ingest-pdf carroll-1865.pdf --chapters-dir chapters --book-id alice --build",
)
class TestAliceIndex:
    @pytest.fixture(scope="class")
    def index(self):
        return BookIndex(persist_dir=ALICE_INDEX)

    def test_stats_alice_structure(self, index):
        """Index has expected Alice structure: 12 chapters, 1 act."""
        stats = index.stats()
        assert stats["chapter"] == 12
        assert stats["act"] == 1
        assert stats["sentence"] > 500
        assert stats["paragraph"] > 50

    def test_search_rabbit_hole_returns_ch1(self, index):
        """Paragraph search for 'rabbit hole' surfaces Ch 1."""
        results = index.query("rabbit hole", level="paragraph", n_results=5)
        assert len(results) >= 1
        top = results[0]
        assert top["metadata"]["chapter_num"] == 1
        assert top["metadata"]["chapter_title"] == "Down the Rabbit-Hole"

    def test_search_mad_tea_party_returns_ch7(self, index):
        """Paragraph search for 'mad tea party' surfaces Ch 7."""
        results = index.query("mad tea party", level="paragraph", n_results=5)
        assert len(results) >= 1
        assert results[0]["metadata"]["chapter_num"] == 7
        assert "Mad Tea-Party" in results[0]["metadata"]["chapter_title"]

    def test_search_queen_hearts_croquet_returns_ch8(self, index):
        """Paragraph search for 'Queen of Hearts croquet' surfaces Ch 8."""
        results = index.query(
            "Queen of Hearts croquet", level="paragraph", n_results=5
        )
        assert len(results) >= 1
        assert results[0]["metadata"]["chapter_num"] == 8

    def test_search_cheshire_cat_grin_returns_ch6(self, index):
        """Paragraph search for 'Cheshire cat grin' surfaces Ch 6."""
        results = index.query(
            "Cheshire cat grin", level="paragraph", n_results=5
        )
        assert len(results) >= 1
        assert results[0]["metadata"]["chapter_num"] == 6

    def test_search_drink_me_sentence_level(self, index):
        """Sentence-level search for 'drink me' returns results."""
        results = index.query("drink me", level="sentence", n_results=5)
        assert len(results) >= 1
        assert "text" in results[0]
        assert "metadata" in results[0]

    def test_search_trial_verdict_chapter_level(self, index):
        """Chapter-level search for 'trial and verdict' returns trial chapters."""
        results = index.query(
            "trial and verdict", level="chapter", n_results=3
        )
        assert len(results) >= 1
        chapter_nums = [r["metadata"]["chapter_num"] for r in results]
        assert any(c in (11, 12) for c in chapter_nums)

    def test_hybrid_curiouser_and_curiouser(self, index):
        """Hybrid search surfaces exact phrase 'curiouser and curiouser'."""
        results = index.query_hybrid(
            "curiouser and curiouser", level="paragraph", n_results=10
        )
        assert len(results) >= 1
        texts = [r["text"].lower() for r in results]
        assert any("curiouser" in t for t in texts)

    def test_hybrid_eat_me_or_drink_me(self, index):
        """Hybrid search for 'EAT ME' surfaces bottle/cake label from Ch 1."""
        results = index.query_hybrid("EAT ME", level="paragraph", n_results=10)
        assert len(results) >= 1
        chapter_nums = [r["metadata"]["chapter_num"] for r in results]
        assert 1 in chapter_nums

    def test_hierarchical_drill_white_rabbit_watch(self, index):
        """Drill-down from chapters to paragraphs for 'white rabbit watch'."""
        results = index.query_hierarchical(
            "white rabbit watch",
            top_level="chapter",
            drill_level="paragraph",
            n_top=2,
            n_drill=5,
        )
        assert len(results) >= 1
        assert "_parent" in results[0]
        assert results[0]["_parent"]["level"] == "chapter"

    def test_chapter_filter_alice_in_ch7(self, index):
        """Chapter filter restricts 'Alice' search to Ch 7 only."""
        results = index.query(
            "Alice",
            level="paragraph",
            n_results=5,
            where={"chapter_num": 7},
        )
        assert len(results) >= 1
        for r in results:
            assert r["metadata"]["chapter_num"] == 7
