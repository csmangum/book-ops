import tempfile
import unittest
from pathlib import Path

from bookops.indexing import rebuild_index, index_status


class IndexingTests(unittest.TestCase):
    def test_rebuild_excludes_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "reports").mkdir()
            (root / ".bookops").mkdir()
            (root / ".git").mkdir()

            (root / "chapters" / "1_Test.md").write_text("# Chapter\n\nHello\n", encoding="utf-8")
            (root / "reports" / "report.md").write_text("ignore", encoding="utf-8")
            (root / ".bookops" / "internal.md").write_text("ignore", encoding="utf-8")
            (root / ".git" / "meta.md").write_text("ignore", encoding="utf-8")

            payload = rebuild_index(root, root / ".bookops" / "index")
            paths = [item["path"] for item in payload["symbolic"]]
            self.assertEqual(1, payload["file_count"])
            self.assertEqual(["chapters/1_Test.md"], paths)

    def test_rebuild_produces_stable_corpus_hash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Chapter\n\nHello\n", encoding="utf-8")
            index_dir = root / ".bookops" / "index"

            first = rebuild_index(root, index_dir)
            second = rebuild_index(root, index_dir)
            self.assertEqual(first["corpus_hash"], second["corpus_hash"])
            self.assertEqual(first["file_count"], second["file_count"])

    def test_index_status_reports_metadata_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            index_dir = root / ".bookops" / "index"
            status_before = index_status(index_dir)
            self.assertFalse(status_before["symbolic_exists"])

            (root / "chapters").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Chapter\n", encoding="utf-8")
            payload = rebuild_index(root, index_dir)

            status_after = index_status(index_dir)
            self.assertTrue(status_after["symbolic_exists"])
            self.assertEqual(payload["file_count"], status_after["file_count"])
            self.assertEqual(payload["corpus_hash"], status_after["corpus_hash"])
            self.assertEqual("stub", status_after["semantic_status"])


if __name__ == "__main__":
    unittest.main()
