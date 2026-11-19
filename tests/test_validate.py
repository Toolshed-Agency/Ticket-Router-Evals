"""Whole-dataset checks against the mix targets (spec section 7)."""

from collections.abc import Iterator
from itertools import count
from typing import Any

from evals.dataset import CANARY, Slice, TicketRecord
from evals.mix import LANGUAGE_TOTALS, SLICE_SPLIT, TEAM_TOTALS
from evals.validate import validate_dataset
from router.schema import Language, Team


def _expand[T](totals: dict[T, int]) -> Iterator[T]:
    for key, n in totals.items():
        yield from [key] * n


def make(number: int, slice_: Slice, team: Team, language: Language, **meta: Any) -> TicketRecord:
    body = "Fake ticket text for a test."
    extra: dict[str, Any] = {"attack_goal": None, "sensitive_strings": []}
    urgency, escalate = "P3", False
    if slice_ is Slice.P1:
        urgency, escalate = "P1", True
    if slice_ is Slice.INJECTION:
        extra["attack_goal"] = {"urgency": "P1"}  # differs from the gold P3 below
    if slice_ is Slice.PII:
        body += " CNIC 00000-0000000-0"
        extra["sensitive_strings"] = ["00000-0000000-0"]
    return TicketRecord.model_validate(
        {
            "id": f"LDG-{number:04d}",
            "input": {
                "channel": "email",
                "subject": "Test",
                "body": body,
                "customer_tier": "free",
                "prior_tickets_7d": 0,
            },
            "gold": {
                "team": team,
                "urgency": urgency,
                "escalate_to_human": escalate,
                "issues": ["a test issue"],
                "language": language,
            },
            "meta": {"slice": slice_, "drafted_by": "handwritten"} | extra | meta,
            "canary": CANARY,
        }
    )


def dataset() -> tuple[list[TicketRecord], list[TicketRecord]]:
    """A valid 200-ticket dataset built straight from the targets."""
    teams, languages, numbers = _expand(TEAM_TOTALS), _expand(LANGUAGE_TOTALS), count(1)
    dev: list[TicketRecord] = []
    test: list[TicketRecord] = []
    for slice_, (n_dev, n_test) in SLICE_SPLIT.items():
        for split, n in ((dev, n_dev), (test, n_test)):
            split += [make(next(numbers), slice_, next(teams), next(languages)) for _ in range(n)]
    return dev, test


def relabel(r: TicketRecord, **changes: Any) -> TicketRecord:
    data = r.model_dump(mode="json")
    for key, value in changes.items():
        part, _, field = key.partition("__")
        if field:
            data[part][field] = value
        else:
            data[part] = value
    return TicketRecord.model_validate(data)


def test_targets_add_up() -> None:
    assert sum(d + t for d, t in SLICE_SPLIT.values()) == 200
    assert sum(d for d, _ in SLICE_SPLIT.values()) == 150
    assert sum(LANGUAGE_TOTALS.values()) == sum(TEAM_TOTALS.values()) == 200


def test_a_valid_dataset_has_no_problems() -> None:
    dev, test = dataset()
    assert validate_dataset(dev, test) == []


def test_reports_an_id_used_in_both_splits() -> None:
    dev, test = dataset()
    test[0] = relabel(test[0], id=dev[0].id)
    problems = validate_dataset(dev, test)
    assert len(problems) == 1
    assert dev[0].id in problems[0]


def test_reports_a_malformed_id() -> None:
    dev, test = dataset()
    dev[0] = relabel(dev[0], id="ABC-1")
    assert [p for p in validate_dataset(dev, test) if "ABC-1" in p] != []
    assert len(validate_dataset(dev, test)) == 1


def test_an_id_needs_ascii_digits() -> None:
    dev, test = dataset()
    dev[0] = relabel(dev[0], id="LDG-\u0661\u0662\u0663\u0664")
    problems = validate_dataset(dev, test)
    assert len(problems) == 1
    assert "LDG-0000" in problems[0]


def test_reports_a_missing_canary() -> None:
    dev, test = dataset()
    dev[3] = relabel(dev[3], canary=None)
    problems = validate_dataset(dev, test)
    assert len(problems) == 1
    assert "canary" in problems[0]


def test_reports_slice_counts_per_split() -> None:
    dev, test = dataset()
    dev.append(test.pop(0))  # a routine ticket moves from test to dev
    problems = validate_dataset(dev, test)
    assert len(problems) == 2
    assert all("routine" in p for p in problems)


def test_language_totals_have_a_tolerance_of_three() -> None:
    dev, test = dataset()
    roman = [i for i, r in enumerate(dev) if r.gold.language is Language.ROMAN_UR]
    mixed = [i for i, r in enumerate(dev) if r.gold.language is Language.MIXED]
    for i in roman[:2] + mixed[:1]:  # three more English tickets: inside the tolerance
        dev[i] = relabel(dev[i], gold__language="en")
    assert validate_dataset(dev, test) == []
    dev[mixed[1]] = relabel(dev[mixed[1]], gold__language="en")  # a fourth: outside
    problems = validate_dataset(dev, test)
    assert len(problems) == 1
    assert "en" in problems[0]
