import tempfile
import unittest
from pathlib import Path

from bookops.issues import apply_analysis_findings, load_issue_store, update_issue_status


class IssueLifecycleTests(unittest.TestCase):
    def test_issue_status_transitions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issue_path = Path(tmp) / "issues.json"
            findings = [
                {
                    "rule_id": "HARD.TIMELINE.ANCHORS",
                    "title": "Anchor mismatch",
                    "severity": "critical",
                    "message": "Mismatch",
                    "scope": "chapter:1",
                    "evidence": [],
                }
            ]
            store = apply_analysis_findings(issue_path, findings)
            issue_id = store["issues"][0]["id"]

            update_issue_status(issue_path, issue_id, "in_progress", note="started")
            store = load_issue_store(issue_path)
            self.assertEqual("in_progress", store["issues"][0]["status"])

            update_issue_status(issue_path, issue_id, "resolved", note="done")
            store = load_issue_store(issue_path)
            self.assertEqual("resolved", store["issues"][0]["status"])


if __name__ == "__main__":
    unittest.main()
