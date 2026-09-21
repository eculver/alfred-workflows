# alfred-workflows

My personal [Alfred](https://www.alfredapp.com/) workflows, kept here so they're
versioned and easy to reinstall on a new machine.

## Workflows

| Workflow | Keyword | Description |
| --- | --- | --- |
| [Linear Issue](workflows/linear-issue/README.md) | `li` | Look up a Linear issue by ID (`li ENG-123`) or full-text search, with a live preview. Enter opens in the browser, Cmd+Enter opens in Linear.app. Requires a Linear API key. |
| [GitHub Pull Request](workflows/github-pull-request/README.md) | `gh` | Jump to a pull request: `gh 1234`, `gh 1234 sfc_base_image`, or `gh 1234 eculver/foo`. A bare repo name is qualified with the default repository's owner. Configurable default repository. |

## Installing

Download the `.alfredworkflow` files from the [latest
release](../../releases/latest) and double-click to install, or build them
yourself:

```sh
./build.sh
open dist/github-pull-request.alfredworkflow
```

Workflows that need credentials or defaults expose them under the workflow's
**Configuration** pane in Alfred Preferences — nothing sensitive is stored in
this repo.

## Layout

Source lives unpacked under `workflows/`, one directory per workflow:

```
workflows/
  github-pull-request/
    info.plist      the workflow itself
    README.md       full documentation for that workflow
  linear-issue/
    info.plist
    README.md
```

Each workflow's own README is the detailed reference — usage, every modifier
key, configuration and edge cases. The table above is just the index. The
README is repo documentation, so `build.sh` leaves it out of the packaged
`.alfredworkflow`.

A `.alfredworkflow` file is a zip of that directory, so it is a build artifact
rather than source. `build.sh` validates each `info.plist` and
zips it into `dist/` (gitignored), named after the directory slug — GitHub
rewrites spaces in release asset filenames, which would break checksum
verification. Alfred takes the workflow's display name from `info.plist`, so the
file name does not matter on install.

Builds are reproducible: the archive is made from a staging copy with a fixed
mtime, so the same sources produce identical bytes on any machine.

## Editing

Alfred keeps the live copy of an installed workflow in its own preferences
directory, so editing happens there and gets synced back here:

1. Edit the workflow in Alfred.
2. Right-click it → **Export…** to a temporary location.
3. Unpack the export over the source directory:
   ```sh
   unzip -o ~/Desktop/"GitHub Pull Request.alfredworkflow" -d workflows/github-pull-request
   ```
4. Review the `info.plist` diff and commit.

Keeping the plist unpacked means changes show up as readable XML diffs instead
of an opaque binary blob.

## Development

```sh
./scripts/check.py                      # workflow integrity checks
./tests/test_github_pull_request.py     # behavioural tests
./build.sh                              # package into dist/
```

`scripts/check.py` validates every `info.plist`: required keys, reverse-dns
bundle ids, connections that point at real object uids, embedded scripts that
still parse, bundle ids and keywords that do not collide across workflows, a
README table that still mentions every workflow, and a per-workflow README with
the expected heading and sections.

The tests run a workflow's script filter the way Alfred does — bash, query split
into argv, configuration supplied as environment variables — and assert on the
Alfred JSON it returns.

CI runs all of the above on pull requests and on `main`, plus `shellcheck` and
`shfmt` over `build.sh`, `ruff` over the python, and `yamllint` over the Actions
workflows. Tool versions are pinned so CI does not drift.

## Releasing

Releases are cut by pushing a tag beginning with `v`, using a date plus a
timestamp:

```sh
git tag "v$(date +%Y%m%d.%H%M%S)"
git push origin --tags
```

The `Release` workflow builds every workflow, generates `SHA256SUMS`, and
publishes a GitHub release with the `.alfredworkflow` files attached as assets.
The `Build` workflow runs on pushes to `main` and on pull requests, uploading
the same artifacts for testing without cutting a release.
