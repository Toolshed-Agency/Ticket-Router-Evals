"""The Ledgerly dataset's mix targets (spec section 7, D3)."""

from typing import Final

from evals.dataset import Slice
from router.schema import Language, Team

# (dev, test) per slice. Exact: the tickets are written to these counts.
SLICE_SPLIT: Final[dict[Slice, tuple[int, int]]] = {
    Slice.ROUTINE: (75, 25),
    Slice.MULTI_ISSUE: (15, 5),
    Slice.ANGRY_REPEAT: (15, 5),
    Slice.P1: (15, 5),
    Slice.VAGUE: (12, 4),
    Slice.PII: (11, 3),
    Slice.INJECTION: (7, 3),
}

# Targets across all 200: the gold labels may land within TOLERANCE of them.
LANGUAGE_TOTALS: Final[dict[Language, int]] = {
    Language.EN: 100,
    Language.ROMAN_UR: 50,
    Language.UR: 20,
    Language.MIXED: 30,
}
TEAM_TOTALS: Final[dict[Team, int]] = {
    Team.BILLING: 60,
    Team.TECHNICAL: 60,
    Team.REFUNDS: 30,
    Team.SALES: 20,
    Team.OTHER: 16,
    Team.ACCOUNT_SECURITY: 14,
}
TOLERANCE: Final = 3
