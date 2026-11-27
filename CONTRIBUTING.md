# Contributing to vergalin

The vergalin.com site: plain HTML and one stylesheet, served as static files. The rules for every repository are in
[engineering-practices](https://github.com/Vercroft/engineering-practices/blob/main/STANDARD.md); this file adds only
what is specific here. Pull requests come from collaborators only; issues are welcome.

## Commands

From the repository root, unless the command starts with `cd deploy`.

| To | Run |
|---|---|
| Install the Python tools | `uv sync --locked` |
| Install the git hooks | `uv run --locked pre-commit install` |
| Run every check | `uv run --locked pre-commit run --all-files` |
| Run the push checks | `uv run --locked pre-commit run --hook-stage pre-push --all-files` |
| Run the hooks as CI does | `SKIP=gitleaks uv run --locked pre-commit run --all-files --hook-stage manual` |
| Run the tests | `uv run --locked pytest` |
| Run one test | `uv run --locked pytest tests/test_check_headers.py::test_the_real_file_passes` |
| Lint, format and types | `uv run --locked ruff check`, `uv run --locked ruff format --check`, `uv run --locked mypy` |
| Check the headers | `uv run --locked python -B scripts/check-headers.py` |
| Check your commits | `BASE_SHA=$(git merge-base origin/main HEAD) HEAD_SHA=HEAD ALLOWED_COMMIT_IDENTITIES=<your noreply address> uv run --locked python -B .github/scripts/commit_policy.py` |
| Install the preview tool | `cd deploy && corepack pnpm install --frozen-lockfile` |
| Preview the site | `cd deploy && corepack pnpm run preview`, then open http://localhost:8787 |
| Check the preview tool's ages | `cd deploy && corepack pnpm install --frozen-lockfile --lockfile-only` |

The hooks need `uv`, `gitleaks` and `lychee` on PATH and libmagic for `reuse`; the preview needs Node 24 with
corepack. Python is 3.14.10, as `.python-version` says; uv installs it on first use.

CI runs on every pull request. The checks to pass are `Gate summary`, `Secret scan / Full history`, `Local links`,
`dependency-age` and `Analyze (actions)`. The commit policy, inside `Repository checks`, reads the repository variable
`ALLOWED_COMMIT_IDENTITIES`.

## Map

| Path | Holds |
|---|---|
| `public/` | The pages, `style.css`, the icon and `_headers`, served as they are |
| the `.jsonc` file at the root | The host's settings: files only, no script, the 404 page |
| `deploy/` | The preview tool, pinned in `pnpm-lock.yaml`; the age and install-script rules in `pnpm-workspace.yaml` |
| `scripts/check-headers.py` | The header check the `headers` hook runs |
| `scripts/check-suppressions.sh`, `.github/scripts/` | Copies of other projects' files (see Boundaries) |
| `tests/` | The tests of the checks, the gate and the copies |
| `.gitleaks.toml` | The leak rules; its last link allowlist holds the hosts this site links to |
| `REUSE.toml`, `LICENSES/` | Each file's copyright and licence |
| `docs/decisions/` | Why each decision was made |

## Boundaries

- Never add a script, a web font, analytics, a cookie or a request to another site: `public/_headers` allows only the
  site's own files.
- Never name the host's product or its tool outside the host's settings file, `deploy/` and the deploy workflow; write "the
  host" and "the preview tool".
- Never write an email address, a phone number or a family member's name in any page, file or commit.
- Never edit `.github/scripts/` or `scripts/check-suppressions.sh` by hand: copy the file again from its source and
  update its line in `tests/test_vendored.py`.
- Never run pnpm other than as `corepack pnpm` in `deploy/`, and never `npx`.
- A new outside link needs its host added to the last allowlist of `.gitleaks.toml` after review.
- Secrets never go in git.

## Done means

- `pre-commit run --all-files` and the push checks pass, and the preview shows the change.
- New behaviour has a test that failed before the change.
- Every document the change makes wrong is updated in the same change, and a changed decision has a new record in
  `docs/decisions/`.

## Commits and pull requests

As engineering-practices'
[section 6](https://github.com/Vercroft/engineering-practices/blob/main/STANDARD.md#6-git-pull-requests-and-merging)
says: one logical change per commit, approved identities only, no tool named, no em or en dash.
