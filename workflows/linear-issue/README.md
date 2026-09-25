# Linear Issue

Find and open Linear issues from Alfred, either by exact issue ID or by
full-text search, with the issue's state, assignee, priority and project shown
inline.

```
li ENG-123
li billing bug
```

## Quickstart

1. Install the workflow (see [Installation](#installation)).
2. Create a personal API key at
   [linear.app/settings/account/security](https://linear.app/settings/account/security).
3. Paste it into the workflow's **Configuration** in Alfred.
4. Open Alfred, type `li ENG-123`, press Enter.

Until the key is set, the workflow shows a row telling you so rather than
failing silently.

## Installation

Download `linear-issue.alfredworkflow` from the
[latest release](../../../../releases/latest) and double-click it, or build from
source:

```sh
./build.sh linear-issue
open dist/linear-issue.alfredworkflow
```

Requires Alfred with the Powerpack. The script filter runs on the system
`/usr/bin/python3` and talks to Linear's GraphQL API over HTTPS, so it needs
network access but nothing installed.

## Usage

```
li <issue-id>
li <search terms>
```

The workflow picks its strategy from what you type:

| What you type | What happens |
| --- | --- |
| `ENG-123` (matches `<letters/digits>-<digits>`) | Direct lookup of that exact issue. Case-insensitive, so `eng-123` works. If no such issue exists, it falls back to search. |
| anything else | Full-text search across issues you can see, showing the top 8 matches. |

At least two characters are required before the workflow does anything, and it
waits briefly after you stop typing before calling the API, so a search does not
fire on every keystroke.

Each result shows the issue identifier and title, with state, assignee,
priority and project in the subtitle — enough to pick the right one without
opening anything.

### Examples

| Input | Result |
| --- | --- |
| `li ENG-123` | That exact issue. |
| `li eng-123` | Same; identifiers are upper-cased. |
| `li billing bug` | Top 8 issues matching "billing bug". |
| `li deploy` | Top 8 issues matching "deploy". |

### Modifier keys

| Key | Action |
| --- | --- |
| Enter | Open the issue in your browser. |
| Cmd+Enter | Open the issue in the Linear desktop app (`linear://`). |
| Cmd+C | Copy the issue URL. |
| Cmd+L | Show the identifier, title and subtitle in Large Type. |
| Shift | Quick Look the issue. |

## Configuration

Alfred Preferences → Workflows → Linear Issue → **Configuration**
(the `[x]` button).

| Setting | Variable | Purpose |
| --- | --- | --- |
| Linear API Key | `LINEAR_API_KEY` | Personal API key used to query the Linear GraphQL API. |

Create the key at
[linear.app/settings/account/security](https://linear.app/settings/account/security).
It is stored in Alfred's own preferences, not in this repository. The key grants
access to everything your Linear account can see, so treat it like a password
and revoke it in Linear if it leaks.

Results are limited to issues your account has access to; there is no way to
search issues you cannot otherwise see.

## Behaviour and edge cases

| Situation | Result |
| --- | --- |
| API key not set | A row explaining where to set it. |
| Fewer than two characters typed | A usage hint. |
| Identifier looks valid but does not exist | Falls back to full-text search. |
| No matches | `No issues matching '<query>'`. |
| Network error, bad key, or a slow API | `Linear request failed` with the underlying error in the subtitle. |

Requests time out after 10 seconds. Nothing is cached, so results are always
current — and every keystroke past the delay is a fresh API call.

## Development

```sh
./scripts/check.py        # plist integrity
./build.sh linear-issue   # package
```

There are no automated behavioural tests for this workflow, because every code
path calls the Linear API and would need either a live key or a stubbed
transport. `scripts/check.py` still verifies that the embedded script parses.
To exercise it by hand, extract the script and run it the way Alfred would:

```sh
python3 -c "import plistlib;print(plistlib.load(open('workflows/linear-issue/info.plist','rb'))['objects'][0]['config']['script'])" > /tmp/li.sh
LINEAR_API_KEY=lin_api_... bash /tmp/li.sh ENG-123 | python3 -m json.tool
```
