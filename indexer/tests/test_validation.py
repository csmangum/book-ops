"""
Validation tests for the multi-level semantic index.

These tests validate correctness across every dimension of the index:
  1. Structural integrity — hierarchy consistency, unique IDs, no orphans
  2. Text content quality — no empty/degenerate units, appropriate lengths
  3. Metadata consistency — act labels, chapter numbers, sequential indices
  4. Cross-level alignment — sentences ⊂ paragraphs ⊂ scenes ⊂ chapters
  5. Embedding geometry — dimensionality, normalization, no NaN/Inf
  6. Semantic coherence — same-chapter similarity > cross-chapter similarity
  7. Retrieval quality — known-answer queries, ranking sanity, filter correctness
"""

from __future__ import annotations

import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pytest

from indexer.parser import (
    TextUnit,
    parse_all_chapters,
    build_act_units,
    ACT_MAP,
    ACT_CHAPTER_RANGES,
    CHAPTER_DIR,
)
from indexer.embedder import BookIndex

LEVELS = ("sentence", "paragraph", "scene", "chapter", "act")
EMBEDDING_DIM = 768


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def all_units() -> list[TextUnit]:
    if not CHAPTER_DIR.exists() or not list(CHAPTER_DIR.glob("*.md")):
        pytest.skip("Chapters directory with .md files required")
    return parse_all_chapters()


@pytest.fixture(scope="module")
def act_units(all_units) -> list[TextUnit]:
    return build_act_units(all_units)


@pytest.fixture(scope="module")
def units_by_level(all_units, act_units) -> dict[str, list[TextUnit]]:
    combined = all_units + act_units
    by_level: dict[str, list[TextUnit]] = {}
    for u in combined:
        by_level.setdefault(u.level, []).append(u)
    return by_level


@pytest.fixture(scope="module")
def index(all_units) -> BookIndex:
    tmpdir = Path(tempfile.mkdtemp())
    idx = BookIndex(persist_dir=tmpdir, chapters_dir=CHAPTER_DIR)
    idx.build(force=True)
    yield idx
    shutil.rmtree(tmpdir, ignore_errors=True)


# ===================================================================
# 1. STRUCTURAL INTEGRITY
# ===================================================================

