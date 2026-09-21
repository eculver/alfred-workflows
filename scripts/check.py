#!/usr/bin/env python3
"""Integrity checks for the workflow sources in workflows/.

Catches the mistakes that are easy to make when hand-editing an exported
info.plist or unpacking one over a source directory: malformed plists, dangling
connection uids, duplicate keywords or bundle ids, embedded scripts that no
longer parse, and a README that has drifted from the workflows on disk.

Usage: scripts/check.py    (exit 0 = clean)
"""

import ast
import pathlib
import plistlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / "workflows"

REQUIRED_KEYS = ("bundleid", "name", "description", "version", "objects", "connections")

problems = []
notes = []


def fail(slug, message):
    problems.append("%s: %s" % (slug, message))


def load(slug, path):
    """Parse info.plist, insisting it stays XML so diffs remain readable."""
    raw = path.read_bytes()
    if not raw.lstrip().startswith(b"<?xml"):
        fail(slug, "info.plist is not XML (re-save as an XML plist so it diffs cleanly)")
        return None
    try:
        return plistlib.loads(raw)
    except Exception as exc:
        fail(slug, "info.plist does not parse: %s" % exc)
        return None


def check_embedded_scripts(slug, obj):
    """Script filters embed a python heredoc; make sure it still compiles."""
    script = (obj.get("config") or {}).get("script") or ""
    for body in re.findall(r"<<'(\w+)'\n(.*?)\n\1", script, re.DOTALL):
        try:
            ast.parse(body[1])
        except SyntaxError as exc:
            fail(slug, "embedded script has a syntax error on line %s: %s" % (exc.lineno, exc.msg))


def check_workflow(slug, plist):
    for key in REQUIRED_KEYS:
        if not plist.get(key):
            fail(slug, "info.plist is missing %s" % key)
    if problems:
        return

    if not re.fullmatch(r"[a-z0-9]+(\.[a-z0-9-]+)+", plist["bundleid"]):
        fail(
            slug,
            "bundleid %r should be reverse-dns, e.g. com.eculver.%s" % (plist["bundleid"], slug),
        )

    uids = set()
    for obj in plist["objects"]:
        uid = obj.get("uid")
        if not uid:
            fail(slug, "an object has no uid")
            continue
        if uid in uids:
            fail(slug, "duplicate object uid %s" % uid)
        uids.add(uid)
        check_embedded_scripts(slug, obj)

    for source, links in plist["connections"].items():
        if source not in uids:
            fail(slug, "connection from unknown uid %s" % source)
        for link in links:
            if link.get("destinationuid") not in uids:
                fail(slug, "connection to unknown uid %s" % link.get("destinationuid"))

    for uid in plist.get("uidata", {}):
        if uid not in uids:
            fail(slug, "uidata references unknown uid %s" % uid)
    missing_pos = uids - set(plist.get("uidata", {}))
    if missing_pos:
        notes.append("%s: %d object(s) have no canvas position" % (slug, len(missing_pos)))

    for item in plist.get("userconfigurationconfig", []):
        if not item.get("variable"):
            fail(slug, "a user configuration entry has no variable name")


def main():
    if not WORKFLOWS.is_dir():
        sys.exit("no workflows/ directory")

    dirs = sorted(d for d in WORKFLOWS.iterdir() if d.is_dir())
    if not dirs:
        sys.exit("workflows/ is empty")

    loaded = {}
    for d in dirs:
        plist_path = d / "info.plist"
        if not plist_path.is_file():
            fail(d.name, "has no info.plist")
            continue
        plist = load(d.name, plist_path)
        if plist is not None:
            loaded[d.name] = plist
            check_workflow(d.name, plist)

    # Cross-workflow uniqueness: colliding bundle ids overwrite each other on
    # install, and colliding keywords make Alfred ambiguous.
    for label, get in (
        ("bundleid", lambda p: [p.get("bundleid")]),
        ("name", lambda p: [p.get("name")]),
        (
            "keyword",
            lambda p: [(o.get("config") or {}).get("keyword") for o in p.get("objects", [])],
        ),
    ):
        seen = {}
        for slug, plist in loaded.items():
            for value in get(plist):
                if not value:
                    continue
                if value in seen:
                    fail(slug, "%s %r is already used by %s" % (label, value, seen[value]))
                seen[value] = slug

    # The README table is the front door; keep it honest.
    readme = (ROOT / "README.md").read_text()
    for slug, plist in loaded.items():
        if plist.get("name") and plist["name"] not in readme:
            fail(slug, "workflow %r is not mentioned in README.md" % plist["name"])

    for note in notes:
        print("note: %s" % note)
    if problems:
        print("\n%d problem(s):" % len(problems), file=sys.stderr)
        for p in problems:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("ok: %d workflow(s) checked" % len(loaded))
    return 0


if __name__ == "__main__":
    sys.exit(main())
