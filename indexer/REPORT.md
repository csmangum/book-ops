# Semantic Index: Current State & Next Steps

## 1. Index Overview

The index covers the full manuscript (Prologue through Epilogue, 26 files) at five granularity levels:

| Level | Units | Median Length | What It Captures |
|---|---|---|---|
| **Sentence** | 9,427 | 30 chars / 5 words | Individual statements, facts, dialogue lines |
| **Paragraph** | 1,796 | 193 chars / 35 words | Beats, exchanges, sensory moments |
| **Scene** | 56 | 6,550 chars / 1,158 words | Narrative segments (split on `---` markers) |
| **Chapter** | 26 | 16,799 chars / 2,898 words | Full chapter text |
| **Act** | 5 | 93,830 chars / 16,682 words | Concatenated chapter groups |

**Model**: `all-mpnet-base-v2` (768-dimensional embeddings, cosine distance, 384 token max)  
**Storage**: ChromaDB with HNSW index, persistent on disk (`.book_index/`)  
**Validation**: 93 tests passing across 3 test files

---

## 2. What Works Well

### Paragraph-level search is the sweet spot
The paragraph level consistently returns the most useful results. It captures enough context to be meaningful while staying focused enough to be precise. Queries about character voice, sensory atmosphere, and recurring motifs all perform well here:

- `"Connie choral fragment clinical voice"` → correctly surfaces the three key Connie-voice-shift passages (Ch 11, Ch 16, Ch 6) with similarities of 0.54–0.60
- `"rain and neon and chrome city streets"` → finds the city palette paragraphs (Ch 11, Ch 18, Ch 23) at 0.53–0.56
- `"tunnel underground darkness cold stone"` → retrieves tunnel sequences from the right chapters

### Chapter-level search works for thematic/structural queries
- `"the EMP Madrecitas copper network Tomás"` → Ch 13 (Nine Madrecitas) ranks first, followed by Ch 8 and Ch 22 — the three Tomás-centric chapters
- `"Connie's fall from human to fragment"` → Ch 15 (Connie's Last Human Moment) ranks first with a clear margin (0.60 vs 0.38)

### Hierarchical drill-down is effective
The two-stage search (find chapters, then drill into paragraphs/sentences within them) outperforms flat search for complex queries because it narrows the search space to narratively relevant territory first.

### Metadata filtering works cleanly
Chapter and act filters restrict results correctly. Useful for scoped editing queries like "find every mention of copper in Act I" or "all dialogue in Chapter 7."

### Embedding geometry is sound
All 11,310 embeddings are 768-dimensional, L2-normalized, free of NaN/Inf, and semantically distinct. The cosine similarity distribution is healthy (paragraph mean: 0.28, std: 0.15).

---

## 3. What Doesn't Work Well

### Sentence-level search is noisy
This is the weakest level. Three problems compound:

**a) Short/degenerate sentences pollute results.** NLTK's sentence tokenizer splits markdown italic markers (`*`) into standalone "sentences." There are 49 instances of `"*"` and 9 of `""*"` in the index. Another 602 sentences are single words (`"Steady."`, `"Quiet."`, `"Low."`). These are legitimate stylistic fragments but they embed poorly — a one-word sentence has almost no semantic signal, so it matches many queries by accident.

**b) Short sentences dominate nearest-neighbor results.** When you search for `"What color are Olive's eyes?"`, the top results are all `"Olive."` — single-word sentences that match on the name alone, not on the actual eye-color detail. The real answer (gray-green eyes) is buried lower because it lives in a longer paragraph where "eyes" is one detail among many.

**c) Exact duplicates cluster in results.** 33 sentence texts appear more than once across chapters (e.g., `"Nine days until the equinox."` x6, `"Not yet."` x5). These are intentional literary echoes, but they waste result slots by returning the same text from different locations.

### Scene-level coverage is uneven
14 of 26 chapters have no `---` scene breaks, so the scene level degenerates to a duplicate of the chapter level for those chapters. The other 12 chapters have 2–4 scenes each. This makes the scene level inconsistent — some "scenes" are 19 characters, others are 24,887.

### Act-level search is limited
Act texts are truncated to 1,500 characters (beginning + end) before embedding due to the model's 384-token window. This means the middle of long acts (Act II is 37,861 words) is invisible to the embedding. The act level is useful for rough structural queries but misses detail.

### Abstract/thematic queries underperform
Queries like `"sacrifice and loss cost of closing the door"` return low similarity scores (0.27–0.34 at scene level). The model embeds surface-level text well but struggles with abstract thematic concepts that the prose expresses indirectly. This is a known limitation of general-purpose sentence transformers with literary text.