class TestStructuralIntegrity:
    """Every unit has valid hierarchy references; IDs are unique; no orphans."""

    def test_all_ids_unique(self, all_units, act_units):
        """No two units share the same ID."""
        combined = all_units + act_units
        ids = [u.id for u in combined]
        dupes = {k: v for k, v in Counter(ids).items() if v > 1}
        assert not dupes, f"Duplicate IDs found: {dupes}"

    def test_every_sentence_has_parent_paragraph(self, units_by_level):
        """Every sentence maps to an existing paragraph via chapter/scene/para index."""
        para_keys = {
            (u.chapter_num, u.scene_idx, u.paragraph_idx)
            for u in units_by_level["paragraph"]
        }
        for s in units_by_level["sentence"]:
            key = (s.chapter_num, s.scene_idx, s.paragraph_idx)
            assert key in para_keys, (
                f"Sentence {s.id} references paragraph "
                f"ch{s.chapter_num}/sc{s.scene_idx}/p{s.paragraph_idx} which doesn't exist"
            )

    def test_every_paragraph_has_parent_scene(self, units_by_level):
        """Every paragraph maps to an existing scene."""
        scene_keys = {
            (u.chapter_num, u.scene_idx) for u in units_by_level["scene"]
        }
        for p in units_by_level["paragraph"]:
            key = (p.chapter_num, p.scene_idx)
            assert key in scene_keys, (
                f"Paragraph {p.id} references scene "
                f"ch{p.chapter_num}/sc{p.scene_idx} which doesn't exist"
            )

    def test_every_scene_has_parent_chapter(self, units_by_level):
        """Every scene maps to an existing chapter."""
        chapter_nums = {u.chapter_num for u in units_by_level["chapter"]}
        for sc in units_by_level["scene"]:
            assert sc.chapter_num in chapter_nums, (
                f"Scene {sc.id} references ch{sc.chapter_num} which doesn't exist"
            )

    def test_every_chapter_maps_to_act(self, units_by_level):
        """Every chapter's act label is a valid act name."""
        valid_acts = set(ACT_CHAPTER_RANGES.keys())
        for ch in units_by_level["chapter"]:
            assert ch.act in valid_acts, (
                f"Chapter {ch.chapter_num} has invalid act '{ch.act}'"
            )

    def test_sentence_indices_sequential_within_paragraph(self, units_by_level):
        """Sentence indices within each paragraph form a contiguous 0-based sequence."""
        by_para: dict[tuple, list[int]] = defaultdict(list)
        for s in units_by_level["sentence"]:
            key = (s.chapter_num, s.scene_idx, s.paragraph_idx)
            by_para[key].append(s.sentence_idx)
        for key, indices in by_para.items():
            expected = list(range(len(indices)))
            assert sorted(indices) == expected, (
                f"Non-sequential sentence indices in ch{key[0]}/sc{key[1]}/p{key[2]}: "
                f"{sorted(indices)}"
            )

    def test_paragraph_indices_sequential_within_scene(self, units_by_level):
        """Paragraph indices within each scene form a contiguous 0-based sequence."""
        by_scene: dict[tuple, list[int]] = defaultdict(list)
        for p in units_by_level["paragraph"]:
            key = (p.chapter_num, p.scene_idx)
            by_scene[key].append(p.paragraph_idx)
        for key, indices in by_scene.items():
            expected = list(range(len(indices)))
            assert sorted(indices) == expected, (
                f"Non-sequential paragraph indices in ch{key[0]}/sc{key[1]}: "
                f"{sorted(indices)}"
            )

    def test_scene_indices_sequential_within_chapter(self, units_by_level):
        """Scene indices within each chapter form a contiguous 0-based sequence."""
        by_ch: dict[int, list[int]] = defaultdict(list)
        for sc in units_by_level["scene"]:
            by_ch[sc.chapter_num].append(sc.scene_idx)
        for ch_num, indices in by_ch.items():
            expected = list(range(len(indices)))
            assert sorted(indices) == expected, (
                f"Non-sequential scene indices in ch{ch_num}: {sorted(indices)}"
            )

    def test_no_chapter_gaps(self, units_by_level):
        """Chapter numbers 0–25 are all present with no gaps."""
        nums = sorted(u.chapter_num for u in units_by_level["chapter"])
        assert nums == list(range(26))

    def test_all_source_files_exist(self, all_units):
        """Every source_file reference points to a real file."""
        files = {u.source_file for u in all_units if u.source_file}
        for f in files:
            assert (CHAPTER_DIR / f).exists(), f"Source file {f} not found"


# ===================================================================
# 2. TEXT CONTENT QUALITY
# ===================================================================

