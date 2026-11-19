"""The generic router interface (spec section 6), and that Ledgerly routers fit it."""

from harness.contracts import InvalidOutput, Router
from router.schema import LedgerlyRouter, RouterOutput, Ticket


class EchoRouter:
    name = "echo"

    def predict(self, ticket: Ticket) -> RouterOutput:
        raise InvalidOutput(ticket.body)


def test_a_ledgerly_router_fits_the_protocol() -> None:
    # mypy checks these assignments; the asserts check the runtime shape.
    router: LedgerlyRouter = EchoRouter()
    generic: Router[Ticket, RouterOutput] = router
    assert generic.name == "echo"


def test_invalid_output_keeps_the_raw_text() -> None:
    error = InvalidOutput("not json at all")
    assert error.raw_text == "not json at all"
    assert isinstance(error, Exception)
