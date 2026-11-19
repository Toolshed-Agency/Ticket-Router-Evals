"""Keys live only in .env (gitignored); the repo carries names, never values (spec section 3)."""

import re
import subprocess
from pathlib import Path

import pytest

from tests import REPO_ROOT


def git(*args: str) -> subprocess.CompletedProcess[str]:
    # No check=True: some tests read the exit code. A missing git raises, so tests fail, never skip.
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True)


# .dev.vars is where `wrangler dev` keeps a Worker's local secrets (the demo, phase 9).
@pytest.mark.parametrize(
    "name", [".env", ".env.local", ".env.production", ".dev.vars", ".dev.vars.production"]
)
def test_env_files_are_ignored(name: str) -> None:
    assert git("check-ignore", "-q", name).returncode == 0


def test_env_example_is_tracked() -> None:
    assert git("check-ignore", "-q", ".env.example").returncode == 1
    assert git("ls-files", ".env.example").stdout.strip() == ".env.example"


def test_env_example_holds_names_only() -> None:
    for line in (REPO_ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            assert re.fullmatch(r"[A-Z][A-Z0-9_]*=", line), line


def test_no_env_file_is_tracked() -> None:
    listed = git("ls-files")
    # A failed or empty listing would make the check below pass with nothing checked.
    assert listed.returncode == 0, listed.stderr
    names = {Path(p).name for p in listed.stdout.splitlines()}
    assert names, "git ls-files listed nothing"
    secret_files = {
        n
        for n in names - {".env.example"}
        if n.startswith((".env", ".dev.vars")) or n.endswith(".env")
    }
    assert secret_files == set()
