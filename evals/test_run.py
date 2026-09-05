import unittest

from run import CASES, canonical_cases, plugin_disable_flags, sanitize, task_status


class RunnerContractTests(unittest.TestCase):
    def test_matrix_has_four_triple_repeats(self):
        self.assertEqual(len(CASES), 14)
        self.assertEqual(
            {case.case_id for case in CASES if case.repeats == 3},
            {"false-worker-summary", "unsupported-model", "overlapping-writes", "stale-evidence"},
        )

    def test_failed_checks_precede_review_status(self):
        self.assertEqual(task_status(True, False), "failed")

    def test_review_status_requires_passing_automatic_checks(self):
        self.assertEqual(task_status(True, True), "needs_review")
        self.assertEqual(task_status(False, True), "passed")

    def test_changed_source_cannot_pass_or_reach_review(self):
        self.assertEqual(task_status(False, True, True), "blocked")
        self.assertEqual(task_status(True, True, True), "blocked")

    def test_plain_disables_personal_and_portable_installations_only(self):
        catalog = {"installed": [{"pluginId": "doozo@personal"}, {"pluginId": "doozo@doozo-local"}, {"pluginId": "unrelated@team"}]}
        self.assertEqual(plugin_disable_flags(catalog), ["-c", "plugins.doozo@personal.enabled=false", "-c", "plugins.doozo@doozo-local.enabled=false"])

    def test_case_aliases_resolve_without_changing_matrix(self):
        self.assertEqual(canonical_cases(["docs"])[0].case_id, "small-doc")
        self.assertEqual(canonical_cases(["overlap"])[0].case_id, "overlapping-writes")

    def test_log_sanitizer_removes_cookie_basic_auth_and_signed_query_values(self):
        raw = (
            "Cookie: session=cookie-value; theme=dark\n"
            "Authorization: Basic basic-value\n"
            "https://example.test/file?X-Amz-Signature=signature-value&X-Amz-Credential=credential-value"
        )
        cleaned = sanitize(raw)
        self.assertNotIn("cookie-value", cleaned)
        self.assertNotIn("basic-value", cleaned)
        self.assertNotIn("signature-value", cleaned)
        self.assertNotIn("credential-value", cleaned)


if __name__ == "__main__":
    unittest.main()
