"""The router's input and output contracts (spec section 6; plan P2-D2)."""

import pytest
from pydantic import ValidationError

from router.schema import RouterOutput, Team, Ticket, Urgency

VALID = {
    "team": "billing",
    "urgency": "P2",
    "escalate_to_human": False,
    "issues": ["card charged twice"],
    "language": "roman_ur",
    "draft_reply": "Shukriya, hum check kar rahe hain.",
    "reasoning": "A duplicate charge is a billing matter.",
}

TICKET = {
    "id": "LDG-0001",
    "channel": "chat",
    "subject": "card do dafa charge hua",
    "body": "Mera card do dafa charge ho gaya hai.",
    "customer_tier": "pro",
    "prior_tickets_7d": 2,
}


def test_valid_output() -> None:
    output = RouterOutput.model_validate(VALID)
    assert output.team is Team.BILLING
    assert output.urgency is Urgency.P2


@pytest.mark.parametrize(
    "change",
    [
        {"urgency": "p1"},  # no case folding
        {"team": "Billing"},
        {"escalate_to_human": "yes"},  # strict boolean
        {"escalate_to_human": 1},
        {"issues": []},  # at least one issue
        {"issues": ["  "]},  # whitespace-only is empty
        {"draft_reply": " "},
        {"reasoning": ""},
        {"language": "urdu"},
        {"escalate_to_humen": True},  # misspelled extra field
    ],
)
def test_invalid_output(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RouterOutput.model_validate(VALID | change)


def test_missing_field_is_invalid() -> None:
    without_reasoning = {k: v for k, v in VALID.items() if k != "reasoning"}
    with pytest.raises(ValidationError):
        RouterOutput.model_validate(without_reasoning)


def test_strings_are_stripped() -> None:
    output = RouterOutput.model_validate(VALID | {"issues": ["  card charged twice "]})
    assert output.issues == ["card charged twice"]


def test_valid_ticket() -> None:
    assert Ticket.model_validate(TICKET).prior_tickets_7d == 2


@pytest.mark.parametrize("bad", ["2", -1, 2.0])
def test_ticket_rejects_string_negative_or_float_count(bad: object) -> None:
    with pytest.raises(ValidationError):
        Ticket.model_validate(TICKET | {"prior_tickets_7d": bad})


def test_empty_subject_is_allowed() -> None:
    # Chat tickets often have no subject.
    assert Ticket.model_validate(TICKET | {"subject": ""}).subject == ""


@pytest.mark.parametrize("change", [{"body": "  "}, {"id": ""}, {"channel": "phone"}])
def test_invalid_ticket(change: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Ticket.model_validate(TICKET | change)


def test_models_are_frozen() -> None:
    ticket = Ticket.model_validate(TICKET)
    with pytest.raises(ValidationError):
        ticket.body = "changed"  # type: ignore[misc]
