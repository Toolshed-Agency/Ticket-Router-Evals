"""The results file format and run id (spec section 6; plan P2-D4)."""

import json
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import pytest
from pydantic import ValidationError

from harness.results import FORMAT_VERSION, ResultsFile, make_run_id

AT = datetime(2026, 12, 3, 10, 15, 0, tzinfo=UTC)


def test_run_id_matches_the_spec_example() -> None:
    assert make_run_id(AT, "v3", ["self_check"], "gemini-flash", "dev", 3) == (
        "20261203t101500z-v3-no-self-check-gemini-flash-dev-x3"
    )


def test_run_id_slugifies_models_and_paths() -> None:
    run_id = make_run_id(
        AT,
        "v3",
        ["policy_context", "injection_defense"],
        "models/gemini-3.5-flash-lite",
        "my files/Tickets.jsonl",
        1,
    )
    assert run_id == (
        "20261203t101500z-v3-no-injection-defense-no-policy-context"
        "-models-gemini-3-5-flash-lite-tickets-x1"
    )


def test_run_id_converts_to_utc() -> None:
    karachi = AT.astimezone(timezone(timedelta(hours=5)))
    assert make_run_id(karachi, "v1", [], "m", "test", 1).startswith("20261203t101500z-")


@pytest.mark.parametrize(
    ("router", "model", "split", "repeat"),
    [
        ("", "m", "dev", 1),
        ("v3", "///", "dev", 1),
        ("v3", "m", "data/---.jsonl", 1),
        ("v3", "m", "dev", True),
    ],
)
def test_run_id_rejects_an_empty_part_or_a_boolean_repeat(
    router: str, model: str, split: str, repeat: int
) -> None:
    with pytest.raises(ValueError, match=r"slugifying|whole number"):
        make_run_id(AT, router, [], model, split, repeat)


def test_run_id_needs_an_aware_time() -> None:
    with pytest.raises(ValueError, match="timezone"):
        make_run_id(datetime(2026, 12, 3), "v3", [], "m", "dev", 1)


def ticket(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "ticket_id": "LDG-0001",
        "output": {"team": "billing"},
        "raw_text": None,
        "valid_first_try": True,
        "latency_ms": 1820.5,
        "input_tokens": 1639,
        "output_tokens": 170,
        "cost_usd": 0.0,
        "cached": False,
        "verdicts": [{"criterion": "follows_policy", "passed": True, "reason": "Matches."}],
        "judge_input_tokens": 2210,
        "judge_output_tokens": 96,
        "judge_cost_usd": 0.0,
        "pii_leak": None,
        "coverage": None,
        "passed": True,
        "repeats": [],
    }
    return base | overrides


def with_provenance(**changes: Any) -> dict[str, Any]:
    r = results()
    return results(provenance=r["provenance"] | changes)


def results(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "format_version": FORMAT_VERSION,
        "run_id": "20261203t101500z-v3-gemini-flash-dev-x1",
        "created_at": "2026-12-03T10:15:00Z",
        "source": "ci",
        "ci_run_url": "https://github.com/Toolshed-Agency/Ticket-Router-Evals/actions/runs/1",
        "provenance": {
            "git_commit": "a" * 40,
            "dataset_version": "1.0",
            "dataset_sha256": "b" * 64,
            "split": "dev",
            "router": "v3",
            "switches_off": [],
            "prompt_sha256": "c" * 64,
            "model": "gemini-3.5-flash-lite",
            "provider": "google",
            "request_settings": {"temperature": 0},
            "judge_model": "gemini-3.1-flash-lite",
            "rubric_sha256": "d" * 64,
            "prices": [
                {
                    "provider": "google",
                    "model": "gemini-3.5-flash-lite",
                    "input_usd_per_million": 0.0,
                    "output_usd_per_million": 0.0,
                    "as_of": "2026-11-19",
                    "source_url": "https://ai.google.dev/pricing",
                }
            ],
        },
        "tickets": [ticket()],
        "aggregates": [
            {
                "metric": "p1_recall",
                "group": "overall",
                "value": 1.0,
                "n": 5,
                "ci_low": 0.478,
                "ci_high": 1.0,
            }
        ],
    }
    return base | overrides


def aggregate(**overrides: Any) -> dict[str, Any]:
    base = {"metric": "x", "group": "overall", "value": 0.4, "n": 5, "ci_low": 0.2, "ci_high": 0.6}
    return base | overrides


def test_a_full_results_file_round_trips() -> None:
    parsed = ResultsFile.model_validate(results())
    assert ResultsFile.model_validate_json(parsed.model_dump_json()) == parsed


def test_a_whole_number_is_a_valid_float() -> None:
    # JSON writers often write 0.0 as 0; strict floats still accept integers.
    parsed = ResultsFile.model_validate_json(json.dumps(results(tickets=[ticket(cost_usd=0)])))
    assert parsed.tickets[0].cost_usd == 0


def test_an_aggregate_without_a_value_has_no_interval() -> None:
    parsed = ResultsFile.model_validate(
        results(aggregates=[aggregate(value=None, ci_low=None, ci_high=None, n=0)])
    )
    assert parsed.aggregates[0].value is None


@pytest.mark.parametrize("group", ["overall", "slice:p1", "language:roman_ur"])
def test_aggregate_groups(group: str) -> None:
    assert ResultsFile.model_validate(results(aggregates=[aggregate(group=group)]))


