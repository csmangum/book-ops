import tempfile
import unittest
from pathlib import Path

from bookops.runlog import append_run_history, get_run_entry, load_run_history, write_decision_log


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
            self.assertIn("run_id", result)

    def test_appends_and_reads_run_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            history_path = root / "runs.json"
            report_dir = root / "reports" / "chapter-1"
            report_dir.mkdir(parents=True, exist_ok=True)
            decision_log = report_dir / "decision-log.json"
            decision_log.write_text("{}", encoding="utf-8")

            append_run_history(
                history_path,
                run_id="run-123",
                scope="chapter:1",
                gate={"status": "pass"},
                report_dir=report_dir,
                decision_log_json=decision_log,
            )
            runs = load_run_history(history_path)
            self.assertEqual(1, len(runs))
            self.assertEqual("run-123", runs[0]["run_id"])
            self.assertEqual("pass", runs[0]["gate"])
            self.assertIsNotNone(get_run_entry(history_path, "run-123"))


if __name__ == "__main__":
    unittest.main()
