import tempfile
import unittest
from pathlib import Path

from bookops.config import bootstrap, load_runtime_config
from bookops.pipeline import run_chapter_pipeline
from bookops.runlog import load_run_history


class PipelineRunHistoryTests(unittest.TestCase):
    def test_pipeline_records_run_history_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text(
                "# Chapter 1\n\nHarry walked into the room.\n",
                encoding="utf-8",
            )
            (root / "lore" / "Harry.md").write_text("# Harry\n", encoding="utf-8")
            bootstrap(root)
            config = load_runtime_config(root)

            payload = run_chapter_pipeline(config, chapter_id=1, output_format="json", strict=False)
            self.assertIn("run", payload)
            self.assertIn("run_id", payload["run"])

            history = load_run_history(config.run_history_file)
            self.assertEqual(1, len(history))
            self.assertEqual(payload["run"]["run_id"], history[0]["run_id"])


if __name__ == "__main__":
    unittest.main()