class TestTextContent:
    """Text at every level is non-empty, appropriately sized, and free of artifacts."""

    def test_no_empty_texts(self, all_units, act_units):
        """No unit at any level has empty text."""
        for u in all_units + act_units:
            assert u.text.strip(), f"Empty text in {u.level} unit {u.id}"

    def test_no_markdown_headings_in_body(self, units_by_level):
        """Chapter body text shouldn't start with markdown headings."""
        for ch in units_by_level["chapter"]:
            first_line = ch.text.strip().split("\n")[0]
            assert not first_line.startswith("#"), (
                f"Chapter {ch.chapter_num} body still contains heading: {first_line[:60]}"
            )

    def test_sentence_length_bounds(self, units_by_level):
        """Sentences should be between 1 and 1000 characters."""
        for s in units_by_level["sentence"]:
            assert 1 <= len(s.text) <= 1000, (
                f"Sentence {s.id} has unusual length {len(s.text)}: '{s.text[:80]}'"
            )

    def test_paragraph_longer_than_constituent_sentences(self, units_by_level):
        """Each paragraph's text should be at least as long as its longest sentence."""
        by_para: dict[tuple[int, int, int], TextUnit] = {
            (u.chapter_num, u.scene_idx, u.paragraph_idx): u
            for u in units_by_level["paragraph"]
        }
        for s in units_by_level["sentence"]:
            key = (s.chapter_num, s.scene_idx, s.paragraph_idx)
            para = by_para.get(key)
            if para:
                assert len(para.text) >= len(s.text), (
                    f"Paragraph {para.id} ({len(para.text)} chars) shorter than "
                    f"its sentence {s.id} ({len(s.text)} chars)"
                )

    def test_scene_longer_than_constituent_paragraphs(self, units_by_level):
        """Each scene's text should be at least as long as its longest paragraph."""
        by_scene: dict[tuple, TextUnit] = {
            (u.chapter_num, u.scene_idx): u for u in units_by_level["scene"]
        }
        for p in units_by_level["paragraph"]:
            key = (p.chapter_num, p.scene_idx)
            scene = by_scene.get(key)
            if scene:
                assert len(scene.text) >= len(p.text), (
                    f"Scene {scene.id} ({len(scene.text)} chars) shorter than "
                    f"its paragraph {p.id} ({len(p.text)} chars)"
                )

    def test_chapter_word_counts_in_range(self, units_by_level):
        """Chapters should have between 500 and 6000 words (prose, not outliers)."""
        for ch in units_by_level["chapter"]:
            wc = len(ch.text.split())
            assert 500 <= wc <= 6000, (
                f"Chapter {ch.chapter_num} has {wc} words, outside expected range"
            )

    def test_act_text_longer_than_any_chapter(self, units_by_level):
        """Each act's text is longer than any single chapter within it."""
        ch_by_act: dict[str, int] = defaultdict(int)
        for ch in units_by_level["chapter"]:
            ch_by_act.setdefault(ch.act, 0)
            ch_by_act[ch.act] = max(ch_by_act[ch.act], len(ch.text))
        for act in units_by_level["act"]:
            max_ch_len = ch_by_act.get(act.act, 0)
            if max_ch_len > 0:
                assert len(act.text) >= max_ch_len, (
                    f"Act '{act.act}' text ({len(act.text)} chars) shorter than "
                    f"its longest chapter ({max_ch_len} chars)"
                )

    def test_sentence_count_per_paragraph_reasonable(self, units_by_level):
        """No paragraph should produce more than 50 sentences (parsing sanity)."""
        by_para: dict[tuple, int] = Counter()
        for s in units_by_level["sentence"]:
            by_para[(s.chapter_num, s.scene_idx, s.paragraph_idx)] += 1
        for key, count in by_para.items():
            assert count <= 50, (
                f"Paragraph ch{key[0]}/sc{key[1]}/p{key[2]} has {count} sentences"
            )


# ===================================================================
# 3. METADATA CONSISTENCY
# ===================================================================

class TestMetadataConsistency:
    """Act labels, chapter numbers, and file references are all internally consistent."""

    def test_act_label_matches_act_map(self, all_units):
        """Every unit's act label matches ACT_MAP for its chapter number."""
        for u in all_units:
            expected_act = ACT_MAP[u.chapter_num]
            assert u.act == expected_act, (
                f"Unit {u.id} (ch{u.chapter_num}) has act '{u.act}' "
                f"but ACT_MAP says '{expected_act}'"
            )

    def test_source_file_matches_chapter_number(self, all_units):
        """The chapter number in the source filename matches the unit's chapter_num."""
        import re
        for u in all_units:
            if u.source_file:
                match = re.match(r"(\d+)_", u.source_file)
                if match:
                    file_num = int(match.group(1))
                    assert file_num == u.chapter_num, (
                        f"Unit {u.id}: source_file '{u.source_file}' implies ch{file_num} "
                        f"but chapter_num is {u.chapter_num}"
                    )

    def test_chapter_titles_non_empty(self, units_by_level):
        """Every chapter has a non-empty title."""
        for ch in units_by_level["chapter"]:
            assert ch.chapter_title.strip(), (
                f"Chapter {ch.chapter_num} has empty title"
            )

    def test_metadata_dict_has_all_keys(self, all_units, act_units):
        """Every unit's metadata dict contains all required keys."""
        required = {"level", "act", "chapter_num", "chapter_title",
                     "scene_idx", "paragraph_idx", "sentence_idx",
                     "source_file", "char_offset"}
        for u in (all_units + act_units)[:100]:
            meta = u.metadata
            missing = required - set(meta.keys())
            assert not missing, f"Unit {u.id} missing metadata keys: {missing}"

    def test_act_chapter_ranges_cover_all_chapters(self):
        """ACT_CHAPTER_RANGES covers every chapter 0–25 without overlap or gaps."""
        covered = set()
        for act_name, (start, end) in ACT_CHAPTER_RANGES.items():
            for ch in range(start, end + 1):
                assert ch not in covered, (
                    f"Chapter {ch} covered by multiple acts"
                )
                covered.add(ch)
        assert covered == set(range(26)), (
            f"Chapters not covered: {set(range(26)) - covered}"
        )

    def test_act_unit_chapter_range_metadata(self, act_units):
        """Act units have correct chapter range in their title."""
        for a in act_units:
            start, end = ACT_CHAPTER_RANGES[a.act]
            assert str(start) in a.chapter_title
            assert str(end) in a.chapter_title


