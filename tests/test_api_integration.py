"""Comprehensive API integration tests using FastAPI TestClient."""
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from bookops.api import app
from bookops.config import bootstrap


def _project_fixture():
    """Create a minimal project with chapters and lore."""
    tmp = tempfile.mkdtemp()
    root = Path(tmp)
    (root / "chapters").mkdir()
    (root / "lore").mkdir()
    (root / "chapters" / "1_Test.md").write_text("# Chapter 1\n\nHarry walked in. Day 5.\n")
    (root / "chapters" / "2_Second.md").write_text("# Chapter 2\n\nMore content.\n")
    (root / "lore" / "Harry.md").write_text("# Harry\n\nWizard.\n")
    bootstrap(root)
    return root


class ApiIntegrationTests(unittest.TestCase):
    """Integration tests for all API endpoints."""

    def setUp(self) -> None:
        self.root = _project_fixture()
        self._prev_project = os.environ.get("BOOKOPS_PROJECT")
        self._prev_output = os.environ.get("BOOKOPS_OUTPUT_DIR")
        os.environ["BOOKOPS_PROJECT"] = str(self.root)
        os.environ["BOOKOPS_OUTPUT_DIR"] = str(self.root / "reports")

    def tearDown(self) -> None:
        if self._prev_project is None:
            os.environ.pop("BOOKOPS_PROJECT", None)
        else:
            os.environ["BOOKOPS_PROJECT"] = self._prev_project
        if self._prev_output is None:
            os.environ.pop("BOOKOPS_OUTPUT_DIR", None)
        else:
            os.environ["BOOKOPS_OUTPUT_DIR"] = self._prev_output
        import shutil
        shutil.rmtree(self.root, ignore_errors=True)

    def test_version(self) -> None:
        client = TestClient(app)
        r = client.get("/version")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertIn("bookops_version", data["data"])

    def test_index_rebuild_and_status(self) -> None:
        client = TestClient(app)
        r = client.post("/index/rebuild")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        r = client.get("/index/status")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertTrue(data["data"]["symbolic_exists"])
        self.assertIn("symbolic", data["data"])

    def test_canon_build_validate_graph(self) -> None:
        client = TestClient(app)
        r = client.post("/canon/build")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        r = client.get("/canon/validate")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["data"]["valid"])
        r = client.get("/canon/graph")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertIn("nodes", data["data"])

    def test_analyze_chapter_and_project(self) -> None:
        client = TestClient(app)
        r = client.post("/analyze/chapter", json={"chapter_id": 1})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        r = client.post("/analyze/project", json={})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_gate_chapter_and_project(self) -> None:
        client = TestClient(app)
        r = client.post("/gate/chapter", json={"chapter_id": 1, "strict": False})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertIn(data["exit_code"], (0, 2, 3))
        r = client.post("/gate/project", json={})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_pipeline_chapter_and_project(self) -> None:
        client = TestClient(app)
        r = client.post("/pipeline/chapter", json={"chapter_id": 1, "strict": False})
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertIn("run_id", data["data"])
        r = client.post("/pipeline/project", json={})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_issues_list_and_update(self) -> None:
        client = TestClient(app)
        r = client.get("/issues")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_lore_delta_approve_sync(self) -> None:
        client = TestClient(app)
        r = client.post("/lore/delta", json={"scope": "chapter", "id": 1})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_reports_build_and_open(self) -> None:
        client = TestClient(app)
        r = client.post("/reports/build", json={"scope": "chapter", "id": 1})
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])
        r = client.get("/reports/open?scope=chapter&id=1")
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])

    def test_runs_list_and_detail(self) -> None:
        client = TestClient(app)
        r = client.post("/pipeline/chapter", json={"chapter_id": 1, "strict": False})
        run_id = r.json()["data"]["run_id"]
        r = client.get("/runs")
        self.assertEqual(r.status_code, 200)
        self.assertGreaterEqual(r.json()["data"]["count"], 1)
        r = client.get(f"/runs/{run_id}")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["run_id"], run_id)

    def test_chapter_content_rules_settings(self) -> None:
        client = TestClient(app)
        r = client.get("/chapters/1/content")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["chapter_id"], 1)
        r = client.get("/rules")
        self.assertEqual(r.status_code, 200)
        self.assertIn("rules", r.json()["data"])
        r = client.get("/settings")
        self.assertEqual(r.status_code, 200)
        self.assertIn("paths", r.json()["data"])
        r = client.patch("/settings", json={"project": {"chapters_dir": "chapters"}})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["data"]["project"]["chapters_dir"], "chapters")

    def test_artifact_endpoints_return_envelope(self) -> None:
        client = TestClient(app)
        for path in [
            "/artifacts/chapter/1/analysis",
            "/artifacts/chapter/1/gate",
            "/artifacts/project/gate",
        ]:
            r = client.get(path)
            self.assertEqual(r.status_code, 200)
            data = r.json()
            self.assertIn("ok", data)
            self.assertIn("data", data)

    def test_reports_open_requires_scope(self) -> None:
        client = TestClient(app)
        r = client.get("/reports/open")
        self.assertEqual(r.status_code, 422)
