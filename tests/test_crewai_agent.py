"""Tests for CrewAI-backed agent integration."""

import os
import tempfile
import unittest
from pathlib import Path

from bookops.agents import run_agent
from bookops.config import bootstrap, load_runtime_config


class CrewAiAgentTests(unittest.TestCase):
    def test_run_agent_returns_stub_when_no_api_key(self) -> None:
        """Without OPENAI_API_KEY, run_agent falls back to stub."""
        key = os.environ.pop("OPENAI_API_KEY", None)
        anth_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "chapters").mkdir()
                (root / "lore").mkdir()
                (root / "chapters" / "1_Test.md").write_text("# Ch1\n\nDay 1. Harry walked.")
                (root / "lore" / "Harry.md").write_text("# Harry\n")
                bootstrap(root)
                config = load_runtime_config(root)

                result = run_agent("continuity_guardian", scope="chapter", scope_id=1, config=config)

                self.assertEqual("continuity_guardian", result.name)
                self.assertEqual([], result.findings)
                self.assertEqual([], result.proposals)
                self.assertEqual(0.62, result.confidence)
        finally:
            if key is not None:
                os.environ["OPENAI_API_KEY"] = key
            if anth_key is not None:
                os.environ["ANTHROPIC_API_KEY"] = anth_key

    def test_run_agent_accepts_config_none(self) -> None:
        """run_agent works with config=None (stub path)."""
        result = run_agent("line_editor", scope="chapter", scope_id=1, config=None)
        self.assertEqual("line_editor", result.name)
        self.assertEqual([], result.findings)
