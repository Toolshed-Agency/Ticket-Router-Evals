"""The results file every run writes (spec section 6; plan P2-D4). A public contract.

Generic on purpose (spec D1): outputs are stored as JSON objects and verdicts carry their
criterion's name, so the format fits any routing task. Reproducing a number never needs a key:
every raw output and judge verdict is here, and the aggregates can be recomputed from them.
"""

import re
from collections.abc import Sequence
from datetime import UTC, date, datetime
from pathlib import PurePath
from typing import Annotated, Final, Literal, Self

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    JsonValue,
    StrictBool,
    StrictInt,
    model_validator,
)

FORMAT_VERSION: Final = "1.0"

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
NonNegative = Annotated[float, Field(ge=0)]
Count = Annotated[StrictInt, Field(ge=0)]


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class PriceEntry(_Frozen):
    """One line of the dated price table a run's costs were computed from."""

    provider: str
    model: str
    input_usd_per_million: NonNegative
    output_usd_per_million: NonNegative
    as_of: date
    source_url: HttpUrl


class Provenance(_Frozen):
    """Everything needed to say exactly what was run."""

    git_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    dataset_version: str
    dataset_sha256: Sha256
    split: str  # "dev", "test", or the path of a user's own ticket file
    router: str
    switches_off: list[str]
    prompt_sha256: Sha256 | None
    model: str
    provider: str
    request_settings: dict[str, JsonValue]
    judge_model: str | None
    rubric_sha256: Sha256 | None
    prices: list[PriceEntry]


class Verdict(_Frozen):
    criterion: str
    passed: StrictBool
    reason: str


class TicketResult(_Frozen):
    """One ticket's outcome. Exactly one of `output` (valid) and `raw_text` (invalid) is set."""

    ticket_id: str
    output: dict[str, JsonValue] | None
    raw_text: str | None
    valid_first_try: StrictBool
    latency_ms: NonNegative
    input_tokens: Count | None  # None: the router bypassed the model client ("not recorded")
    output_tokens: Count | None
    cost_usd: NonNegative | None
    cached: StrictBool
    verdicts: list[Verdict]
    pii_leak: StrictBool | None
    issue_coverage: Annotated[float, Field(ge=0, le=1)] | None
    passed: StrictBool
    repeats: list[dict[str, JsonValue] | None]

    @model_validator(mode="after")
    def _one_outcome(self) -> Self:
        if (self.output is None) == (self.raw_text is None):
            raise ValueError("exactly one of output and raw_text must be set")
        return self


class Aggregate(_Frozen):
    """One metric for one group: "overall", "slice:<name>" or "language:<code>"."""

    metric: str
    group: str
    value: float | None
    n: Count
    ci_low: float | None
    ci_high: float | None

    @model_validator(mode="after")
    def _interval_contains_value(self) -> Self:
        value, low, high = self.value, self.ci_low, self.ci_high
        if value is not None and low is not None and high is not None and not low <= value <= high:
            raise ValueError("the interval must contain the value")
        return self


class ResultsFile(_Frozen):
    format_version: Literal["1.0"]
    run_id: Annotated[str, Field(pattern=r"^[a-z0-9-]+$")]
    created_at: AwareDatetime
    source: Literal["ci", "local"]
    ci_run_url: HttpUrl | None
    provenance: Provenance
    tickets: list[TicketResult]
    aggregates: list[Aggregate]

    @model_validator(mode="after")
    def _ci_links_its_log(self) -> Self:
        # Published numbers come only from CI runs, each linked to its public log (section 11).
        if (self.source == "ci") != (self.ci_run_url is not None):
            raise ValueError("ci_run_url is set exactly when source is ci")
        return self


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def make_run_id(
    created_at: datetime,
    router: str,
    switches_off: Sequence[str],
    model: str,
    split: str,
    repeat: int,
) -> str:
    """`<utc time>-<router>[-no-<switch>...]-<model>-<split or file stem>-x<repeat>`, slugified."""
    if created_at.tzinfo is None or created_at.utcoffset() is None:
        raise ValueError("created_at needs a timezone")
    if repeat < 1:
        raise ValueError("repeat must be at least 1")
    stamp = created_at.astimezone(UTC).strftime("%Y%m%dt%H%M%Sz")
    where = split if split in ("dev", "test") else PurePath(split.replace("\\", "/")).stem
    parts = [stamp, router, *(f"no-{s}" for s in sorted(switches_off)), model, where, f"x{repeat}"]
    return "-".join(slug for slug in map(_slug, parts) if slug)
