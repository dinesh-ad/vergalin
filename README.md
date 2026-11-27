<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/images/home-dark.png">
    <img src="docs/images/home-light.png" alt="The Vergalin home page: the name in English and Tamil, the line &quot;of the roots&quot;, and a section on Vergalin Backup that links to the privacy policy" width="800">
  </picture>
</p>

# Vergalin

வேர்களின், "of the roots": the family's home on the web, and the privacy policy of Vergalin Backup, the family's
private backup tool. Live at [vergalin.com](https://vergalin.com) from the first deploy.

[![CI](https://github.com/dinesh-ad/vergalin/actions/workflows/ci.yml/badge.svg)](https://github.com/dinesh-ad/vergalin/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://api.scorecard.dev/projects/github.com/dinesh-ad/vergalin/badge)](https://scorecard.dev/viewer/?uri=github.com/dinesh-ad/vergalin)

## How a change ships

```mermaid
flowchart LR
  PR[Pull request] --> CK["Checks: hooks, Python, secret scan,<br/>links, dependency age, CodeQL"]
  CK --> OM[Owner approves and merges]
  OM --> DP["Deploy from a protected<br/>environment (coming next)"]
  DP --> SH[Static host, files only]
  SH --> LIVE["vergalin.com<br/>/ · /privacy"]
```

Why the site is files only: [the decision](docs/decisions/2026-11-27-static-site-served-as-assets-only.md).

## Quick start

Node 24 with corepack (`.nvmrc`). The preview serves `public/` with the host's routing, 404 page and headers.

```sh
cd deploy
corepack pnpm install --frozen-lockfile
corepack pnpm run preview   # http://localhost:8787
```

## Links

[Contributing](CONTRIBUTING.md) · [Reporting a vulnerability](SECURITY.md) · [Decisions](docs/decisions/)

## License

All rights reserved: see [LICENSE](LICENSE). A few files copied from other projects keep their own licences, listed in
[REUSE.toml](REUSE.toml).
