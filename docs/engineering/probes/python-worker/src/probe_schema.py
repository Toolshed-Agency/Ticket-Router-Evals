"""The router output fields (spec section 6) as the probes request them.

Probe only: the real schema is written test-first in phase 2.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProbeOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    team: Literal["billing", "technical", "sales", "refunds", "account_security", "other"]
    urgency: Literal["P1", "P2", "P3", "P4"]
    escalate_to_human: bool
    issues: list[str] = Field(min_length=1)
    language: Literal["en", "ur", "roman_ur", "mixed"]
    draft_reply: str
    reasoning: str


PROBE_OUTPUT_JSON_SCHEMA: dict[str, object] = ProbeOutput.model_json_schema()
