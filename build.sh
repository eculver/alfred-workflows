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

  # Validate, and read the display name for the build log.
  name="$(
    python3 - "$plist" <<'PY'
import plistlib, sys
with open(sys.argv[1], "rb") as f:
    plist = plistlib.load(f)
for key in ("name", "bundleid"):
    if not plist.get(key):
        sys.exit("info.plist is missing a %s" % key)
print(plist["name"])
PY
  )"

  # Named after the directory slug, not the display name: GitHub rewrites
  # spaces in release asset filenames, which breaks checksum verification.
  out="$dist/$slug.alfredworkflow"
  rm -f "$out"

  # Build from a staging copy with a fixed mtime. zip records timestamps, so
  # without this the same sources produce different bytes on every checkout.
  stage="$(mktemp -d)"
  trap 'rm -rf "$stage"' EXIT
  cp -R "$src"/. "$stage"/
  find "$stage" -name '.DS_Store' -delete
  # README.md documents the workflow for this repo; it is not part of the
  # workflow itself, so it does not belong in the installed bundle.
  rm -f "$stage/README.md"
  find "$stage" -exec touch -t 200001010000 {} +
  # -X drops extra file attributes so builds of identical sources match.
  (cd "$stage" && zip --quiet -X --recurse-paths "$out" .)
  rm -rf "$stage"
  trap - EXIT

  echo "built $(basename "$out")  <-  $name"
done
