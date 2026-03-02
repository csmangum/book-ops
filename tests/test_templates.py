import unittest

from bookops.config import DEFAULT_RULES
from bookops.templates import apply_template_to_rules, list_templates


class TemplateTests(unittest.TestCase):
    def test_templates_list_contains_expected(self) -> None:
        names = list_templates()
        self.assertIn("noir", names)
        self.assertIn("epic_fantasy", names)
        self.assertIn("thriller", names)

    def test_noir_template_overrides_motif_thresholds(self) -> None:
        payload = apply_template_to_rules(DEFAULT_RULES, "noir")
        motif_rule = next(r for r in payload["rules"] if r["id"] == "SOFT.MOTIF.DENSITY_BALANCE")
        self.assertEqual(
            10,
            motif_rule["params"]["motifs"]["copper"]["warn_per_chapter"],
        )


if __name__ == "__main__":
    unittest.main()
