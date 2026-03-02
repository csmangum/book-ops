import unittest
from pathlib import Path

from bookops.ingest import ChapterDoc
from bookops.lore import select_chapters_for_lore_delta


class LoreDeltaSelectionTests(unittest.TestCase):
    def test_selects_only_changed_chapters_when_filter_present(self) -> None:
        chapters = [
            ChapterDoc(path=Path("/repo/chapters/1_A.md"), chapter_number=1, title="A", lines=[], text=""),
            ChapterDoc(path=Path("/repo/chapters/2_B.md"), chapter_number=2, title="B", lines=[], text=""),
        ]
        selected = select_chapters_for_lore_delta(
            chapters,
            chapter_id=None,
            changed_chapter_paths={"chapters/2_B.md"},
            project_root=Path("/repo"),
        )
        self.assertEqual(1, len(selected))
        self.assertEqual(2, selected[0].chapter_number)


if __name__ == "__main__":
    unittest.main()
