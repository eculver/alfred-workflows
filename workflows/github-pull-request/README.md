# GitHub Pull Request

Jump straight to a GitHub pull request from Alfred by typing its number.

```
gh 1234
```

Most pull requests you open are in one repository, so the common case is a
number and nothing else. Other repositories are reachable without typing a full
`owner/repo` when they share an owner with your default.

## Quickstart

1. Install the workflow (see [Installation](#installation)).
2. Open Alfred, type `gh 1234`, press Enter.

It works out of the box against `sfcompute/sfcompute`. To point it somewhere
else, change the **Default Repository** setting described in
[Configuration](#configuration).

## Installation

Download `github-pull-request.alfredworkflow` from the
[latest release](../../../../releases/latest) and double-click it, or build from
source:

```sh
./build.sh github-pull-request
open dist/github-pull-request.alfredworkflow
```

Requires Alfred with the Powerpack. The script filter runs on the system
`/usr/bin/python3`, so there is nothing to install.

## Usage

```
gh <number> [<repo>]
```

| Argument | Required | Meaning |
| --- | --- | --- |
| `<number>` | yes | Pull request number. A leading `#` is accepted and ignored. |
| `<repo>` | no | Either a bare repository name or a full `owner/repo`. Defaults to the configured **Default Repository**. |

The repository argument is resolved in three ways:

| What you type | How it resolves |
| --- | --- |
| nothing | The **Default Repository** verbatim. |
| `sfc_base_image` | Qualified with the *owner* of the Default Repository, giving `sfcompute/sfc_base_image`. |
| `eculver/foo` | Used exactly as given. |

Alfred shows the resolved URL in the result subtitle, so you can confirm where
you are about to land before pressing Enter.

### Examples

| Input | Opens |
| --- | --- |
| `gh 1234` | `https://github.com/sfcompute/sfcompute/pull/1234` |
| `gh #1234` | `https://github.com/sfcompute/sfcompute/pull/1234` |
| `gh 1234 sfc_base_image` | `https://github.com/sfcompute/sfc_base_image/pull/1234` |
| `gh 1234 eculver/foo` | `https://github.com/eculver/foo/pull/1234` |

### Modifier keys

| Key | Action |
| --- | --- |
| Enter | Open the pull request. |
| Cmd+Enter | Open the pull request's **Files changed** tab. |
| Option+Enter | Open the repository's pull request list. |
| Cmd+C | Copy the pull request URL. |
| Cmd+L | Show the URL in Large Type. |
| Shift | Quick Look the pull request. |

## Configuration

Alfred Preferences → Workflows → GitHub Pull Request → **Configuration**
(the `[x]` button).

| Setting | Variable | Default | Purpose |
| --- | --- | --- | --- |
| Default Repository | `DEFAULT_REPO` | `sfcompute/sfcompute` | Used when no repository is given. Its owner also becomes the default organization for a bare repository name. |

It must be a full `owner/repo`; the owner half is what makes
`gh 1234 sfc_base_image` work. If it is empty or has no `/`, the workflow says
so instead of guessing.

## Behaviour and edge cases

The workflow never navigates anywhere it cannot construct a sensible URL for.
These inputs produce an inactive hint row rather than opening something wrong:

| Input | Result |
| --- | --- |
| `gh` | Usage hint naming the current default repository. |
| `gh abc` | `'abc' is not a pull request number`. |
| `gh 1234 a/b/c` | `'a/b/c' is not a valid repository`. |
| `gh 1234 bad name` | `Too many arguments`. |
| any input, default repo unset | Prompt to fix the Default Repository setting. |

Notes on deliberate choices:

- **`/pull/` not `/pulls/`.** GitHub's canonical path for a single pull request
  is `/pull/<n>`; `/pulls` is the list view.
- **Numeric repository names are allowed.** `gh 12 34` resolves to the repo
  named `34`, because that is a legal GitHub repository name. The subtitle shows
  the URL so a typo is visible before you open it.
- **No network calls.** The workflow only builds a URL, so it is instant and
  works offline. It does not verify that the pull request exists; a wrong number
  lands on GitHub's 404 page.
- **Issues work too.** GitHub redirects `/pull/<n>` to `/issues/<n>` when the
  number is an issue, so `gh` finds either.

## Development

```sh
./scripts/check.py                    # plist integrity
./tests/test_github_pull_request.py   # behavioural tests
./build.sh github-pull-request        # package
```

The tests drive the script filter the way Alfred does — bash, query split into
argv, `DEFAULT_REPO` from the environment — and assert on the Alfred JSON it
returns. Add a case to `CASES` in the test file when you change argument
handling.

The logic lives in a Python heredoc inside `info.plist`, under the script
filter's `script` key. To read it on its own:

```sh
python3 -c "import plistlib;print(plistlib.load(open('workflows/github-pull-request/info.plist','rb'))['objects'][0]['config']['script'])"
```
