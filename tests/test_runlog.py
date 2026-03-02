import tempfile
import unittest
from pathlib import Path

from bookops.runlog import write_decision_log


class RunlogTests(unittest.TestCase):
    def test_writes_decision_log_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            result = write_decision_log(
                output_dir=out,
                scope="chapter:1",
                gate={"status": "pass", "message": "ok"},
                analysis={"generated_findings": []},
                lore_delta={"proposals": []},
            )
            self.assertTrue((out / "decision-log.md").exists())
            self.assertTrue((out / "decision-log.json").exists())
            self.assertIn("md", result)


if __name__ == "__main__":
    unittest.main()
