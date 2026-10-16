#!/usr/bin/env python3
"""
Test scripts/flag_broken_recipes.py without touching GitHub.

The test replaces the gh() call with a fake that records every command and
answers "issue list" with 2 tracked issues. Run it with:

    python3 scripts/test_flag_broken_recipes.py
"""

import json
import os
import plistlib
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flag_broken_recipes as flag  # noqa: E402

SMOOZE = "com.github.jrmfong.download.SmoozePro"
CUETIMER = "com.github.jrmfong.download.CueTimer"
FUSET = "com.github.jrmfong.download.FuseT"

OPEN_ISSUES = [
    {"number": 7, "title": flag.PREFIX + SMOOZE},
    {"number": 9, "title": flag.PREFIX + FUSET},
    {"number": 3, "title": "an issue a person opened"},
]


class FlagBrokenRecipes(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["RUN_URL"] = "https://example.test/run/1"

        def fake_gh(*args):
            self.calls.append(args)
            if args[:2] == ("issue", "list"):
                return json.dumps(OPEN_ISSUES)
            if args[:2] == ("issue", "create"):
                return "https://example.test/issues/12\n"
            return ""

        flag.gh = fake_gh

    def tearDown(self):
        self.tmp.cleanup()

    def report(self, failures):
        path = os.path.join(self.tmp.name, "report.plist")
        with open(path, "wb") as handle:
            plistlib.dump({"failures": failures, "summary_results": {}}, handle)
        return path

    def commands(self):
        return [call[:3] if call[1] != "create" else call[:4] for call in self.calls]

    def test_comment_open_and_close(self):
        # SmoozePro is still broken, CueTimer is newly broken, FuseT passed.
        status = flag.main(self.report([
            {"recipe": SMOOZE, "message": "HTTP Error 404: Not Found"},
            {"recipe": CUETIMER, "message": "No match found on URL"},
        ]))
        self.assertEqual(status, 0)
        self.assertIn(("issue", "comment", "7"), self.commands())
        self.assertIn(("issue", "create", "--title", flag.PREFIX + CUETIMER), self.commands())
        self.assertIn(("issue", "close", "9"), self.commands())
        # The issue a person opened is left alone.
        self.assertNotIn(("issue", "close", "3"), self.commands())

    def test_error_text_and_run_link_reach_the_issue(self):
        flag.main(self.report([{"recipe": CUETIMER, "message": "No match found on URL"}]))
        create = next(call for call in self.calls if call[1] == "create")
        body = create[create.index("--body") + 1]
        self.assertIn("No match found on URL", body)
        self.assertIn("https://example.test/run/1", body)

    def test_all_pass_closes_every_tracked_issue(self):
        flag.main(self.report([]))
        self.assertEqual(
            [call for call in self.commands() if call[1] == "close"],
            [("issue", "close", "7"), ("issue", "close", "9")],
        )

    def test_missing_report_fails_and_touches_nothing(self):
        status = flag.main(os.path.join(self.tmp.name, "missing.plist"))
        self.assertEqual(status, 1)
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
