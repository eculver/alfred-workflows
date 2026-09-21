# alfred-workflows

My personal [Alfred](https://www.alfredapp.com/) workflows, kept here so they're
versioned and easy to reinstall on a new machine.

## Workflows

| Workflow | Keyword | Description |
| --- | --- | --- |
| Linear Issue | `li` | Look up a Linear issue by ID (`li ENG-123`) or full-text search, with a live preview. Enter opens in the browser, Cmd+Enter opens in Linear.app. Requires a Linear API key. |
| GitHub Pull Request | `gh` | Jump to a pull request: `gh 1234`, `gh 1234 sfc_base_image`, or `gh 1234 eculver/foo`. A bare repo name is qualified with the default repository's owner. Configurable default repository. |

## Installing

Download the `.alfredworkflow` files from the [latest
release](../../releases/latest) and double-click to install, or build them
yourself:

```sh
./build.sh
open "dist/GitHub Pull Request.alfredworkflow"
```

Workflows that need credentials or defaults expose them under the workflow's
**Configuration** pane in Alfred Preferences — nothing sensitive is stored in
this repo.

## Layout

Source lives unpacked under `workflows/`, one directory per workflow:

```
workflows/
  github-pull-request/info.plist
  linear-issue/info.plist
```

A `.alfredworkflow` file is just a zip of that directory's contents, so it is a
build artifact rather than source. `build.sh` validates each `info.plist` and
zips it into `dist/`, naming the output after the workflow's `name` key. `dist/`
is gitignored.

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
