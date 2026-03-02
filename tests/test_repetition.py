import unittest
from pathlib import Path

from bookops.analyzers import check_phrase_family_density
from bookops.ingest import ChapterDoc


class RepetitionAnalyzerTests(unittest.TestCase):
    def test_phrase_density_flags_over_threshold(self) -> None:
        lines = ["Not yet."] * 7
        chapter = ChapterDoc(
            path=Path("chapters/1_test.md"),
            chapter_number=1,
            title="One",
            lines=lines,
            text="\n".join(lines),
        )
        findings = check_phrase_family_density(chapter, warn_threshold=6)
        self.assertTrue(any(f.rule_id == "SOFT.REPETITION.PHRASE_FAMILY" for f in findings))


if __name__ == "__main__":
    unittest.main()
