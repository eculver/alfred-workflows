#!/usr/bin/env python3
"""End-to-end tests for the GitHub Pull Request workflow.

Runs the script filter exactly as Alfred does - bash, with the query split into
argv and DEFAULT_REPO supplied as an environment variable - against the plist in
workflows/, and asserts on the Alfred JSON that comes back.

Usage: tests/test_github_pull_request.py
"""

import json
import pathlib
import plistlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLIST = ROOT / "workflows" / "github-pull-request" / "info.plist"
DEFAULT_REPO = "sfcompute/sfcompute"

# (query, expected url or None when the result should not be actionable)
CASES = [
    ("1234", "https://github.com/sfcompute/sfcompute/pull/1234"),
    ("1234 sfc_base_image", "https://github.com/sfcompute/sfc_base_image/pull/1234"),
    ("1234 eculver/foo", "https://github.com/eculver/foo/pull/1234"),
    ("#1234", "https://github.com/sfcompute/sfcompute/pull/1234"),
    ("1234 /sfc_base_image/", "https://github.com/sfcompute/sfc_base_image/pull/1234"),
    ("  1234   eculver/foo  ", "https://github.com/eculver/foo/pull/1234"),
    ("", None),
    ("abc", None),
    ("abc 123", None),
    ("1234 a/b/c", None),
    ("1234 bad name", None),
    # A purely numeric repo name is legal on GitHub, so this resolves rather
    # than erroring; the result row shows the URL before it is opened.
    ("12 34", "https://github.com/sfcompute/34/pull/12"),
]


def run(query, default_repo=DEFAULT_REPO):
    plist = plistlib.loads(PLIST.read_bytes())
    script = plist["objects"][0]["config"]["script"]
    proc = subprocess.run(
        ["/bin/bash", "-c", script, "bash"] + query.split(),
        capture_output=True,
        text=True,
        env={"DEFAULT_REPO": default_repo, "PATH": "/usr/bin:/bin"},
    )
    if proc.returncode != 0:
        raise AssertionError("script exited %d: %s" % (proc.returncode, proc.stderr))
    return json.loads(proc.stdout)["items"]


def main():
    failures = []

    for query, expected in CASES:
        try:
            item = run(query)[0]
        except Exception as exc:
            failures.append("%r raised %s" % (query, exc))
            continue
        actual = item.get("arg") if item.get("valid", True) else None
        if actual != expected:
            failures.append("%r -> %r, expected %r" % (query, actual, expected))

    # A misconfigured default repository must be reported, not guessed at.
    for bad in ("", "sfcompute", "   "):
        item = run("1234", default_repo=bad)[0]
        if item.get("valid", True):
            failures.append("default repo %r should produce an inactive hint" % bad)

    # Modifier actions should stay pointed at the same pull request.
    item = run("1234")[0]
    mods = item.get("mods", {})
    if mods.get("cmd", {}).get("arg") != "https://github.com/sfcompute/sfcompute/pull/1234/files":
        failures.append("cmd modifier does not open the Files changed tab")
    if mods.get("alt", {}).get("arg") != "https://github.com/sfcompute/sfcompute/pulls":
        failures.append("alt modifier does not open the pull request list")
    if item.get("text", {}).get("copy") != item.get("arg"):
        failures.append("Cmd+C would copy something other than the pull request URL")

    if failures:
        print("%d failure(s):" % len(failures), file=sys.stderr)
        for f in failures:
            print("  - %s" % f, file=sys.stderr)
        return 1
    print("ok: %d cases passed" % (len(CASES) + 6))
    return 0


if __name__ == "__main__":
    sys.exit(main())