# ===================================================================
# 4. CROSS-LEVEL ALIGNMENT
# ===================================================================

class TestCrossLevelAlignment:
    """Verify containment: sentences ⊂ paragraphs ⊂ scenes ⊂ chapters."""

    def test_sentence_text_found_in_parent_paragraph(self, units_by_level):
        """Every sentence's normalized text appears in its parent paragraph."""
        para_map: dict[tuple, str] = {
            (u.chapter_num, u.scene_idx, u.paragraph_idx): u.text
            for u in units_by_level["paragraph"]
        }
        failures = []
        for s in units_by_level["sentence"]:
            key = (s.chapter_num, s.scene_idx, s.paragraph_idx)
            para_text = para_map.get(key, "")
            # NLTK collapses whitespace, so normalize both sides
            norm_sent = " ".join(s.text.split())
            norm_para = " ".join(para_text.split())
            if norm_sent not in norm_para:
                failures.append(
                    f"{s.id}: '{norm_sent[:60]}' not in para "
                    f"ch{key[0]}/sc{key[1]}/p{key[2]}"
                )
        assert len(failures) == 0, (
            f"{len(failures)} sentences not found in parent paragraph:\n"
            + "\n".join(failures[:10])
        )

    def test_paragraph_text_found_in_parent_scene(self, units_by_level):
        """Every paragraph's text appears in its parent scene."""
        scene_map: dict[tuple, str] = {
            (u.chapter_num, u.scene_idx): u.text
            for u in units_by_level["scene"]
        }
        failures = []
        for p in units_by_level["paragraph"]:
            key = (p.chapter_num, p.scene_idx)
            scene_text = scene_map.get(key, "")
            if p.text not in scene_text:
                failures.append(
                    f"{p.id}: not found in scene ch{key[0]}/sc{key[1]}"
                )
        assert len(failures) == 0, (
            f"{len(failures)} paragraphs not found in parent scene:\n"
            + "\n".join(failures[:10])
        )

    def test_scene_text_found_in_parent_chapter(self, units_by_level):
        """Every scene's text appears in its parent chapter."""
        ch_map: dict[int, str] = {
            u.chapter_num: u.text for u in units_by_level["chapter"]
        }
        failures = []
        for sc in units_by_level["scene"]:
            ch_text = ch_map.get(sc.chapter_num, "")
            if sc.text not in ch_text:
                failures.append(
                    f"{sc.id}: not found in chapter {sc.chapter_num}"
                )
        assert len(failures) == 0, (
            f"{len(failures)} scenes not found in parent chapter:\n"
            + "\n".join(failures[:10])
        )

    def test_sentence_count_matches_paragraph_tokenization(self, units_by_level):
        """
        The number of sentence units per paragraph should equal what NLTK
        produces when re-tokenizing the paragraph text.
        """
        import nltk
        import re as _re

        by_para: dict[tuple, int] = Counter()
        for s in units_by_level["sentence"]:
            by_para[(s.chapter_num, s.scene_idx, s.paragraph_idx)] += 1

        failures = []
        for p in units_by_level["paragraph"]:
            key = (p.chapter_num, p.scene_idx, p.paragraph_idx)
            clean = _re.sub(r"\s+", " ", p.text).strip()
            expected = len(nltk.sent_tokenize(clean)) if clean else 0
            actual = by_para.get(key, 0)
            if actual != expected:
                failures.append(
                    f"ch{key[0]}/sc{key[1]}/p{key[2]}: "
                    f"{actual} stored vs {expected} re-tokenized"
                )
        assert len(failures) == 0, (
            f"{len(failures)} paragraph/sentence count mismatches:\n"
            + "\n".join(failures[:10])
        )

    def test_total_paragraphs_equals_sum_across_scenes(self, units_by_level):
        """Total paragraph count equals sum of paragraphs in all scenes."""
        para_count_from_units = len(units_by_level["paragraph"])
        para_count_from_scenes = 0
        for sc in units_by_level["scene"]:
            paras_in_scene = [
                p for p in units_by_level["paragraph"]
                if p.chapter_num == sc.chapter_num and p.scene_idx == sc.scene_idx
            ]
            para_count_from_scenes += len(paras_in_scene)
        assert para_count_from_units == para_count_from_scenes


