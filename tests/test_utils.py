"""Unit tests for bookops.utils."""
import tempfile
import unittest
from pathlib import Path

from bookops.utils import (
    chapter_number_from_name,
    dump_json,
    ensure_dir,
    iter_markdown_files,
    load_json,
    read_text,
    sha256_file,
    sorted_chapter_paths,
    write_text,
)


class TestChapterNumberFromName(unittest.TestCase):
    def test_numeric_prefix(self) -> None:
        self.assertEqual(chapter_number_from_name("1_Opening.md"), 1)
        self.assertEqual(chapter_number_from_name("42_The_Answer.md"), 42)

    def test_non_numeric_prefix(self) -> None:
        self.assertEqual(chapter_number_from_name("intro.md"), 10_000)
        self.assertEqual(chapter_number_from_name("prologue.md"), 10_000)


class TestSortedChapterPaths(unittest.TestCase):
    def test_sorts_by_chapter_number(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "3_Three.md").write_text("# Three")
            (root / "1_One.md").write_text("# One")
            (root / "2_Two.md").write_text("# Two")
            paths = sorted_chapter_paths(root)
            self.assertEqual([p.name for p in paths], ["1_One.md", "2_Two.md", "3_Three.md"])


class TestSha256File(unittest.TestCase):
    def test_stable_hash(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("hello world")
            path = Path(f.name)
        try:
            h1 = sha256_file(path)
            h2 = sha256_file(path)
            self.assertEqual(h1, h2)
            self.assertEqual(len(h1), 64)
        finally:
            path.unlink()


class TestJsonRoundTrip(unittest.TestCase):
    def test_dump_load_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.json"
            payload = {"a": 1, "b": [2, 3], "c": {"nested": True}}
            dump_json(path, payload)
            loaded = load_json(path)
            self.assertEqual(loaded, payload)

    def test_load_missing_returns_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_json(Path(tmp) / "nonexistent.json", default={"fallback": True})
            self.assertEqual(result, {"fallback": True})


class TestEnsureDir(unittest.TestCase):
    def test_creates_nested_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "a" / "b" / "c"
            ensure_dir(target)
            self.assertTrue(target.is_dir())


class TestReadWriteText(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "file.txt"
            content = "line1\nline2"
            write_text(path, content)
            self.assertEqual(read_text(path), content)


class TestIterMarkdownFiles(unittest.TestCase):
    def test_collects_md_files_excludes_git(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / ".git").mkdir()
            (root / "chapters" / "1_One.md").write_text("# One")
            (root / ".git" / "config.md").write_text("git")
            files = iter_markdown_files(root)
            paths = [str(p.relative_to(root)) for p in files]
            self.assertIn("chapters/1_One.md", paths)
            self.assertNotIn(".git/config.md", paths)
