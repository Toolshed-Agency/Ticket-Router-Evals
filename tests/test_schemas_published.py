"""The JSON Schemas in docs/schemas/ match the models (plan P2-D5)."""

import pytest

from evals.export_schemas import SCHEMAS, render
from tests import REPO_ROOT


def test_all_three_contracts_are_published() -> None:
    assert set(SCHEMAS) == {
        "ticket-record.schema.json",
        "router-output.schema.json",
        "results.schema.json",
    }


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_published_schema_matches_the_model(name: str) -> None:
    published = (REPO_ROOT / "docs" / "schemas" / name).read_text(encoding="utf-8")
    assert published == render(SCHEMAS[name]), (
        f"docs/schemas/{name} is out of date: run `uv run python -m evals.export_schemas`"
    )
