# alfred-workflows

My personal [Alfred](https://www.alfredapp.com/) workflows, kept here so they're
versioned and easy to reinstall on a new machine.

## Installing

Double-click any `.alfredworkflow` file to install it into Alfred. Workflows that
need credentials or defaults expose them under the workflow's **Configuration**
pane in Alfred Preferences — nothing sensitive is stored in this repo.

## Workflows

| Workflow | Keyword | Description |
| --- | --- | --- |
| Linear Issue | `li` | Look up a Linear issue by ID (`li ENG-123`) or full-text search, with a live preview. Enter opens in the browser, Cmd+Enter opens in Linear.app. Requires a Linear API key. |
| GitHub Pull Request | `gh` | Jump to a pull request: `gh 1234`, `gh 1234 sfc_base_image`, or `gh 1234 eculver/foo`. A bare repo name is qualified with the default repository's owner. Configurable default repository. |

## Editing

Alfred stores the live copy of an installed workflow in its own preferences
directory, so the file here is an export. After changing a workflow in Alfred,
re-export it (right-click the workflow → **Export…**) over the file in this repo
and commit the result.

The exported file is a zip archive containing `info.plist`; to inspect one
without Alfred:

```sh
unzip -p "Linear Issue.alfredworkflow" info.plist
```
