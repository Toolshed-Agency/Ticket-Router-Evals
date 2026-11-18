"""ci.yml runs on every pull request, forks included: it must hold no secrets and write nothing."""

import re
import shutil
import subprocess

from tests import REPO_ROOT

CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"


def test_ci_uses_no_secrets() -> None:
    text = CI.read_text(encoding="utf-8")
    assert "secrets." not in text
    assert "pull_request_target" not in text


def test_ci_is_read_only() -> None:
    text = CI.read_text(encoding="utf-8")
    assert re.search(r"^permissions:\n  contents: read$", text, re.MULTILINE)
    assert "write" not in text


def test_actions_are_pinned_to_commits() -> None:
    # A moved tag must never change what CI runs (plan P1-D5).
    uses = re.findall(r"uses:\s*(\S+)", CI.read_text(encoding="utf-8"))
    assert uses
    assert all(re.search(r"@[0-9a-f]{40}$", u) for u in uses), uses


def test_actionlint_passes() -> None:
    actionlint = shutil.which("actionlint")
    assert actionlint, "actionlint is missing: run uv sync"
    result = subprocess.run([actionlint, str(CI)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
