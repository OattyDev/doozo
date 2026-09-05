import tempfile
import unittest
from pathlib import Path

from astra_benchmark import fingerprint, init_repo, rotate
from astra_tasks import CASE_BY_ID


class AstraBenchmarkTests(unittest.TestCase):
    def test_arm_order_rotates_without_omitting_an_arm(self):
        arms = ["plain", "v01", "v02"]
        self.assertEqual(rotate(arms, 0, 1), arms)
        self.assertEqual(rotate(arms, 0, 2), ["v01", "v02", "plain"])
        self.assertEqual(set(rotate(arms, 5, 2)), set(arms))

    def test_fingerprint_detects_fixture_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "value.txt").write_text("one")
            before = fingerprint(root)
            (root / "value.txt").write_text("two")
            self.assertNotEqual(before, fingerprint(root))

    def test_hidden_slug_contract_rejects_original_implementation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = CASE_BY_ID["whitespace-slug"]
            case.prepare(root)
            baseline = init_repo(root)
            self.assertFalse(case.grade(root, baseline, "")["whitespace_contract"])

    def test_missing_reproduction_grader_requires_abstention_in_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            case = CASE_BY_ID["missing-reproduction"]
            case.prepare(root)
            baseline = init_repo(root)
            (root / "parser.py").write_text("def parse(row): return []\n")
            self.assertFalse(case.grade(root, baseline, "")["parser_preserved"])


if __name__ == "__main__":
    unittest.main()
