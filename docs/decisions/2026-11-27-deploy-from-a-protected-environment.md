# Deploy from a protected environment, with provenance and an SBOM on every file

Date: 2026-11-27
Status: accepted

## Context

vergalin is a public repository whose static site must go live. engineering-practices asks a public repository's
static site to deploy from its own GitHub Actions through a protected environment that holds the only token
(§7B.16), and its deployable outputs to carry build provenance (§7B.10) and an SBOM (§7B.11). The site is the files of
`public/`, uploaded as they are; nothing is built.

## Decision

We will deploy with `.github/workflows/deploy.yml`, on every push to main and by hand from main:

- **Three jobs.** `build` runs the site's checks and makes an SPDX SBOM of `public/`, with no secret and no write
  permission. `attest` holds the right to sign and runs no repository code. `deploy` alone runs in the `production`
  environment, alone sees the token, and uploads the files `attest` signed: it deletes its checked-out `public/` and
  downloads the artifact, whose digest the download action checks.
- **Provenance and the SBOM are attested on the files themselves,** one attestation of each with every file as a
  subject, so anyone can check one live file by its own sha256 (`CONTRIBUTING.md`).
- **The SBOM tool lists files, not packages.** reuse, already here, writes SPDX 2.1 tag-value only, and the SPDX
  project's converter validates only 2.2 and 2.3; syft writes SPDX 2.3 JSON and, with its file metadata set to all,
  lists every file with its sha256. syft is pinned by version and checksum.
- **The upload tool comes from `deploy/pnpm-lock.yaml`,** installed with install scripts blocked, not from the host's
  own action. That action installs the tool at run time from a version number, so its dependencies are resolved fresh,
  without a lockfile and with install scripts running; the lockfile pins every package by integrity under the 7-day
  rule.
- **One token, for this site only,** with the narrowest role on the one site and an expiry within a year, kept only as
  a secret of `production`, whose deployments are limited to main with no administrator bypass.
- **A manual run is allowed** (`workflow_dispatch`), limited to main: GitHub re-runs a failed run for 30 days only, and
  a redeploy without a commit is needed after the token is renewed or the site is recreated.
- A running deploy is never cancelled. `tests/test_deploy_workflow.py` keeps the triggers, the secrets, the
  environment, the right to sign and the pins as they are.

## Consequences

- The token expires within a year and is renewed by hand, before its expiry alert.
- The first run fails until the `production` environment and its secrets exist.
- syft is updated by hand: Dependabot does not read the version in a `run:` line.
- Every live file can be checked against the attestation of the commit that deployed it.
- The pages are uploaded without a build, so the deployed bytes are the reviewed bytes.
