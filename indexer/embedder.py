"""
Embedding engine and ChromaDB storage for the multi-level semantic index.

Uses SentenceTransformers for encoding and ChromaDB for storage/retrieval.
Handles the token-length limits of the embedding model by truncating
or summarizing long texts at the chapter and act levels.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import chromadb
from filelock import FileLock
from sentence_transformers import SentenceTransformer

from .parser import TextUnit, parse_all_chapters, build_act_units

INDEX_DIR = Path(__file__).resolve().parent.parent / ".book_index"
MODEL_NAME = "all-mpnet-base-v2"
MAX_SEQ_TOKENS = 384  # model max is 384 tokens; ~1500 chars is safe


def _truncate_for_embedding(text: str, max_chars: int = 1500) -> str:
    """For long texts (chapters, acts), take beginning + end to stay in token budget."""
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n[...]\n" + text[-half:]


def _sanitize_metadata(meta: dict) -> dict:
    """Ensure metadata values are ChromaDB-compatible (str, int, float, bool)."""
    allowed = (str, int, float, bool)
    out = {}
    for k, v in meta.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, allowed):
            out[k] = v
        else:
            out[k] = str(v)
    return out


def _content_hash(units: list[TextUnit]) -> str:
    """Hash of all unit texts and key metadata to detect when re-indexing is needed."""
    h = hashlib.sha256()
    for u in units:
        h.update(u.text.encode("utf-8"))
        for val in (u.act, str(u.chapter_num), str(u.scene_idx), str(u.paragraph_idx), str(u.sentence_idx)):
            h.update(val.encode("utf-8"))
            h.update(b"\x00")
    return h.hexdigest()[:16]


class BookIndex:
    """Multi-level semantic index for the manuscript."""

    def __init__(self, model_name: str = MODEL_NAME, persist_dir: Path | None = None):
        self.persist_dir = persist_dir or INDEX_DIR
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._model_name = model_name
        self._model: SentenceTransformer | None = None
        self.client = chromadb.PersistentClient(path=str(self.persist_dir / "chromadb"))
        self._collections: dict[str, chromadb.Collection] = {}

    def _get_model(self) -> SentenceTransformer:
        """Lazy-load the embedding model on first use."""
        if self._model is None:
            self._model = SentenceTransformer(self._model_name)
        return self._model

    def _get_collection(self, level: str) -> chromadb.Collection:
        if level not in self._collections:
            self._collections[level] = self.client.get_or_create_collection(
                name=f"book_{level}",
                metadata={"hnsw:space": "cosine"},
            )
        return self._collections[level]

    def build(self, force: bool = False) -> dict[str, int]:
        """Parse the manuscript and build/rebuild the index. Returns counts per level."""
        all_units = parse_all_chapters()
        act_units = build_act_units(all_units)
        all_units.extend(act_units)

        content_hash = _content_hash(all_units)
        hash_file = self.persist_dir / "content_hash"
        if not force and hash_file.exists() and hash_file.read_text().strip() == content_hash:
            counts = {}
            for level in ("sentence", "paragraph", "scene", "chapter", "act"):
                col = self._get_collection(level)
                counts[level] = col.count()
            return counts

        lock = FileLock(self.persist_dir / "build.lock")
        with lock:
            if not force and hash_file.exists() and hash_file.read_text().strip() == content_hash:
                counts = {}
                for level in ("sentence", "paragraph", "scene", "chapter", "act"):
                    col = self._get_collection(level)
                    counts[level] = col.count()
                return counts

            by_level: dict[str, list[TextUnit]] = {}
            for u in all_units:
                by_level.setdefault(u.level, []).append(u)

            counts = {}
            for level, units in by_level.items():
                col = self._get_collection(level)
                # Clear existing data by deleting and recreating
                self.client.delete_collection(f"book_{level}")
                self._collections.pop(level, None)
                col = self._get_collection(level)

                texts = []
                for u in units:
                    t = u.text
                    if level in ("chapter", "act"):
                        t = _truncate_for_embedding(t)
                    texts.append(t)

                batch_size = 64
                for i in range(0, len(units), batch_size):
                    batch_units = units[i : i + batch_size]
                    batch_texts = texts[i : i + batch_size]
                    embeddings = self._get_model().encode(batch_texts, show_progress_bar=False).tolist()
                    col.add(
                        ids=[u.id for u in batch_units],
                        embeddings=embeddings,
                        documents=batch_texts,
                        metadatas=[_sanitize_metadata(u.metadata) for u in batch_units],
                    )

                counts[level] = col.count()

            hash_file.write_text(content_hash)
            return counts

    def query(
        self,
        text: str,
        level: str = "paragraph",
        n_results: int = 10,
        where: dict | None = None,
    ) -> list[dict]:
        """
        Semantic search at a given level.

        Args:
            text: The query string.
            level: One of "sentence", "paragraph", "scene", "chapter", "act".
            n_results: Number of results to return.
            where: Optional ChromaDB metadata filter, e.g. {"act": "Act I – The Hire"}
                   or {"chapter_num": 7}.

        Returns:
            List of result dicts with keys: id, text, metadata, distance.
        """
        col = self._get_collection(level)
        if col.count() == 0:
            return []

        query_embedding = self._get_model().encode(text).tolist()
        kwargs: dict = {
            "query_embeddings": [query_embedding],
            "n_results": min(n_results, col.count()),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = col.query(**kwargs)

        output = []
        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            })
        return output

    def query_hierarchical(
        self,
        text: str,
        top_level: str = "chapter",
        drill_level: str = "paragraph",
        n_top: int = 3,
        n_drill: int = 5,
    ) -> list[dict]:
        """
        Two-stage hierarchical search: find top-level matches, then drill down.

        Example: find the 3 most relevant chapters, then the 5 best paragraphs
        within those chapters.
        """
        top_results = self.query(text, level=top_level, n_results=n_top)
        all_drill = []

        for tr in top_results:
            meta = tr["metadata"]
            if top_level == "act":
                where_filter = {"act": meta["act"]}
            elif top_level == "chapter":
                where_filter = {"chapter_num": meta["chapter_num"]}
            elif top_level == "scene":
                where_filter = {
                    "chapter_num": meta["chapter_num"],
                    "scene_idx": meta["scene_idx"],
                }
            elif top_level == "paragraph":
                where_filter = {
                    "chapter_num": meta["chapter_num"],
                    "scene_idx": meta["scene_idx"],
                    "paragraph_idx": meta["paragraph_idx"],
                }
            else:  # sentence
                where_filter = {
                    "chapter_num": meta["chapter_num"],
                    "scene_idx": meta["scene_idx"],
                    "paragraph_idx": meta["paragraph_idx"],
                    "sentence_idx": meta["sentence_idx"],
                }

            drill_results = self.query(
                text,
                level=drill_level,
                n_results=n_drill,
                where=where_filter,
            )
            for dr in drill_results:
                dr["_parent"] = {
                    "level": top_level,
                    "chapter_num": tr["metadata"]["chapter_num"],
                    "chapter_title": tr["metadata"]["chapter_title"],
                    "distance": tr["distance"],
                }
            all_drill.extend(drill_results)

        all_drill.sort(key=lambda x: x["distance"])
        return all_drill[:n_drill * n_top]

    def stats(self) -> dict[str, int]:
        counts = {}
        for level in ("sentence", "paragraph", "scene", "chapter", "act"):
            col = self._get_collection(level)
            counts[level] = col.count()
        return counts
