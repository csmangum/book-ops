import unittest
from pathlib import Path

from bookops.analyzers import check_timeline_day_sequence
from bookops.ingest import ChapterDoc


class TimelineAnalyzerTests(unittest.TestCase):
    def test_detects_day_regression(self) -> None:
        chapter_2 = ChapterDoc(
            path=Path("chapters/2_test.md"),
            chapter_number=2,
            title="Two",
            lines=["Day 2.", "Something happens."],
            text="Day 2.\nSomething happens.\n",
        )
        chapter_3 = ChapterDoc(
            path=Path("chapters/3_test.md"),
            chapter_number=3,
            title="Three",
            lines=["Day 1.", "Backwards drift."],
            text="Day 1.\nBackwards drift.\n",
        )
        findings = check_timeline_day_sequence([chapter_2, chapter_3])
        self.assertEqual(1, len(findings))
        self.assertEqual("HARD.TIMELINE.DAY_SEQUENCE", findings[0].rule_id)


if __name__ == "__main__":
    unittest.main()
