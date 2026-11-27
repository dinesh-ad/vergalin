"""The Tamil font subset: the file is pinned, and it covers every Tamil character the pages use.

scripts/make-tamil-font.py makes the file from the recorded release.
"""

import hashlib
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otBase import BaseTTXConverter

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "public" / "fonts" / "noto-sans-tamil-v2.004-tamil.woff2"
FONT_SHA256 = "a2a42b1f9b86daf2b3b0e5c04c8672a930af30a1bc1e4a5eaf54152e4dc3b9e0"
TAMIL_BLOCK = range(0x0B80, 0x0C00)
JOINERS = {0x200C, 0x200D}
# The features Tamil shaping uses in this font (script tml2), which the subset must keep.
SHAPING = {"GSUB": {"akhn", "haln", "psts", "abvs"}, "GPOS": {"abvm", "dist"}}


def test_the_font_is_the_pinned_subset() -> None:
    assert hashlib.sha256(FONT.read_bytes()).hexdigest() == FONT_SHA256


def test_the_font_covers_every_tamil_character_the_pages_use() -> None:
    used = {
        ord(char)
        for path in (ROOT / "public").rglob("*")
        if path.suffix in {".html", ".css"}
        for char in path.read_text(encoding="utf-8")
        if ord(char) in TAMIL_BLOCK or ord(char) in JOINERS
    }
    assert used, "no page uses Tamil, so the font is not needed"
    cmap = TTFont(FONT).getBestCmap()
    assert cmap is not None, "the font has no Unicode cmap"
    missing = sorted(hex(point) for point in used - set(cmap))
    assert not missing, f"the subset lacks {missing}"


def test_the_font_keeps_the_tamil_shaping_features() -> None:
    font = TTFont(FONT)
    for tag, needed in SHAPING.items():
        table = font[tag]
        assert isinstance(table, BaseTTXConverter)
        kept = {record.FeatureTag for record in table.table.FeatureList.FeatureRecord}
        assert needed <= kept, f"{tag} lost {sorted(needed - kept)}"
