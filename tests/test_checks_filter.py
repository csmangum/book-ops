import tempfile
import unittest
from pathlib import Path

from bookops.config import bootstrap, load_runtime_config
from bookops.analyzers import run_chapter_analysis


class ChecksFilterTests(unittest.TestCase):
    def test_run_chapter_analysis_honors_requested_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text(
                "# Chapter One\n\nThe way the way the way the way the way the way.\n",
                encoding="utf-8",
            )
            bootstrap(root)
            config = load_runtime_config(root)
            payload = run_chapter_analysis(config, 1, checks={"repetition"})
            self.assertEqual(["repetition"], payload["checks"])
            # Ensure we only run configured check family and avoid hard-rule findings.
            self.assertTrue(
                all(str(item["rule_id"]).startswith("SOFT.REPETITION") for item in payload["generated_findings"])
            )


if __name__ == "__main__":
    unittest.main()
