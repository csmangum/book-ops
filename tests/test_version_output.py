import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from bookops.cli import main


class VersionOutputTests(unittest.TestCase):
    def test_version_includes_agent_pack_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["--project", str(root), "version"])
            self.assertEqual(0, code)
            payload = json.loads(out.getvalue())
            self.assertIn("agent_pack_version", payload)
            self.assertIn("agent_count", payload)


if __name__ == "__main__":
    unittest.main()
