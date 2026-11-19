"""The JSON Schemas in docs/schemas/ match the models (plan P2-D5)."""

import json
from collections.abc import Iterator
from typing import Any

import pytest

from evals.export_schemas import SCHEMAS, render
from tests import REPO_ROOT


def test_all_three_contracts_are_published() -> None:
    assert set(SCHEMAS) == {
        "ticket-record.schema.json",
        "router-output.schema.json",
        "results.schema.json",
    }


def _strings(node: object) -> Iterator[dict[str, Any]]:
    if isinstance(node, dict):
        if node.get("type") == "string":
            yield node
        for value in node.values():
            yield from _strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _strings(value)


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_a_required_string_cannot_be_blank_in_the_schema_either(name: str) -> None:
    # The models strip strings before checking length; a schema cannot strip, so "  " would pass
    # a minLength check that the loader then rejects. A pattern needing one visible character
    # makes the published contract reject what the code rejects.
    schema = json.loads(render(SCHEMAS[name]))
    # A string with a format (a URL) is already checked by that format.
    non_empty = [s for s in _strings(schema) if s.get("minLength", 0) >= 1 and "format" not in s]
    assert non_empty
    assert all(s.get("pattern") == r"\S" for s in non_empty)


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_published_schema_matches_the_model(name: str) -> None:
    published = (REPO_ROOT / "docs" / "schemas" / name).read_text(encoding="utf-8")
    assert published == render(SCHEMAS[name]), (
        f"docs/schemas/{name} is out of date: run `uv run python -m evals.export_schemas`"
    )
