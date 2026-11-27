#!/usr/bin/env python3
"""Make the site's Tamil font subset from the Noto Sans Tamil release, the same way every time.

The release zip is NotoSansTamil-v2.004.zip from https://github.com/notofonts/tamil/releases; the
script checks its sha256 and the source TTF's, then keeps the whole Tamil block, ZWNJ and ZWJ and
every OpenType layout feature, and writes WOFF2. tests/test_tamil_font.py pins the result.

Usage: make-tamil-font.py <path to NotoSansTamil-v2.004.zip>
"""

import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Final

from fontTools import subset

ZIP_SHA256: Final = "f8284e0f200a7f29a439b4ec88280d864b2b31f8479111c5b658ba6da38b3005"
SOURCE: Final = "NotoSansTamil/full/ttf/NotoSansTamil-Regular.ttf"
SOURCE_SHA256: Final = "0afbc221964b6048c6d771c525be474d21b288a621dce0fafedd695cc5c98e4e"
OUTPUT: Final = (
    Path(__file__).resolve().parents[1] / "public/fonts/noto-sans-tamil-v2.004-tamil.woff2"
)
# The Tamil block, ZERO WIDTH NON-JOINER and ZERO WIDTH JOINER; style.css's unicode-range matches.
UNICODES: Final = "U+0B80-0BFF,U+200C,U+200D"
OPTIONS: Final = (
    f"--unicodes={UNICODES}",
    "--layout-features=*",
    "--name-IDs=*",
    "--flavor=woff2",
)


def sha256(data: bytes) -> str:
    """Return the hex sha256 of the bytes."""
    return hashlib.sha256(data).hexdigest()


def main(argv: list[str]) -> int:
    """Check the release zip, then write the subset."""
    if len(argv) != 1:
        print("usage: make-tamil-font.py <path to NotoSansTamil-v2.004.zip>", file=sys.stderr)
        return 2
    archive = Path(argv[0]).read_bytes()
    if sha256(archive) != ZIP_SHA256:
        print("make-tamil-font: the zip is not the recorded v2.004 release", file=sys.stderr)
        return 1
    with zipfile.ZipFile(argv[0]) as release:
        source = release.read(SOURCE)
    if sha256(source) != SOURCE_SHA256:
        print("make-tamil-font: the source TTF is not the recorded one", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as work:
        ttf = Path(work) / "NotoSansTamil-Regular.ttf"
        ttf.write_bytes(source)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        subset.main([str(ttf), *OPTIONS, f"--output-file={OUTPUT}"])
    print(f"{OUTPUT.name}: {OUTPUT.stat().st_size} bytes, sha256 {sha256(OUTPUT.read_bytes())}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
