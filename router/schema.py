"""What a Ledgerly router receives and returns (spec section 6). A public contract.

Validation is strict on purpose (plan P2-D2): a boolean must be true or false, a count must be an
integer, and enum values must match exactly. The schema-validity metric counts a sloppy answer as
invalid instead of quietly repairing it.
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, StringConstraints

from harness.contracts import Router

# The pattern repeats the stripped length check in the published JSON Schema, which cannot strip.
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, pattern=r"\S")]
StrippedStr = Annotated[str, StringConstraints(strip_whitespace=True)]


class Team(StrEnum):
    """The primary owner of a ticket."""

    BILLING = "billing"
    TECHNICAL = "technical"
    SALES = "sales"
    REFUNDS = "refunds"
    ACCOUNT_SECURITY = "account_security"
    OTHER = "other"


class Urgency(StrEnum):
    """P1 is an outage, data loss or a security incident; respond within 1 hour."""

    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"


class Language(StrEnum):
    """The language the customer wrote in (spec D2)."""

    EN = "en"
    UR = "ur"
    ROMAN_UR = "roman_ur"
    MIXED = "mixed"


class Channel(StrEnum):
    EMAIL = "email"
    WEB_FORM = "web_form"
    CHAT = "chat"


class Tier(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Ticket(BaseModel):
    """The ticket a router sees: its id and five input fields, never the answer key."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: NonEmptyStr
    channel: Channel
    subject: StrippedStr  # may be empty: chat tickets often have none
    body: NonEmptyStr
    customer_tier: Tier
    prior_tickets_7d: Annotated[StrictInt, Field(ge=0)]


class RouterOutput(BaseModel):
    """One routing decision. "P1 means escalate" is measured, not enforced (section 6)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    team: Team
    urgency: Urgency
    escalate_to_human: StrictBool
    issues: Annotated[list[NonEmptyStr], Field(min_length=1)]
    language: Language
    draft_reply: NonEmptyStr
    reasoning: NonEmptyStr


type LedgerlyRouter = Router[Ticket, RouterOutput]
