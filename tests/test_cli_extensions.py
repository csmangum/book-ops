import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from bookops.cli import main
from bookops.config import bootstrap


class CliExtensionsTests(unittest.TestCase):
    def test_chapter_content_rules_settings_and_runs_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text(
                "# Chapter 1\n\nContent.\n",
                encoding="utf-8",
            )
            (root / "lore" / "Olive.md").write_text(
                "# Olive\n\nLore entry.\n",
                encoding="utf-8",
            )
            bootstrap(root)

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "chapter", "content", "1"])
            self.assertEqual(0, code)
            payload = json.loads(out.getvalue())
            self.assertEqual(1, payload["chapter_id"])
            self.assertIn("Content.", payload["content"])

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "rules", "get"])
            self.assertEqual(0, code)
            rules_payload = json.loads(out.getvalue())
            self.assertIn("rules", rules_payload)

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "settings", "get"])
            self.assertEqual(0, code)
            settings_payload = json.loads(out.getvalue())
            self.assertIn("paths", settings_payload)

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(
                    [
                        "--project",
                        str(root),
                        "settings",
                        "patch",
                        "--patch-json",
                        '{"project":{"chapters_dir":"chapters"}}',
                    ]
                )
            self.assertEqual(0, code)
            patched = json.loads(out.getvalue())
            self.assertEqual("chapters", patched["project"]["chapters_dir"])

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "run", "list"])
            self.assertEqual(0, code)
            runs_payload = json.loads(out.getvalue())
            self.assertEqual(0, runs_payload["count"])

            code = main(["--project", str(root), "run", "show", "missing-run"])
            self.assertEqual(1, code)

    def test_canon_graph_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text("# Chapter 1\n", encoding="utf-8")
            (root / "lore" / "Entity.md").write_text("# Entity\n", encoding="utf-8")
            bootstrap(root)

            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "canon", "graph"])
            self.assertEqual(0, code)
            payload = json.loads(out.getvalue())
            self.assertIn("nodes", payload)
            self.assertIn("edges", payload)


if __name__ == "__main__":
    unittest.main()