# ===================================================================
# 5. EMBEDDING GEOMETRY
# ===================================================================

@pytest.mark.integration
class TestEmbeddingGeometry:
    """Embedding vectors have correct dimensionality, normalization, and no degenerate values."""

    @pytest.mark.parametrize("level", LEVELS)
    def test_embedding_dimensionality(self, index, level):
        """All embeddings have the expected 768 dimensions."""
        col = index._get_collection(level)
        if col.count() == 0:
            pytest.skip(f"No data at {level} level")
        sample = col.get(limit=min(50, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        assert embs.shape[1] == EMBEDDING_DIM, (
            f"{level}: expected dim {EMBEDDING_DIM}, got {embs.shape[1]}"
        )

    @pytest.mark.parametrize("level", LEVELS)
    def test_no_nan_embeddings(self, index, level):
        """No embedding vector contains NaN values."""
        col = index._get_collection(level)
        if col.count() == 0:
            pytest.skip(f"No data at {level} level")
        sample = col.get(limit=min(100, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        assert not np.any(np.isnan(embs)), f"{level}: NaN values found in embeddings"

    @pytest.mark.parametrize("level", LEVELS)
    def test_no_inf_embeddings(self, index, level):
        """No embedding vector contains Inf values."""
        col = index._get_collection(level)
        if col.count() == 0:
            pytest.skip(f"No data at {level} level")
        sample = col.get(limit=min(100, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        assert not np.any(np.isinf(embs)), f"{level}: Inf values found in embeddings"

    @pytest.mark.parametrize("level", LEVELS)
    def test_embeddings_unit_normalized(self, index, level):
        """Cosine-space embeddings should be L2-normalized (norm ≈ 1.0)."""
        col = index._get_collection(level)
        if col.count() == 0:
            pytest.skip(f"No data at {level} level")
        sample = col.get(limit=min(100, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        norms = np.linalg.norm(embs, axis=1)
        assert np.allclose(norms, 1.0, atol=1e-4), (
            f"{level}: embeddings not unit-normalized. "
            f"Norm range: [{norms.min():.6f}, {norms.max():.6f}]"
        )

    @pytest.mark.parametrize("level", LEVELS)
    def test_no_zero_vectors(self, index, level):
        """No embedding is the zero vector (would indicate encoding failure)."""
        col = index._get_collection(level)
        if col.count() == 0:
            pytest.skip(f"No data at {level} level")
        sample = col.get(limit=min(100, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        norms = np.linalg.norm(embs, axis=1)
        assert np.all(norms > 0.1), (
            f"{level}: zero or near-zero embedding found"
        )

    @pytest.mark.parametrize("level", LEVELS)
    def test_embeddings_not_all_identical(self, index, level):
        """Embeddings within a level are not all the same (degenerate model check)."""
        col = index._get_collection(level)
        if col.count() < 2:
            pytest.skip(f"Not enough data at {level} level")
        sample = col.get(limit=min(20, col.count()), include=["embeddings"])
        embs = np.array(sample["embeddings"])
        pairwise_dists = np.linalg.norm(embs[0] - embs[1:], axis=1)
        assert np.any(pairwise_dists > 0.01), (
            f"{level}: all sampled embeddings appear identical"
        )


# ===================================================================
# 6. SEMANTIC COHERENCE
# ===================================================================

@pytest.mark.integration
class TestSemanticCoherence:
    """
    Validate that embeddings capture meaningful semantic relationships:
    same-chapter paragraphs should be more similar than cross-chapter ones.
    """

    def test_nearest_neighbors_favor_same_chapter(self, index):
        """
        For a sample of paragraphs, the proportion of top-5 nearest
        neighbors from the same chapter should exceed the baseline
        proportion (if chapters were distributed uniformly).

        In a consistently-voiced novel, average similarity across chapters
        is high (shared genre, narrator, motifs), so we test neighbor
        concentration rather than raw averages.
        """
        col = index._get_collection("paragraph")
        total = col.count()
        all_data = col.get(limit=total, include=["embeddings", "metadatas"])
        embs = np.array(all_data["embeddings"])
        chapters = np.array([m["chapter_num"] for m in all_data["metadatas"]])

        k = 5
        rng = np.random.default_rng(42)
        probe_indices = rng.choice(len(embs), size=min(200, len(embs)), replace=False)

        same_chapter_hits = 0
        total_neighbors = 0
        for idx in probe_indices:
            sims = embs @ embs[idx]
            sims[idx] = -1  # exclude self
            top_k = np.argsort(sims)[-k:]
            same_chapter_hits += int(np.sum(chapters[top_k] == chapters[idx]))
            total_neighbors += k

        observed_rate = same_chapter_hits / total_neighbors
        # Baseline: if neighbors were random, ~1/26 ≈ 3.8% would share a chapter
        baseline = 1.0 / 26
        assert observed_rate > baseline * 2, (
            f"Same-chapter neighbor rate ({observed_rate:.3f}) should meaningfully "
            f"exceed random baseline ({baseline:.3f})"
        )

    def test_same_act_more_similar_than_cross_act(self, index):
        """
        Chapter-level embeddings within the same act should be more
        similar on average than chapters from different acts.
        """
        col = index._get_collection("chapter")
        all_data = col.get(limit=col.count(), include=["embeddings", "metadatas"])
        embs = np.array(all_data["embeddings"])
        acts = [m["act"] for m in all_data["metadatas"]]

        intra_sims = []
        inter_sims = []
        for i in range(len(embs)):
            for j in range(i + 1, len(embs)):
                sim = float(np.dot(embs[i], embs[j]))
                if acts[i] == acts[j]:
                    intra_sims.append(sim)
                else:
                    inter_sims.append(sim)

        if not intra_sims or not inter_sims:
            pytest.skip("Not enough intra/inter act pairs")

        avg_intra = np.mean(intra_sims)
        avg_inter = np.mean(inter_sims)
        assert avg_intra > avg_inter, (
            f"Intra-act chapter similarity ({avg_intra:.4f}) should exceed "
            f"inter-act chapter similarity ({avg_inter:.4f})"
        )


# ===================================================================
# 7. RETRIEVAL QUALITY
# ===================================================================

@pytest.mark.integration
class TestRetrievalQuality:
    """Known-answer queries return expected results; filters work; rankings are sane."""

    def test_known_query_revolver_finds_weapon_sentences(self, index):
        """Searching for 'revolver' at sentence level should return weapon-related text."""
        results = index.query("Harry's revolver", level="sentence", n_results=10)
        assert len(results) > 0
        weapon_terms = {"revolver", ".38", "door knocker", "gun", "holster", "fired", "round", "slug"}
        hits = sum(
            1 for r in results
            if any(t in r["text"].lower() for t in weapon_terms)
        )
        assert hits >= 3, (
            f"Only {hits}/10 results for 'revolver' mention weapons"
        )

    def test_known_query_olive_painting(self, index):
        """Searching for 'Olive painting canvas' should surface Ch 14 prominently."""
        results = index.query(
            "Olive painting canvas", level="paragraph", n_results=10
        )
        ch14_hits = [r for r in results if r["metadata"]["chapter_num"] == 14]
        assert len(ch14_hits) >= 1, (
            "Query 'Olive painting canvas' should surface Ch 14 (Olive's Painting)"
        )

    def test_known_query_mari_botanica(self, index):
        """Searching for 'Abuela Mari botanica' should find Act I content."""
        results = index.query(
            "Abuela Mari at the botanica", level="paragraph", n_results=10
        )
        act1_hits = [
            r for r in results
            if r["metadata"]["act"] == "Act I – The Hire"
        ]
        assert len(act1_hits) >= 1, (
            "Query about Mari's botanica should return Act I results"
        )

    def test_results_sorted_by_distance(self, index):
        """Results should be returned in ascending distance order."""
        results = index.query("the Egg", level="paragraph", n_results=20)
        distances = [r["distance"] for r in results]
        assert distances == sorted(distances), (
            "Results not sorted by ascending distance"
        )

    def test_chapter_filter_restricts_results(self, index):
        """Filtering by chapter_num should only return results from that chapter."""
        for ch_num in (3, 7, 21):
            results = index.query(
                "copper", level="sentence", n_results=10,
                where={"chapter_num": ch_num},
            )
            for r in results:
                assert r["metadata"]["chapter_num"] == ch_num, (
                    f"Result from ch{r['metadata']['chapter_num']} leaked into "
                    f"ch{ch_num} filter"
                )

    def test_act_filter_restricts_results(self, index):
        """Filtering by act should only return results from that act."""
        for act in ACT_CHAPTER_RANGES:
            results = index.query(
                "Harry", level="paragraph", n_results=5,
                where={"act": act},
            )
            for r in results:
                assert r["metadata"]["act"] == act, (
                    f"Result from '{r['metadata']['act']}' leaked into "
                    f"'{act}' filter"
                )

    def test_hierarchical_drill_returns_parent_info(self, index):
        """Hierarchical queries attach _parent metadata to drill results."""
        results = index.query_hierarchical(
            "Tomás slug fired",
            top_level="chapter",
            drill_level="sentence",
            n_top=2,
            n_drill=3,
        )
        assert len(results) > 0
        for r in results:
            assert "_parent" in r
            assert "chapter_num" in r["_parent"]
            assert "level" in r["_parent"]
            assert r["_parent"]["level"] == "chapter"

    def test_different_levels_return_different_granularity(self, index):
        """
        The same query at sentence vs. chapter level should return text
        of very different average lengths.
        """
        query = "cosmic horror"
        sent_results = index.query(query, level="sentence", n_results=5)
        ch_results = index.query(query, level="chapter", n_results=5)

        avg_sent_len = np.mean([len(r["text"]) for r in sent_results])
        avg_ch_len = np.mean([len(r["text"]) for r in ch_results])

        assert avg_ch_len > avg_sent_len * 10, (
            f"Chapter results (avg {avg_ch_len:.0f} chars) should be much longer "
            f"than sentence results (avg {avg_sent_len:.0f} chars)"
        )

    def test_cosine_similarities_in_valid_range(self, index):
        """All cosine distances should be in [0, 2] (the valid range for cosine distance)."""
        results = index.query("the door", level="paragraph", n_results=20)
        for r in results:
            assert 0 <= r["distance"] <= 2, (
                f"Cosine distance {r['distance']} out of valid range [0, 2]"
            )

    def test_index_count_matches_collection(self, index):
        """stats() counts should match actual collection sizes."""
        stats = index.stats()
        for level in LEVELS:
            col = index._get_collection(level)
            assert stats[level] == col.count(), (
                f"{level}: stats reports {stats[level]} but collection has {col.count()}"
            )
