"""The vendored files are unchanged copies, byte for byte, of the commit named with each one.

A copy is refreshed only by copying the file again from its source and updating its line here.
"""

import hashlib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

RECORDED = {
    # Vercroft/burnbird at 72837e6f6e036764af19b3c9d40cb711e7632654, FSL-1.1-MIT (REUSE.toml).
    ".github/scripts/commit_policy.py": (
        "7e4d0eba90a600aad3e2a30cd66903a2e15217dd9a9b8660f7a64eff3a3e3d14"
    ),
    ".github/scripts/test_commit_policy.py": (
        "356f71d8ab48a07f0c8b2e37c024378507511fb192285143b249a816d586d1c9"
    ),
    # Vercroft/engineering-practices at 1e0ca286817707f9d55d65e7fedb089a20d0b703, MIT (REUSE.toml).
    "scripts/check-suppressions.sh": (
        "a7856f9f7ebdf38ea133f93adaa535d1ddd9f11d0c53695f4791268eb627faf4"
    ),
}


@pytest.mark.parametrize(("path", "sha256"), RECORDED.items())
def test_vendored_file_matches_its_recorded_sha256(path: str, sha256: str) -> None:
    assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha256
