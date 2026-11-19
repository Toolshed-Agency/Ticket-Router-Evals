"""The generic router interface (spec section 6), and that Ledgerly routers fit it."""

from dataclasses import dataclass

from harness.contracts import InvalidOutput, Router
from router.schema import LedgerlyRouter, RouterOutput, Ticket


class EchoRouter:
    name = "echo"

    def predict(self, ticket: Ticket) -> RouterOutput:
        raise InvalidOutput(ticket.body)


@dataclass(frozen=True)
class FrozenRouter:
    """The style this repo uses for its own routers: a read-only name must fit too."""

    name: str = "frozen"

    def predict(self, ticket: Ticket) -> RouterOutput:
        raise InvalidOutput(ticket.body)


class PropertyRouter:
    @property
    def name(self) -> str:
        return "property"

    def predict(self, ticket: Ticket) -> RouterOutput:
        raise InvalidOutput(ticket.body)


def test_a_ledgerly_router_fits_the_protocol() -> None:
    # mypy checks these assignments; the asserts check the runtime shape.
    router: LedgerlyRouter = EchoRouter()
    generic: Router[Ticket, RouterOutput] = router
    assert generic.name == "echo"


def test_a_read_only_name_fits_the_protocol() -> None:
    routers: list[LedgerlyRouter] = [FrozenRouter(), PropertyRouter()]
    assert [r.name for r in routers] == ["frozen", "property"]


def test_invalid_output_keeps_the_raw_text() -> None:
    error = InvalidOutput("not json at all")
    assert error.raw_text == "not json at all"
    assert isinstance(error, Exception)
