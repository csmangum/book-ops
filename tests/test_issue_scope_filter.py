import unittest

from bookops.issues import filter_issues


class IssueScopeFilterTests(unittest.TestCase):
    def test_scope_project_returns_all(self) -> None:
        store = {
            "issues": [
                {"id": "1", "scope": "chapter:1"},
                {"id": "2", "scope": "project"},
            ]
        }
        issues = filter_issues(store, scope="project")
        self.assertEqual(2, len(issues))

    def test_scope_chapter_returns_chapter_only(self) -> None:
        store = {
            "issues": [
                {"id": "1", "scope": "chapter:1"},
                {"id": "2", "scope": "project"},
            ]
        }
        issues = filter_issues(store, scope="chapter")
        self.assertEqual(1, len(issues))
        self.assertEqual("1", issues[0]["id"])


if __name__ == "__main__":
    unittest.main()
