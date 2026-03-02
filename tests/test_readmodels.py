"""Unit tests for bookops.readmodels."""
import tempfile
import unittest
from pathlib import Path

from bookops.config import load_runtime_config
from bookops.readmodels import (
    get_chapter_content,
    get_canon_graph,
    get_rules_payload,
    get_settings_payload,
    list_runs,
    patch_settings_payload,
)


class TestGetChapterContent(unittest.TestCase):
    def test_returns_chapter_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Test\n\nHello world.")
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            result = get_chapter_content(config, 1)
            self.assertEqual(result["chapter_id"], 1)
            self.assertIn("Hello world", result["content"])
            self.assertTrue(result["title"])  # title from first non-header line or stem fallback

    def test_raises_for_missing_chapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            with self.assertRaises(ValueError) as ctx:
                get_chapter_content(config, 99)
            self.assertIn("99", str(ctx.exception))


class TestGetCanonGraph(unittest.TestCase):
    def test_returns_graph_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Test\n")
            (root / "lore" / "Harry.md").write_text("# Harry\n")
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            result = get_canon_graph(config)
            self.assertIn("nodes", result)
            self.assertIn("edges", result)
            self.assertIn("node_count", result)
            self.assertGreaterEqual(result["node_count"], 1)


class TestGetRulesPayload(unittest.TestCase):
    def test_returns_rules_from_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".bookops").mkdir()
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            result = get_rules_payload(config)
            self.assertIn("rules", result)


class TestSettingsPayload(unittest.TestCase):
    def test_get_returns_default_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".bookops").mkdir()
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            result = get_settings_payload(config)
            self.assertIsInstance(result, dict)

    def test_patch_merges_and_persists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".bookops").mkdir()
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            patched = patch_settings_payload(
                config, {"project": {"chapters_dir": "my_chapters"}}
            )
            self.assertEqual(patched["project"]["chapters_dir"], "my_chapters")
            reloaded = get_settings_payload(config)
            self.assertEqual(reloaded["project"]["chapters_dir"], "my_chapters")


class TestListRuns(unittest.TestCase):
    def test_returns_empty_when_no_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".bookops").mkdir()
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            result = list_runs(config)
            self.assertEqual(result, [])
