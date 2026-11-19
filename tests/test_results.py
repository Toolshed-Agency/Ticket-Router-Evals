"""The results file format and run id (spec section 6; plan P2-D4)."""

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
            "judge_model": None,
            "rubric_sha256": None,
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


def test_a_full_results_file_round_trips() -> None:
    parsed = ResultsFile.model_validate(results())
    assert ResultsFile.model_validate_json(parsed.model_dump_json()) == parsed


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
        results(tickets=[ticket(output=None, raw_text="not json", valid_first_try=False)])
    )
    assert parsed.tickets[0].raw_text == "not json"


def test_raw_text_is_kept_exactly() -> None:
    # Unlike names and reasons, a model's raw answer is evidence: never stripped.
    parsed = ResultsFile.model_validate(
        results(tickets=[ticket(output=None, raw_text="  \n", valid_first_try=False)])
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
