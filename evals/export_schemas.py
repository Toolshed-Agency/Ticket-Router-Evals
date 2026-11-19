"""Writes the JSON Schemas of the public contracts to docs/schemas/ (plan P2-D5).

Run `uv run python -m evals.export_schemas` after changing a contract; a test fails until the
published files match the models. Changing a contract is a breaking change (CLAUDE.md).
"""

import json
from pathlib import Path
from typing import Final

from pydantic import BaseModel

from evals.dataset import TicketRecord
from harness.results import ResultsFile
from router.schema import RouterOutput

SCHEMAS: Final[dict[str, type[BaseModel]]] = {
    "ticket-record.schema.json": TicketRecord,
    "router-output.schema.json": RouterOutput,
    "results.schema.json": ResultsFile,
}

OUT_DIR: Final = Path(__file__).resolve().parents[1] / "docs" / "schemas"
# The draft Pydantic generates; named so a validator does not fall back to its own default.
DRAFT: Final = "https://json-schema.org/draft/2020-12/schema"


def render(model: type[BaseModel]) -> str:
    schema = {"$schema": DRAFT, **model.model_json_schema()}
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, model in SCHEMAS.items():
        (OUT_DIR / name).write_text(render(model), encoding="utf-8", newline="\n")
        print(f"wrote docs/schemas/{name}")


if __name__ == "__main__":
    main()
