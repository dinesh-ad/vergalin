"""scripts/check-headers.py, run as the hook runs it, on the real file and on broken copies."""

import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / "scripts" / "check-headers.py"
HEADERS = ROOT / "public" / "_headers"
REQUIRED = (
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Permissions-Policy",
    "Cross-Origin-Opener-Policy",
    "Strict-Transport-Security",
    "Content-Security-Policy",
)


def check(path: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, "-B", str(CHECK), str(path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return result.returncode, result.stdout + result.stderr


def variant(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "_headers"
    path.write_text(text)
    return path


def test_the_real_file_passes() -> None:
    assert check(HEADERS)[0] == 0


@pytest.mark.parametrize("header", REQUIRED)
def test_each_missing_header_fails(tmp_path: Path, header: str) -> None:
    lines = HEADERS.read_text().splitlines(keepends=True)
    kept = [line for line in lines if not line.strip().startswith(header + ":")]
    assert len(kept) == len(lines) - 1, f"{header} is not on exactly one line of the real file"
    code, output = check(variant(tmp_path, "".join(kept)))
    assert (code, f"does not set {header}" in output) == (1, True)


@pytest.mark.parametrize("source", ["style-src", "script-src"])
def test_unsafe_inline_fails(tmp_path: Path, source: str) -> None:
    text = HEADERS.read_text().replace("style-src 'self'", f"{source} 'self' 'unsafe-inline'")
    code, output = check(variant(tmp_path, text))
    assert (code, "allows 'unsafe-inline'" in output) == (1, True)


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("default-src 'none'", "default-src 'self'", "has default-src 'self', expected 'none'"),
        ("font-src 'self'; ", "", "has font-src (none), expected 'self'"),
        ("img-src 'self'", "img-src 'self' data:", "has img-src 'self' data:, expected 'self'"),
        (
            "base-uri 'none'",
            "base-uri 'none'; connect-src *",
            "has connect-src *, expected (none)",
        ),
    ],
)
def test_a_policy_other_than_the_expected_one_fails(
    tmp_path: Path, old: str, new: str, message: str
) -> None:
    text = HEADERS.read_text()
    assert text.count(old) == 1
    code, output = check(variant(tmp_path, text.replace(old, new)))
    assert (code, message in output) == (1, True)


def test_the_policy_may_list_its_directives_in_another_order(tmp_path: Path) -> None:
    text = HEADERS.read_text().replace(
        "default-src 'none'; style-src 'self';", "style-src  'self' ;default-src 'none';"
    )
    assert check(variant(tmp_path, text))[0] == 0


@pytest.mark.parametrize(
    "cache", ["public, max-age=3600", "no-store", None], ids=["short", "no-store", "missing"]
)
def test_the_font_block_must_cache_for_a_year(tmp_path: Path, cache: str | None) -> None:
    line = "  Cache-Control: public, max-age=31536000, immutable\n"
    text = HEADERS.read_text()
    assert text.count(line) == 1
    replacement = "" if cache is None else f"  Cache-Control: {cache}\n"
    code, output = check(variant(tmp_path, text.replace(line, replacement)))
    assert (code, "/fonts/* must set Cache-Control" in output) == (1, True)


@pytest.mark.parametrize("bad", ["*/", "X-Frame-Options: DENY", "  not a header"])
def test_a_malformed_line_fails(tmp_path: Path, bad: str) -> None:
    code, output = check(variant(tmp_path, HEADERS.read_text() + bad + "\n"))
    assert (code, "not a path at column 0 or an indented header" in output) == (1, True)


def test_headers_on_another_path_only_fail(tmp_path: Path) -> None:
    text = re.sub(r"^/\*$", "/privacy", HEADERS.read_text(), flags=re.MULTILINE)
    code, output = check(variant(tmp_path, text))
    assert (code, "no /* block" in output) == (1, True)
