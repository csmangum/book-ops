import tempfile
import unittest
from pathlib import Path

from bookops.config import bootstrap, load_runtime_config
from bookops.lore import apply_lore_proposal, approve_lore_proposal, generate_lore_delta
from bookops.utils import dump_json, dump_yaml


class LoreSyncTests(unittest.TestCase):
    def test_sync_blocks_when_precedence_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "lore" / "Thing.md").write_text("lore", encoding="utf-8")
            bootstrap(root)
            # disable precedence policy
            rules = {
                "version": 1,
                "policy": {"precedence": {"manuscript_over_lore": False}},
                "rules": [],
            }
            dump_yaml(root / "canon" / "rules.yaml", rules)
            dump_json(
                root / ".bookops" / "lore-proposals.json",
                {
                    "proposals": [
                        {
                            "id": "proposal-1",
                            "target_lore_file": "lore/Thing.md",
                            "status": "approved",
                        }
                    ]
                },
            )
            config = load_runtime_config(root)
            with self.assertRaises(ValueError):
                apply_lore_proposal(config, "proposal-1")

    def test_apply_requires_approval(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "lore" / "Thing.md").write_text("lore", encoding="utf-8")
            bootstrap(root)
            dump_json(
                root / ".bookops" / "lore-proposals.json",
                {
                    "proposals": [
                        {
                            "id": "proposal-1",
                            "target_lore_file": "lore/Thing.md",
                            "status": "pending_review",
                        }
                    ]
                },
            )
            config = load_runtime_config(root)
            with self.assertRaises(ValueError):
                apply_lore_proposal(config, "proposal-1")

            approve_lore_proposal(config, "proposal-1", reviewer="tester", note="ok")
            applied = apply_lore_proposal(config, "proposal-1")
            self.assertEqual("applied", applied["status"])

    def test_round_trip_delta_approve_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text(
                "# Chapter One\n\nThing appears in this chapter.\n",
                encoding="utf-8",
            )
            (root / "lore" / "Thing.md").write_text("Thing lore baseline", encoding="utf-8")
            bootstrap(root)
            config = load_runtime_config(root)

            delta = generate_lore_delta(config, chapter_id=1)
            self.assertGreaterEqual(len(delta.get("proposals", [])), 1)
            proposal_id = delta["proposals"][0]["id"]

            approved = approve_lore_proposal(config, proposal_id, reviewer="qa", note="round-trip")
            self.assertEqual("approved", approved["status"])

            applied = apply_lore_proposal(config, proposal_id)
            self.assertEqual("applied", applied["status"])
            lore_content = (root / "lore" / "Thing.md").read_text(encoding="utf-8")
            self.assertIn("BookOps sync", lore_content)

    def test_apply_rejects_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            bootstrap(root)
            dump_json(
                root / ".bookops" / "lore-proposals.json",
                {
                    "proposals": [
                        {
                            "id": "proposal-abs",
                            "target_lore_file": "/etc/passwd",
                            "status": "approved",
                        }
                    ]
                },
            )
            config = load_runtime_config(root)
            # absolute paths must be rejected before any file I/O
            with self.assertRaises(ValueError):
                apply_lore_proposal(config, "proposal-abs")

    def test_apply_rejects_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            bootstrap(root)
            dump_json(
                root / ".bookops" / "lore-proposals.json",
                {
                    "proposals": [
                        {
                            "id": "proposal-traversal",
                            "target_lore_file": "../../outside.md",
                            "status": "approved",
                        }
                    ]
                },
            )
            config = load_runtime_config(root)
            # paths with ".." segments that escape the project root must be rejected
            with self.assertRaises(ValueError):
                apply_lore_proposal(config, "proposal-traversal")


if __name__ == "__main__":
    unittest.main()
