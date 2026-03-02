import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from bookops.api import app
from bookops.config import bootstrap


class ApiExtensionsTests(unittest.TestCase):
    def test_new_api_endpoints_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "chapters").mkdir()
            (root / "lore").mkdir()
            (root / "chapters" / "1_Test.md").write_text(
                "# Chapter 1\n\nHarry walked in.\n",
                encoding="utf-8",
            )
            (root / "lore" / "Harry.md").write_text("# Harry\n", encoding="utf-8")
            bootstrap(root)

            previous_project = os.environ.get("BOOKOPS_PROJECT")
            previous_output_dir = os.environ.get("BOOKOPS_OUTPUT_DIR")
            os.environ["BOOKOPS_PROJECT"] = str(root)
            os.environ["BOOKOPS_OUTPUT_DIR"] = "reports"
            try:
                client = TestClient(app)

                chapter_content = client.get("/chapters/1/content").json()
                self.assertTrue(chapter_content["ok"])
                self.assertEqual(1, chapter_content["data"]["chapter_id"])

                settings = client.get("/settings").json()
                self.assertTrue(settings["ok"])
                self.assertIn("paths", settings["data"])

                patched = client.patch(
                    "/settings",
                    json={"project": {"chapters_dir": "chapters"}},
                ).json()
                self.assertTrue(patched["ok"])
                self.assertEqual("chapters", patched["data"]["project"]["chapters_dir"])

                rules = client.get("/rules").json()
                self.assertTrue(rules["ok"])
                self.assertIn("rules", rules["data"])

                graph = client.get("/canon/graph").json()
                self.assertTrue(graph["ok"])
                self.assertIn("nodes", graph["data"])

                pipeline = client.post(
                    "/pipeline/chapter",
                    json={"chapter_id": 1, "strict": False},
                ).json()
                self.assertTrue(pipeline["ok"])
                run_id = pipeline["data"]["run_id"]
                self.assertTrue(run_id)

                runs = client.get("/runs").json()
                self.assertTrue(runs["ok"])
                self.assertGreaterEqual(runs["data"]["count"], 1)

                run_detail = client.get(f"/runs/{run_id}").json()
                self.assertTrue(run_detail["ok"])
                self.assertEqual(run_id, run_detail["data"]["run_id"])
            finally:
                if previous_project is None:
                    os.environ.pop("BOOKOPS_PROJECT", None)
                else:
                    os.environ["BOOKOPS_PROJECT"] = previous_project
                if previous_output_dir is None:
                    os.environ.pop("BOOKOPS_OUTPUT_DIR", None)
                else:
                    os.environ["BOOKOPS_OUTPUT_DIR"] = previous_output_dir


if __name__ == "__main__":
    unittest.main()
