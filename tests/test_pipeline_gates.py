import unittest

from bookops.gates import evaluate_gate


class PipelineGateTests(unittest.TestCase):
    def test_gate_fails_with_open_critical(self) -> None:
        issues = [
            {
                "id": "ISSUE-1",
                "severity": "critical",
                "status": "open",
                "scope": "chapter:1",
            }
        ]
        result = evaluate_gate(issues, fail_on_severities=["critical"], strict=False)
        self.assertEqual("fail", result.status)
        self.assertEqual(["ISSUE-1"], result.blocking_issue_ids)


if __name__ == "__main__":
    unittest.main()
