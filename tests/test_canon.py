"""Unit tests for bookops.canon."""
import tempfile
import unittest
from pathlib import Path

from bookops.canon import (
    build_canon,
    diff_canon,
    load_snapshot,
    save_canon_snapshot,
    validate_canon_payload,
)
from bookops.config import RuntimeConfig, load_runtime_config


class TestValidateCanonPayload(unittest.TestCase):
    def test_valid_payload_returns_empty(self) -> None:
        payload = {
            "chapter_index": [],
            "timeline": {"chapter_days": {}, "dates": [], "times": []},
            "entities": [],
        }
        self.assertEqual(validate_canon_payload(payload), [])

    def test_missing_chapter_index(self) -> None:
        payload = {"timeline": {"chapter_days": {}}, "entities": []}
        self.assertIn("Missing chapter_index", validate_canon_payload(payload))

    def test_missing_timeline(self) -> None:
        payload = {"chapter_index": [], "entities": []}
        self.assertIn("Missing timeline", validate_canon_payload(payload))

    def test_missing_chapter_days(self) -> None:
        payload = {"chapter_index": [], "timeline": {}, "entities": []}
        self.assertIn("Missing timeline.chapter_days", validate_canon_payload(payload))

    def test_missing_entities(self) -> None:
        payload = {"chapter_index": [], "timeline": {"chapter_days": {}}}
        self.assertIn("Missing entities", validate_canon_payload(payload))


class TestDiffCanon(unittest.TestCase):
    def test_changed_days(self) -> None:
        from_p = {"timeline": {"chapter_days": {"1": 5, "2": 10}}, "entities": []}
        to_p = {"timeline": {"chapter_days": {"1": 6, "2": 10}}, "entities": []}
        result = diff_canon(from_p, to_p)
        self.assertEqual(result["changed_days"]["1"], {"from": 5, "to": 6})

    def test_entities_added_removed(self) -> None:
        from_p = {"timeline": {"chapter_days": {}}, "entities": [{"id": "a"}]}
        to_p = {"timeline": {"chapter_days": {}}, "entities": [{"id": "b"}]}
        result = diff_canon(from_p, to_p)
        self.assertEqual(result["entities_added"], ["b"])
        self.assertEqual(result["entities_removed"], ["a"])


class TestLoadSnapshot(unittest.TestCase):
    def test_loads_valid_json(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write('{"key": "value"}')
            path = Path(f.name)
        try:
            result = load_snapshot(path)
            self.assertEqual(result, {"key": "value"})
        finally:
            path.unlink()

    def test_returns_empty_for_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = load_snapshot(Path(tmp) / "nonexistent.json")
            self.assertEqual(result, {})


class TestBuildCanonAndSave(unittest.TestCase):
    def test_build_and_save_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Test\n\nDay 5 was cold.\n")
            (root / "lore" / "Harry.md").write_text("# Harry\n")
            config = load_runtime_config(project_root=root, output_dir=root / "reports")
            payload = build_canon(config)
            self.assertIn("chapter_index", payload)
            self.assertIn("timeline", payload)
            self.assertIn("entities", payload)
            self.assertEqual(len(payload["chapter_index"]), 1)
            snapshot_path = save_canon_snapshot(config, payload)
            self.assertTrue(snapshot_path.exists())
            loaded = load_snapshot(config.canon_latest)
            self.assertEqual(len(loaded["chapter_index"]), len(payload["chapter_index"]))
            self.assertEqual(loaded["chapter_index"][0]["chapter_number"], 1)
