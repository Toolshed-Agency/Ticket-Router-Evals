"""The harness boundary (spec D1): harness/ stays free of anything Ledgerly-specific."""

from pathlib import Path

import pytest

from tests import REPO_ROOT
from tests.boundary_check import find_violations


def write(tmp_path: Path, source: str) -> Path:
    """Write `source` as harness/mod.py under tmp_path and return the harness folder."""
    root = tmp_path / "harness"
    root.mkdir()
    (root / "mod.py").write_text(source, encoding="utf-8")
    return root


@pytest.mark.parametrize(
    "source",
    [
        "import router",
        "from evals.metrics import x",
        "import evals.metrics as m",
        "import importlib\nimportlib.import_module('router.v1')",
        "__import__('evals')",
        "p = 'data/tickets_dev.jsonl'",
        "p = 'data\\\\tickets_dev.jsonl'",
        "from pathlib import Path\np = Path('context') / 'policies.md'",
        "from pathlib import Path\np = Path('.') / 'data'",
        "open('data')",
        "# Ledgerly-specific shortcut",
        "def f(:\n",
    ],
)
def test_flags(tmp_path: Path, source: str) -> None:
    assert len(find_violations(write(tmp_path, source))) == 1


@pytest.mark.parametrize(
    "source",
    [
        "x = {}\ny = x['data']",
        "p = 'metadata/x'",
        "d = 'dataset'",
        "import json",
    ],
)
def test_allows(tmp_path: Path, source: str) -> None:
    assert find_violations(write(tmp_path, source)) == []


def test_reports_file_and_line(tmp_path: Path) -> None:
    [violation] = find_violations(write(tmp_path, "import json\nimport router"))
    assert (violation.path.name, violation.line) == ("mod.py", 2)


def test_empty_root_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"no \.py files"):
        find_violations(tmp_path)


def test_harness_respects_the_boundary() -> None:
    assert find_violations(REPO_ROOT / "harness") == []
