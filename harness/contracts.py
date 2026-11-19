"""The router interface every router version implements (spec section 6).

Generic over its ticket and output types, so the harness never needs to know a task's own
shapes (spec D1). Each task binds the types on its own side of the boundary.
"""

from typing import Protocol


class Router[TicketT, OutputT](Protocol):
    """Anything with a name that turns one ticket into one output."""

    @property
    def name(self) -> str:
        """Read-only, so a class attribute, a frozen dataclass field or a property all fit."""
        ...

    def predict(self, ticket: TicketT) -> OutputT:
        """Route one ticket. Raise `InvalidOutput` when no valid output can be produced."""
        ...


class InvalidOutput(Exception):
    """A router could not produce a valid output. Counts as wrong on every field (section 8)."""

    def __init__(self, raw_text: str) -> None:
        super().__init__("router produced no valid output")
        self.raw_text = raw_text
