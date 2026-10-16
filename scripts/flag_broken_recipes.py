#!/usr/bin/env python3
"""
Open, update or close a GitHub issue for each recipe the download check found
broken.

Read the report that autopkg run --report-plist wrote. For each recipe that
failed, open an issue titled "Download recipe broken: <identifier>", or add a
comment to the open issue of the same title. Close the open issue of any recipe
that passed this run.

Runs in GitHub Actions with gh on the path, GH_TOKEN and GH_REPO set by the
workflow, and RUN_URL pointing at the run.
"""

import json
import os
import plistlib
import subprocess
import sys
from datetime import date

PREFIX = "Download recipe broken: "


def gh(*args):
    """
    Run a gh command and return its output.
    """
    return subprocess.run(
        ["gh", *args], check=True, capture_output=True, text=True
    ).stdout


def open_issues():
    """
    Map each recipe with an open issue to that issue's number.

    List every open issue rather than search, because the search index can lag
    behind a new issue by minutes.
    """
    issues = json.loads(
        gh("issue", "list", "--state", "open", "--limit", "200",
           "--json", "number,title")
    )
    return {
        issue["title"][len(PREFIX):]: issue["number"]
        for issue in issues
        if issue["title"].startswith(PREFIX)
    }


def main(report_path):
    """
    Flag each failed recipe, then clear the flag of each recipe that passed.
    """
    if not os.path.isfile(report_path):
        print(f"{report_path} is missing, so the check did not run.")
        return 1

    with open(report_path, "rb") as handle:
        failures = {
            item["recipe"]: item["message"]
            for item in plistlib.load(handle)["failures"]
        }
    tracked = open_issues()
    today = date.today().isoformat()
    run_url = os.environ.get("RUN_URL", "")

    for recipe, message in failures.items():
        body = f"The check on {today} failed:\n\n```\n{message}\n```\n\nRun: {run_url}"
        if recipe in tracked:
            gh("issue", "comment", str(tracked[recipe]), "--body", body)
            print(f"commented on #{tracked[recipe]} for {recipe}")
        else:
            url = gh("issue", "create", "--title", PREFIX + recipe, "--body", body)
            print(f"opened {url.strip()} for {recipe}")

    for recipe, number in tracked.items():
        if recipe not in failures:
            gh("issue", "close", str(number),
               "--comment", f"The check passed on {today}.\n\nRun: {run_url}")
            print(f"closed #{number} for {recipe}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "report.plist"))
