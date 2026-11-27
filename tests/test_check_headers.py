"""scripts/check-headers.py, run as the hook runs it, on the real file and on broken copies."""

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


def test_a_policy_without_default_src_none_fails(tmp_path: Path) -> None:
    text = HEADERS.read_text().replace("default-src 'none'", "default-src 'self'")
    code, output = check(variant(tmp_path, text))
    assert (code, "default-src 'none'" in output) == (1, True)


@pytest.mark.parametrize("bad", ["*/", "X-Frame-Options: DENY", "  not a header"])
def test_a_malformed_line_fails(tmp_path: Path, bad: str) -> None:
    code, output = check(variant(tmp_path, HEADERS.read_text() + bad + "\n"))
    assert (code, "not a path at column 0 or an indented header" in output) == (1, True)


def test_headers_on_another_path_only_fail(tmp_path: Path) -> None:
    code, output = check(variant(tmp_path, HEADERS.read_text().replace("/*\n", "/privacy\n")))
    assert (code, "no /* block" in output) == (1, True)
