# A static site served as files only

Date: 2026-11-27
Status: accepted

## Context

Google's app branding needs a home page and a privacy policy on a domain the owner has verified before the family's
backup tool can be published. vergalin.com is the family's long-term domain. Today it needs three pages that never
change between visitors: home, privacy and a 404 page. engineering-practices asks for static sites served as files
only, so requests are not billed (§1.1), and for web pages with no third-party requests and a strict content security
policy (§7D).

## Decision

We will serve `public/` as it is, as static files with no script:

- Plain HTML and one stylesheet: no build step, no JavaScript, no web font (system fonts render Tamil), no cookie.
- The host's settings name no script, so no request runs code. An unknown path gets `public/404.html` with status 404.
- `public/_headers` sets seven security headers on every path. Its content security policy starts from
  `default-src 'none'` and allows only the site's own stylesheet and icon; `scripts/check-headers.py` keeps it so.
- The preview tool is pinned in `deploy/` so the host's routing and headers can be seen locally before a merge. It is
  installed with pnpm 11 through corepack, which checks the sha512 in `packageManager`. The lockfile holds only versions
  at least 7 days old, and install scripts are refused unless listed.
- pnpm 11, not 12: GitHub's own pages do not confirm that the dependency graph reads the two-document lockfile pnpm 12
  writes.

## Consequences

- Nothing runs at request time, so there is no server code to patch and no request is billed.
- A page that needs a script, a form or a third-party resource needs a new decision, because the policy refuses it.
- pnpm 11 support ends 2027-04-30; `deploy/` moves to a supported pnpm before then.
