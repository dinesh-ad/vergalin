#!/usr/bin/env python3
"""Check public/_headers: its syntax, the seven headers on every path, the policy and the font.

The host rejects the whole file when one line is malformed, so every non-empty line that does not
start with "#" must be a path at column 0 (starting with "/" or "https://") or an indented
"Name: value". The "/*" block must set each of the seven headers; its Content-Security-Policy
must be exactly the expected policy, which starts from default-src 'none' and allows only the
site's own stylesheet, icon and font. No line may allow 'unsafe-inline'. The "/fonts/*" block
must let browsers keep the versioned font file for a year.

Usage: check-headers.py [path]   (default: public/_headers)
"""

import re
import sys
from pathlib import Path
from typing import Final

DEFAULT_FILE: Final = "public/_headers"
EVERY_PATH: Final = "/*"
FONTS: Final = "/fonts/*"
REQUIRED: Final = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Strict-Transport-Security",
    "Content-Security-Policy",
)
POLICY: Final = {
    "default-src": "'none'",
    "style-src": "'self'",
    "img-src": "'self'",
    "font-src": "'self'",
    "base-uri": "'none'",
    "form-action": "'none'",
    "frame-ancestors": "'none'",
}
FONT_CACHE: Final = "public, max-age=31536000, immutable"
PATH_RULE: Final = re.compile(r"^(/|https?://)\S*$")
HEADER_RULE: Final = re.compile(r"^[ \t]+([!#$%&'*+.^_`|~0-9A-Za-z-]+):(.*\S)")


def directives(policy: str) -> dict[str, str]:
    """Split a policy into its directives, each with its sources joined by one space."""
    found: dict[str, str] = {}
    for part in policy.split(";"):
        words = part.split()
        if words:
            found[words[0].lower()] = " ".join(words[1:])
    return found


def policy_problems(policy: str, name: str) -> list[str]:
    """Return how the policy differs from the expected one, directive by directive."""
    actual = directives(policy)
    return [
        f"{name}: the Content-Security-Policy has {directive} {actual.get(directive, '(none)')}"
        f", expected {POLICY.get(directive, '(none)')}"
        for directive in sorted(set(POLICY) | set(actual))
        if actual.get(directive) != POLICY.get(directive)
    ]


def problems(text: str, name: str) -> list[str]:
    """Return every rule the file breaks, one line each."""
    found: list[str] = []
    blocks: dict[str, dict[str, str]] = {}
    current: dict[str, str] | None = None
    for number, raw in enumerate(text.split("\n"), 1):
        line = raw.removesuffix("\r")
        if not line.strip() or line.startswith("#"):
            continue
        if PATH_RULE.match(line):
            current = blocks.setdefault(line, {})
            continue
        header = HEADER_RULE.match(line)
        if header is None or current is None:
            found.append(f"{name}:{number}: not a path at column 0 or an indented header")
            continue
        current[header[1].lower()] = header[2].strip()
        if "'unsafe-inline'" in header[2].lower():
            found.append(f"{name}:{number}: allows 'unsafe-inline'")
    every = blocks.get(EVERY_PATH)
    if every is None:
        found.append(f"{name}: no {EVERY_PATH} block, so some responses carry no header")
    else:
        found += [
            f"{name}: {EVERY_PATH} does not set {header}"
            for header in REQUIRED
            if header.lower() not in every
        ]
        if "content-security-policy" in every:
            found += policy_problems(every["content-security-policy"], name)
    cache = blocks.get(FONTS, {}).get("cache-control")
    if cache != FONT_CACHE:
        found.append(f"{name}: {FONTS} must set Cache-Control: {FONT_CACHE}")
    return found


def main(argv: list[str]) -> int:
    """Check the given file, or public/_headers."""
    path = Path(argv[0] if argv else DEFAULT_FILE)
    found = problems(path.read_text(encoding="utf-8"), str(path))
    for line in found:
        print(line, file=sys.stderr)
    if found:
        return 1
    print(
        f"{path}: every line is valid, {EVERY_PATH} sets the {len(REQUIRED)} headers and the"
        f" expected policy, and {FONTS} is cached for a year"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
