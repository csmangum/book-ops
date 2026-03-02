import tempfile
import unittest
from pathlib import Path

from bookops.reports import render_project_standard_reports


class ProjectReportsTests(unittest.TestCase):
    def test_renders_project_standard_reports(self) -> None:
        analysis_payload = {
            "metrics": {
                "timeline_markers": [{"chapter": 1, "day_markers": ["Day 1"], "date_markers": []}],
                "motifs": [{"chapter": 1, "copper": 2, "chrome": 1, "orchid": 0}],
            }
        }
        issues = [
            {"id": "ISSUE-1", "status": "open", "severity": "high", "message": "x"},
            {"id": "ISSUE-2", "status": "resolved", "severity": "low", "message": "y"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp)
            paths = render_project_standard_reports(out_dir, analysis_payload, issues, fmt="md")
            self.assertTrue((out_dir / "open-issues.md").exists())
            self.assertTrue((out_dir / "resolved-issues.md").exists())
            self.assertTrue((out_dir / "timeline-status.md").exists())
            self.assertTrue((out_dir / "motif-dashboard.md").exists())
            self.assertIn("open_issues_md", paths)


if __name__ == "__main__":
    unittest.main()
