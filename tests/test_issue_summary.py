import unittest

from bookops.issues import summarize_issues


class IssueSummaryTests(unittest.TestCase):
    def test_top_blockers_prioritize_severity(self) -> None:
        issues = [
            {"id": "ISSUE-low", "severity": "low", "status": "open", "message": "low", "scope": "project"},
            {"id": "ISSUE-critical", "severity": "critical", "status": "open", "message": "critical", "scope": "project"},
            {"id": "ISSUE-high", "severity": "high", "status": "open", "message": "high", "scope": "project"},
            {"id": "ISSUE-resolved", "severity": "critical", "status": "resolved", "message": "done", "scope": "project"},
        ]
        summary = summarize_issues(issues)
        self.assertEqual("ISSUE-critical", summary["top_blockers"][0]["id"])
        self.assertNotIn(
            "ISSUE-resolved",
            [item["id"] for item in summary["top_blockers"]],
        )


if __name__ == "__main__":
    unittest.main()
