"""The Tamil font subset: the file is pinned, and it covers every Tamil character the pages use.

scripts/make-tamil-font.py makes the file from the recorded release; style.css's unicode-range must
name the same code points as the script, so the browser asks for the font only for what it holds.
"""

import hashlib
import importlib.util
import re
from pathlib import Path
from types import ModuleType

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.otBase import BaseTTXConverter

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "public" / "fonts" / "noto-sans-tamil-v2.004-tamil.woff2"
FONT_SHA256 = "a2a42b1f9b86daf2b3b0e5c04c8672a930af30a1bc1e4a5eaf54152e4dc3b9e0"
TAMIL_BLOCK = range(0x0B80, 0x0C00)
JOINERS = {0x200C, 0x200D}
# The features Tamil shaping uses in this font (script tml2), which the subset must keep.
SHAPING = {"GSUB": {"akhn", "haln", "psts", "abvs"}, "GPOS": {"abvm", "dist"}}


def _script() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "make_tamil_font", ROOT / "scripts" / "make-tamil-font.py"
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _code_points(ranges: str) -> set[int]:
    points: set[int] = set()
    for part in re.split(r"\s*,\s*", ranges.strip()):
        first, _, last = part.removeprefix("U+").partition("-")
        points.update(range(int(first, 16), int(last or first, 16) + 1))
    return points


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


def test_the_stylesheet_asks_for_the_font_only_for_what_the_script_keeps() -> None:
    css = (ROOT / "public" / "style.css").read_text(encoding="utf-8")
    face = re.search(r"@font-face\s*\{(.*?)\}", css, re.DOTALL)
    assert face is not None, "style.css has no @font-face"
    declared = re.search(r"unicode-range:\s*([^;]+);", face[1])
    assert declared is not None, "the @font-face has no unicode-range"
    assert _code_points(declared[1]) == _code_points(_script().UNICODES)
    assert f"/fonts/{FONT.name}" in face[1]
    assert "local(" not in face[1], "local() lets a page probe the visitor's installed fonts"
