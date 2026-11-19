"""The results file every run writes (spec section 6; plan P2-D4). A public contract.

Generic on purpose (spec D1): outputs are stored as JSON objects and verdicts carry their
criterion's name, so the format fits any routing task. Reproducing a number never needs a key
(spec S12): every output, the raw text of every invalid one, every judge verdict and every issue
coverage mark is here, and the aggregates can be recomputed from them.
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
    StrictFloat,
    StrictInt,
    StringConstraints,
    model_validator,
)

FORMAT_VERSION: Final = "1.0"

# Plan P2-D2: names and reasons are stripped and never empty. Raw model text is never stripped.
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"\S")]
Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
# Floats are strict (a string or a boolean is not a number) and always finite: NaN or infinity
# would be written as null, which reads as "not recorded".
NonNegative = Annotated[StrictFloat, Field(ge=0)]
Count = Annotated[StrictInt, Field(ge=0)]
Version = Annotated[str, Field(pattern=r"^[0-9]+\.[0-9]+$")]
SPLITS: Final = ("dev", "test")


class _Frozen(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


def _one_outcome(output: object, raw_text: object) -> None:
    if (output is None) == (raw_text is None):
        raise ValueError("exactly one of output and raw_text must be set")


class PriceEntry(_Frozen):
    """One line of the dated price table a run's costs were computed from."""

    provider: Text
    model: Text
    input_usd_per_million: NonNegative
    output_usd_per_million: NonNegative
    as_of: date
    source_url: HttpUrl


class Provenance(_Frozen):
    """Everything needed to say exactly what was run. `dataset_version` is set exactly when
    `split` is `dev` or `test`; it is null for a run on your own ticket file."""

    git_commit: Annotated[str, Field(pattern=r"^[0-9a-f]{40}$")]
    dataset_version: Version | None
    dataset_sha256: Sha256
    split: Text  # "dev", "test", or the path of a user's own ticket file
    router: Text
    switches_off: list[Text]
    prompt_sha256: Sha256 | None
    model: Text
    provider: Text
    request_settings: dict[str, JsonValue]
    judge_model: Text | None
    rubric_sha256: Sha256 | None
    prices: list[PriceEntry]

    @model_validator(mode="after")
    def _split_has_a_version(self) -> Self:
        if (self.split in SPLITS) != (self.dataset_version is not None):
            raise ValueError("dataset_version is set exactly when split is dev or test")
        return self


class Verdict(_Frozen):
    """The judge's pass or fail on one criterion, with a one-line reason (spec D6)."""

    criterion: Text
    passed: StrictBool
    reason: Text


class Repeat(_Frozen):
    """One extra run of a ticket (`--repeat`), used only by the consistency metric; cost, latency
    and schema validity use the first run. Exactly one of
    `output` (valid) and `raw_text` (invalid, kept exactly as received) is set."""

    output: dict[str, JsonValue] | None
    raw_text: str | None

    @model_validator(mode="after")
    def _check_outcome(self) -> Self:
        _one_outcome(self.output, self.raw_text)
        return self


class TicketResult(_Frozen):
    """One ticket's outcome. Exactly one of `output` (valid) and `raw_text` (invalid, kept
    exactly as received) is set; an invalid output is never `valid_first_try` and never
    `passed`. `coverage` holds one mark per gold issue, in order, on tickets with 2 or more
    gold issues. Each verdict's criterion appears once. The judge fields are null when the
    ticket was not judged."""

    ticket_id: Text
    output: dict[str, JsonValue] | None
    raw_text: str | None
    valid_first_try: StrictBool
    latency_ms: NonNegative
    input_tokens: Count | None  # None: the router bypassed the model client ("not recorded")
    output_tokens: Count | None
    cost_usd: NonNegative | None
    cached: StrictBool
    verdicts: list[Verdict]
    judge_input_tokens: Count | None
    judge_output_tokens: Count | None
    judge_cost_usd: NonNegative | None
    pii_leak: StrictBool | None
    coverage: Annotated[list[StrictBool], Field(min_length=1)] | None
    passed: StrictBool
    repeats: list[Repeat]

    @model_validator(mode="after")
    def _check_outcome(self) -> Self:
        _one_outcome(self.output, self.raw_text)
        # Spec section 8: an invalid output counts as wrong on every field.
        if self.raw_text is not None and (self.valid_first_try or self.passed):
            raise ValueError("an invalid output is never valid_first_try or passed")
        criteria = [v.criterion for v in self.verdicts]
        if len(criteria) != len(set(criteria)):
            raise ValueError("each criterion has one verdict")
        return self

    @property
    def judged(self) -> bool:
        return bool(self.verdicts) or self.coverage is not None or self.judge_cost_usd is not None


class Aggregate(_Frozen):
    """One metric for one group: "overall", "slice:<name>" or "language:<code>". The interval
    has both ends or neither; it needs a value, and then `ci_low <= value <= ci_high`."""

    metric: Text
    group: Annotated[str, Field(pattern=r"^(overall|slice:[a-z0-9_]+|language:[a-z0-9_]+)$")]
    value: StrictFloat | None
    n: Count
    ci_low: StrictFloat | None
    ci_high: StrictFloat | None

    @model_validator(mode="after")
    def _interval_contains_value(self) -> Self:
        value, low, high = self.value, self.ci_low, self.ci_high
        if (low is None) != (high is None):
            raise ValueError("an interval has both ends or neither")
        if low is None or high is None:
            return self
        if value is None:
            raise ValueError("an interval needs a value")
        if not low <= value <= high:
            raise ValueError("the interval must contain the value")
        return self


class ResultsFile(_Frozen):
    """One run. `ci_run_url` is set exactly when `source` is `ci`. Each ticket appears once.
    If any ticket was judged, the provenance names the judge model and the rubric hash."""

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
        ids = [t.ticket_id for t in self.tickets]
        if len(ids) != len(set(ids)):
            raise ValueError("each ticket appears once")
        judged = any(t.judged for t in self.tickets)
        if judged and (
            self.provenance.judge_model is None or self.provenance.rubric_sha256 is None
        ):
            raise ValueError("judged tickets need judge_model and rubric_sha256 in provenance")
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
    if isinstance(repeat, bool) or repeat < 1:
        raise ValueError("repeat must be a whole number, at least 1")
    stamp = created_at.astimezone(UTC).strftime("%Y%m%dt%H%M%Sz")
    where = split if split in ("dev", "test") else PurePath(split.replace("\\", "/")).stem
    named = {"router": router, "model": model, "split": where, **{s: s for s in switches_off}}
    empty = [name for name, text in named.items() if not _slug(text)]
    if empty:
        raise ValueError(f"nothing left after slugifying: {', '.join(empty)}")
    parts = [stamp, router, *(f"no-{s}" for s in sorted(switches_off)), model, where, f"x{repeat}"]
    return "-".join(map(_slug, parts))
