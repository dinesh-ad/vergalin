#!/usr/bin/env python3
"""Check public/_headers: its syntax, the seven security headers on every path, and the policy.

The host rejects the whole file when one line is malformed, so every non-empty line that does not
start with "#" must be a path at column 0 (starting with "/" or "https://") or an indented
"Name: value". The "/*" block must set each of the seven headers, and its Content-Security-Policy
must start from default-src 'none' and never allow 'unsafe-inline'.

Usage: check-headers.py [path]   (default: public/_headers)
"""

import re
import sys
from pathlib import Path
from typing import Final

DEFAULT_FILE: Final = "public/_headers"
EVERY_PATH: Final = "/*"
REQUIRED: Final = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Strict-Transport-Security",
    "Content-Security-Policy",
)
PATH_RULE: Final = re.compile(r"^(/|https?://)\S*$")
HEADER_RULE: Final = re.compile(r"^[ \t]+([!#$%&'*+.^_`|~0-9A-Za-z-]+):(.*\S)")


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
        return [*found, f"{name}: no {EVERY_PATH} block, so some responses carry no header"]
    found += [
        f"{name}: {EVERY_PATH} does not set {header}"
        for header in REQUIRED
        if header.lower() not in every
    ]
    policy = every.get("content-security-policy", "")
    directives = [part.strip().lower() for part in policy.split(";")]
    if policy and "default-src 'none'" not in directives:
        found.append(f"{name}: the Content-Security-Policy does not start from default-src 'none'")
    return found


def main(argv: list[str]) -> int:
    """Check the given file, or public/_headers."""
    path = Path(argv[0] if argv else DEFAULT_FILE)
    found = problems(path.read_text(encoding="utf-8"), str(path))
    for line in found:
        print(line, file=sys.stderr)
    if found:
        return 1
    print(f"{path}: every line is valid, and {EVERY_PATH} sets the {len(REQUIRED)} headers")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