---

## 4. Embedding Space Properties

| Level | Mean Sim | Std | Min | Median | Max |
|---|---|---|---|---|---|
| Sentence | 0.124 | 0.103 | -0.220 | 0.110 | 1.000 |
| Paragraph | 0.278 | 0.149 | -0.142 | 0.275 | 1.000 |
| Scene | 0.488 | 0.139 | 0.039 | 0.507 | 0.829 |
| Chapter | 0.499 | 0.132 | 0.072 | 0.517 | 0.739 |

Key observations:
- **Sentence-level similarity is low and dispersed** (mean 0.12) — this is expected; individual sentences are short and topically varied.
- **Chapter/scene similarity is high** (mean ~0.50) — the consistent voice, genre, and recurring motifs make chapters semantically close to each other. Intra-act similarity is measurably higher than inter-act (validated by tests).
- **Intra-chapter paragraph similarity only slightly exceeds inter-chapter** (ratio: 1.09). The novel's unified narrator means paragraphs from different chapters are stylistically similar. Nearest-neighbor analysis shows meaningful same-chapter clustering (well above random baseline), but the margin is modest.
- **92 near-duplicate embedding pairs** (sim > 0.98) exist at sentence level, mostly repeated short phrases across chapters.

---

## 5. Possible Next Steps

These are ordered roughly by impact-to-effort ratio.

### 5a. Filter out degenerate sentences before indexing
Strip sentences that are just markdown artifacts (`*`, `"*`) and optionally merge single-word sentences back into their surrounding context. This would eliminate ~650 low-signal units and significantly improve sentence-level search quality. **Impact: high. Effort: low.**

### 5b. Deduplicate exact-match sentences
When the same text appears in multiple chapters, index it once and store all locations as metadata. This prevents repeated phrases from monopolizing result slots. **Impact: medium. Effort: low.**

### 5c. Add a beat-level parser
Currently, "beats" within chapters that lack `---` markers are not segmented. A beat could be defined as a contiguous cluster of paragraphs (3–8 paragraphs) separated by topic shift, flashback boundaries, or dialogue/narration transitions. Options:
- Heuristic: split on blank-line-followed-by-time/location shifts, or on flashback markers (italics blocks, date references)
- Embedding-based: detect topic boundaries using sliding-window cosine similarity between consecutive paragraph embeddings (TextTiling approach)

This would fill the gap between paragraph (too short) and scene/chapter (too long) for chapters without explicit scene breaks. **Impact: high. Effort: medium.**

### 5d. Use a literary-tuned or asymmetric model
`all-mpnet-base-v2` is a general-purpose model trained on web/academic text. For abstract thematic queries ("sacrifice," "cosmic dread," "agency"), a model fine-tuned on literary text or one that supports query/document asymmetry (like `msmarco-distilbert-base-v4`) might capture thematic resonance better. You could also consider:
- `INSTRUCTOR` or `gte-large` models that accept task-specific prefixes
- Running a small LLM to generate chapter/scene summaries, then embedding the summaries instead of (or alongside) the raw text

**Impact: potentially high for thematic search. Effort: medium-high.**

### 5e. Add chapter/scene summaries as an embedding layer
Instead of truncating chapter text for embedding, generate short (~200 word) summaries using an LLM, then embed those. This gives the chapter and act levels access to the full narrative content rather than just the beginning and end. **Impact: medium for chapter/act search. Effort: medium.**

### 5f. Expose the index as a Python API for agents
The CLI is useful for interactive exploration, but the index's real power is as a tool for AI editing agents. Exposing `BookIndex.query()` as a callable tool would let agents answer continuity questions, check motif density, and find related passages during editing tasks. **Impact: high for the workflow. Effort: low (the API already exists, just needs integration).**

### 5g. Add keyword/BM25 hybrid search
Semantic search misses exact-match queries: searching for `"3:14 a.m."` works by proximity to the embedding of that string, not by literal text match. Adding a BM25 keyword index alongside the vector index — and combining scores — would handle both exact factual lookups and fuzzy thematic queries. ChromaDB doesn't support this natively, but `rank_bm25` or a simple inverted index could run in parallel. **Impact: high for continuity work. Effort: medium.**

---

## 6. Test Coverage Summary

| Test File | Tests | What It Validates |
|---|---|---|
| `test_parser.py` | 14 | Parser functions, chapter coverage, unit structure |
| `test_embedder.py` | 8 | Index build, search, filters, hierarchical drill |
| `test_validation.py` | 71 | 7 dimensions: structural integrity, text content, metadata, cross-level alignment, embedding geometry, semantic coherence, retrieval quality |
| **Total** | **93** | All passing |
