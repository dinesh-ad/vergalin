# Ship a Tamil font subset

Date: 2026-11-27
Status: accepted
Supersedes: the font line of [A static site served as files only](2026-11-27-static-site-served-as-assets-only.md)

## Context

The site's name, வேர்களின், is Tamil. A browser on a device with no Tamil font shows empty boxes in its place, as one
laptop's built-in browser did on 2026-11-27. The earlier decision relied on system fonts. engineering-practices allows
only self-hosted fonts (§7D.2), and `public/` must stay complete on its own.

## Decision

We will ship one Tamil font with the site:

- A subset of Noto Sans Tamil v2.004 (OFL-1.1), from the official notofonts/tamil release: the whole Tamil block,
  ZWNJ and ZWJ, and every OpenType layout feature. `scripts/make-tamil-font.py` makes it from the recorded release and
  `tests/test_tamil_font.py` pins it.
- The file name carries the release version: `public/fonts/noto-sans-tamil-v2.004-tamil.woff2`.
- The content security policy gains `font-src 'self'` and nothing else.
- `@font-face` loads only that file with `url()`, never `local()`, which lets a page probe the visitor's installed
  fonts. The font is not preloaded, because a preload ignores `unicode-range`.
- `/fonts/*` is cached for one year as `immutable`.

## Consequences

- About 23 KB, downloaded only on pages with Tamil text, because `unicode-range` limits the font to the Tamil block.
- The name renders the same on every device, in the shipped font rather than the device's own.
- A new font release gets a new file name, so a cached copy never goes stale.
