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
| Remake the Tamil font subset | `curl -fsSL -o /tmp/NotoSansTamil-v2.004.zip https://github.com/notofonts/tamil/releases/download/NotoSansTamil-v2.004/NotoSansTamil-v2.004.zip`, then `uv run --locked python -B scripts/make-tamil-font.py /tmp/NotoSansTamil-v2.004.zip` |
| Check your commits | `BASE_SHA=$(git merge-base origin/main HEAD) HEAD_SHA=HEAD ALLOWED_COMMIT_IDENTITIES=<your noreply address> uv run --locked python -B .github/scripts/commit_policy.py` |
| Install the preview tool | `cd deploy && corepack pnpm install --frozen-lockfile` |
| Preview the site | `cd deploy && corepack pnpm run preview`, then open http://localhost:8787 |
| Check the preview tool's ages | `cd deploy && corepack pnpm install --frozen-lockfile --lockfile-only` |

The hooks need `uv`, `gitleaks` and `lychee` on PATH and libmagic for `reuse`; the preview needs Node 24 with
corepack. Python is 3.14.10, as `.python-version` says; uv installs it on first use.

CI runs on every pull request. The checks to pass are `Gate summary`, `Secret scan / Full history`, `Local links`,
`dependency-age` and `Analyze (actions)`. The commit policy, inside `Repository checks`, reads the repository variable
`ALLOWED_COMMIT_IDENTITIES`.

A merge to main deploys `public/` through the Deploy workflow and the protected `production` environment; nothing is
deployed by hand. Every deployed file carries build provenance and an SBOM attestation. To check a live file, with gh
and cosign 2.4 or newer:

```sh
curl -fsSL -o page https://vergalin.com/privacy
digest=$(sha256sum page | cut -d' ' -f1)
for type in https://slsa.dev/provenance/v1 https://spdx.dev/Document/v2.3; do
  gh api "repos/dinesh-ad/vergalin/attestations/sha256:$digest" \
    --jq "[.attestations[].bundle | select(.dsseEnvelope.payload | @base64d | fromjson | .predicateType == \"$type\")][0]" \
    > bundle.json
  cosign verify-blob-attestation --new-bundle-format --bundle bundle.json \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    --certificate-identity https://github.com/dinesh-ad/vergalin/.github/workflows/deploy.yml@refs/heads/main \
    --type "$type" page
done
```

## Map

| Path | Holds |
|---|---|
| `public/` | The pages, `style.css`, the icon, the Tamil font subset in `fonts/` and `_headers`, served as they are |
| the `.jsonc` file at the root | The host's settings: files only, no script, the 404 page |
| `deploy/` | The tool that previews and uploads the site, pinned in `pnpm-lock.yaml`; the age and install-script rules in `pnpm-workspace.yaml` |
| `.github/workflows/deploy.yml` | The deploy: checks and SBOM, attestations, upload from `production`; `tests/test_deploy_workflow.py` keeps its triggers, secrets and pins |
| `scripts/check-headers.py` | The header check the `headers` hook runs |
| `scripts/make-tamil-font.py` | Makes `public/fonts/` from the Noto Sans Tamil release; `tests/test_tamil_font.py` pins the result |
| `scripts/check-suppressions.sh`, `.github/scripts/` | Copies of other projects' files (see Boundaries) |
| `tests/` | The tests of the checks, the gate and the copies |
| `.gitleaks.toml` | The leak rules; its last link allowlist holds the hosts this site links to |
| `REUSE.toml`, `LICENSES/` | Each file's copyright and licence |
| `docs/decisions/` | Why each decision was made |

## Boundaries

- Never add a script, another web font, analytics, a cookie or a request to another site: `public/_headers` allows only the
  site's own files.
- Never name the host's product or its tool outside the host's settings file, `deploy/` and the deploy workflow; write "the
  host" and "the preview tool".
- Never write an email address, a phone number or a family member's name in any page, file or commit.
- Never edit `.github/scripts/` or `scripts/check-suppressions.sh` by hand: copy the file again from its source and
  update its line in `tests/test_vendored.py`.
- Never run pnpm other than as `corepack pnpm` in `deploy/`, and never `npx`.
- Never add a pull-request trigger, or a secret outside the deploy job, to `.github/workflows/deploy.yml`
  (`tests/test_deploy_workflow.py`); never deploy by hand.
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