@pytest.mark.parametrize(
    "bad",
    [
        results(ci_run_url=None),  # a ci run must link its public log
        results(source="local", ci_run_url="https://example.com/run"),  # only ci runs have one
        results(tickets=[ticket(output={"team": "billing"}, raw_text="x")]),  # not both
        results(tickets=[ticket(output=None, raw_text=None)]),  # not neither
        results(tickets=[ticket(coverage=[])]),  # one mark per gold issue, so never empty
        results(tickets=[ticket(coverage=["yes"])]),
        results(tickets=[ticket(judge_cost_usd=-0.01)]),
        results(tickets=[ticket(repeats=[{"output": None, "raw_text": None}])]),  # not neither
        results(tickets=[ticket(repeats=[{"output": {"team": "x"}, "raw_text": "x"}])]),  # not both
        results(tickets=[ticket(ticket_id="  ")]),  # strings are stripped and never empty
        results(
            tickets=[
                ticket(verdicts=[{"criterion": "follows_policy", "passed": True, "reason": ""}])
            ]
        ),
        with_provenance(dataset_version="v1"),
        with_provenance(model=""),
        results(tickets=[ticket(cached="no")]),
        results(
            aggregates=[
                {
                    "metric": "x",
                    "group": "overall",
                    "value": 0.4,
                    "n": 5,
                    "ci_low": 0.5,
                    "ci_high": 1.0,
                }
            ]
        ),
        # An invalid output is wrong on every field (spec section 8): never valid, never passed.
        results(tickets=[ticket(output=None, raw_text="x", valid_first_try=True, passed=False)]),
        results(tickets=[ticket(output=None, raw_text="x", valid_first_try=False, passed=True)]),
        results(tickets=[ticket(), ticket()]),  # the same ticket twice would count twice
        results(tickets=[ticket(latency_ms=float("nan"))]),  # numbers must be real numbers
        results(tickets=[ticket(cost_usd=float("inf"))]),
        results(tickets=[ticket(cost_usd="0.5")]),  # floats are strict, like the schema
        results(tickets=[ticket(latency_ms=True)]),
        results(
            tickets=[
                ticket(
                    verdicts=[
                        {"criterion": "follows_policy", "passed": True, "reason": "Matches."},
                        {"criterion": "follows_policy", "passed": False, "reason": "Twice."},
                    ]
                )
            ]
        ),
        results(aggregates=[aggregate(value=None, ci_low=0.9, ci_high=0.1)]),
        results(aggregates=[aggregate(ci_low=0.6, ci_high=0.2)]),
        results(aggregates=[aggregate(ci_high=None)]),  # both ends or neither
        results(aggregates=[aggregate(value=None)]),  # no value, no interval
        results(aggregates=[aggregate(value=float("nan"))]),
        results(aggregates=[aggregate(group="everything")]),
        with_provenance(split="dev", dataset_version=None),  # a split has a dataset version
        with_provenance(split="my.jsonl", dataset_version="1.0"),  # your own file has none
        with_provenance(dataset_version="\u0661.\u0660"),  # digits are ASCII
        with_provenance(judge_model=None),  # judged tickets name their judge
        with_provenance(rubric_sha256=None),
        results(format_version="2.0"),
        results(run_id="Has Spaces"),
        results(created_at="2026-12-03T10:15:00"),  # no timezone
    ],
)
def test_invalid_results_file(bad: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ResultsFile.model_validate(bad)


def test_an_invalid_output_keeps_its_raw_text() -> None:
    parsed = ResultsFile.model_validate(
        results(
            tickets=[ticket(output=None, raw_text="not json", valid_first_try=False, passed=False)]
        )
    )
    assert parsed.tickets[0].raw_text == "not json"


def test_raw_text_is_kept_exactly() -> None:
    # Unlike names and reasons, a model's raw answer is evidence: never stripped.
    parsed = ResultsFile.model_validate(
        results(tickets=[ticket(output=None, raw_text="  \n", valid_first_try=False, passed=False)])
    )
    assert parsed.tickets[0].raw_text == "  \n"


def test_an_invalid_repeat_keeps_its_raw_text() -> None:
    repeats = [{"output": {"team": "billing"}, "raw_text": None}, {"output": None, "raw_text": "{"}]
    parsed = ResultsFile.model_validate(results(tickets=[ticket(repeats=repeats)]))
    assert parsed.tickets[0].repeats[1].raw_text == "{"


def test_coverage_keeps_one_mark_per_gold_issue() -> None:
    # The share is recomputed from the marks by rescore; the marks are the evidence.
    parsed = ResultsFile.model_validate(results(tickets=[ticket(coverage=[True, False, True])]))
    assert parsed.tickets[0].coverage == [True, False, True]


def test_a_run_on_your_own_tickets_has_no_dataset_version() -> None:
    parsed = ResultsFile.model_validate(with_provenance(dataset_version=None, split="my.jsonl"))
    assert parsed.provenance.dataset_version is None


def test_an_unjudged_ticket_has_no_judge_cost() -> None:
    unjudged = ticket(verdicts=[], judge_input_tokens=None, judge_output_tokens=None)
    parsed = ResultsFile.model_validate(results(tickets=[unjudged | {"judge_cost_usd": None}]))
    assert parsed.tickets[0].judge_cost_usd is None
