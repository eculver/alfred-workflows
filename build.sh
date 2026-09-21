#!/usr/bin/env bash
#
# Packages each workflow under workflows/ into dist/<Workflow Name>.alfredworkflow
#
# A .alfredworkflow file is just a zip of the workflow directory's contents
# (info.plist plus any icons or assets), so building one is a matter of
# validating the plist and zipping the directory from the inside.
#
# Usage: ./build.sh [workflow-dir-name ...]   (default: all)

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dist="$root/dist"

targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  for dir in "$root"/workflows/*/; do
    targets+=("$(basename "$dir")")
  done
fi

mkdir -p "$dist"

for slug in "${targets[@]}"; do
  src="$root/workflows/$slug"
  plist="$src/info.plist"

  if [ ! -f "$plist" ]; then
    echo "error: $slug has no info.plist" >&2
    exit 1
  fi

  # Validate, and read the display name that the built file is named after.
  name="$(python3 - "$plist" <<'PY'
import plistlib, sys
with open(sys.argv[1], "rb") as f:
    plist = plistlib.load(f)
for key in ("name", "bundleid"):
    if not plist.get(key):
        sys.exit("info.plist is missing a %s" % key)
print(plist["name"])
PY
)"

  out="$dist/$name.alfredworkflow"
  rm -f "$out"
  # -X drops extra file attributes so builds of identical sources match.
  (cd "$src" && zip --quiet -X --recurse-paths "$out" . --exclude '.DS_Store' '*/.DS_Store')

  echo "built $(basename "$out")  <-  workflows/$slug"
done
