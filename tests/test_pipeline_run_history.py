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

    def test_pipeline_writes_agent_results_and_decision_log_includes_agents(self) -> None:
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
            self.assertIn("agent_results", payload)
            self.assertEqual(4, len(payload["agent_results"]))

            agent_results_path = config.output_dir / "chapter-1" / "agent-results.json"
            self.assertTrue(agent_results_path.exists())
            import json
            agent_data = json.loads(agent_results_path.read_text())
            self.assertEqual(4, len(agent_data))

            decision_log_path = config.output_dir / "chapter-1" / "decision-log.json"
            self.assertTrue(decision_log_path.exists())
            decision_data = json.loads(decision_log_path.read_text())
            self.assertIn("agent_summaries", decision_data)
            self.assertEqual(4, len(decision_data["agent_summaries"]))


if __name__ == "__main__":
    unittest.main()
