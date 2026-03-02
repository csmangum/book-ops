"""Unit tests for bookops.vcs."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bookops.vcs import changed_paths_since


class TestChangedPathsSince(unittest.TestCase):
    def test_returns_empty_on_git_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = OSError("git not found")
                result = changed_paths_since(root, "origin/main")
                self.assertEqual(result, [])

    def test_returns_empty_on_nonzero_exit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = type("R", (), {"returncode": 1, "stdout": ""})()
                result = changed_paths_since(root, "origin/main")
                self.assertEqual(result, [])

    def test_returns_changed_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = type(
                    "R",
                    (),
                    {"returncode": 0, "stdout": "chapters/1_One.md\nlore/Harry.md\n"},
                )()
                result = changed_paths_since(root, "origin/main")
                self.assertEqual(result, ["chapters/1_One.md", "lore/Harry.md"])
