import subprocess
import sys
from pathlib import Path

import pytest

from tests import REPO_ROOT


@pytest.mark.parametrize("name", ["harness", "router", "evals"])
def test_package_resolves_to_this_repo(name: str, tmp_path: Path) -> None:
    # `evals` is also the name of OpenAI's package on PyPI; a stray install must never shadow ours.
    # pytest puts the repo root first on sys.path, which would hide a clash, so check from a fresh
    # interpreter started outside the repo: that is how the installed command will import it.
    result = subprocess.run(
        [sys.executable, "-c", f"import {name}; print({name}.__file__)"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    assert Path(result.stdout.strip()).resolve().parent == REPO_ROOT / name
