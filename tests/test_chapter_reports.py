import tempfile
import unittest
from pathlib import Path

from bookops.reports import render_chapter_standard_reports


class ChapterReportsTests(unittest.TestCase):
    def test_renders_continuity_style_and_lore_files(self) -> None:
        analysis = {
            "generated_findings": [
                {"rule_id": "HARD.TIMELINE.ANCHORS", "severity": "critical", "message": "x", "scope": "chapter:1"},
                {"rule_id": "SOFT.REPETITION.PHRASE_FAMILY", "severity": "medium", "message": "y", "scope": "chapter:1"},
            ]
        }
        lore_delta = {"proposals": [{"id": "p1", "target_lore_file": "lore/A.md", "reason": "test"}]}
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            paths = render_chapter_standard_reports(out, analysis, lore_delta=lore_delta, fmt="md")
            self.assertTrue((out / "continuity.md").exists())
            self.assertTrue((out / "style-audit.md").exists())
            self.assertTrue((out / "lore-delta.md").exists())
            self.assertIn("continuity_md", paths)


if __name__ == "__main__":
    unittest.main()
