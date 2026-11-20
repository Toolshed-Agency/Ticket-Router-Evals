"""The scenario list the Ledgerly tickets are drafted from (spec section 7; plan P2-D8).

`allocate()` fixes every column except the premise, hitting each mix target exactly and spreading
them jointly: each team in a slice gets its fair share of each language, and channels, tiers and
urgencies are spread evenly rather than clumped. It is deterministic, so the committed
`data/scenarios.csv` can be checked against it. Premises are written separately (plan P2-D8).

The list never says which scenario becomes a test ticket: the split is assigned at the freeze.
"""

import csv
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import Final

from evals.dataset import Slice
from router.schema import Channel, Language, Team, Tier, Urgency

TEAM_BY_SLICE: Final[dict[Slice, dict[Team, int]]] = {
    Slice.ROUTINE: {Team.BILLING: 38, Team.TECHNICAL: 31, Team.REFUNDS: 15, Team.SALES: 16},
    Slice.MULTI_ISSUE: {
        Team.BILLING: 6,
        Team.TECHNICAL: 5,
        Team.REFUNDS: 4,
        Team.SALES: 2,
        Team.ACCOUNT_SECURITY: 3,
    },
    Slice.ANGRY_REPEAT: {
        Team.BILLING: 7,
        Team.TECHNICAL: 6,
        Team.REFUNDS: 5,
        Team.ACCOUNT_SECURITY: 2,
    },
    Slice.P1: {Team.TECHNICAL: 12, Team.ACCOUNT_SECURITY: 8},
    Slice.VAGUE: {Team.OTHER: 16},
    Slice.PII: {Team.BILLING: 6, Team.TECHNICAL: 3, Team.REFUNDS: 4, Team.ACCOUNT_SECURITY: 1},
    Slice.INJECTION: {Team.BILLING: 3, Team.TECHNICAL: 3, Team.REFUNDS: 2, Team.SALES: 2},
}

_EN, _RU, _UR, _MX = Language.EN, Language.ROMAN_UR, Language.UR, Language.MIXED
LANGUAGE_BY_SLICE: Final[dict[Slice, dict[Language, int]]] = {
    Slice.ROUTINE: {_EN: 50, _RU: 25, _UR: 10, _MX: 15},
    Slice.MULTI_ISSUE: {_EN: 10, _RU: 5, _UR: 2, _MX: 3},
    Slice.ANGRY_REPEAT: {_EN: 10, _RU: 5, _UR: 2, _MX: 3},
    Slice.P1: {_EN: 10, _RU: 5, _UR: 2, _MX: 3},
    Slice.VAGUE: {_EN: 8, _RU: 4, _UR: 2, _MX: 2},
    Slice.PII: {_EN: 7, _RU: 3, _UR: 1, _MX: 3},
    Slice.INJECTION: {_EN: 5, _RU: 3, _UR: 1, _MX: 1},
}

# Intended urgency: a drafting aim only; the gold label is the labeller's.
URGENCY_BY_SLICE: Final[dict[Slice, dict[Urgency, int]]] = {
    Slice.ROUTINE: {Urgency.P2: 15, Urgency.P3: 55, Urgency.P4: 30},
    Slice.MULTI_ISSUE: {Urgency.P2: 8, Urgency.P3: 12},
    Slice.ANGRY_REPEAT: {Urgency.P2: 14, Urgency.P3: 6},
    Slice.P1: {Urgency.P1: 20},
    Slice.VAGUE: {Urgency.P3: 6, Urgency.P4: 10},
    Slice.PII: {Urgency.P2: 6, Urgency.P3: 8},
    Slice.INJECTION: {Urgency.P3: 6, Urgency.P4: 4},
}

CHANNEL_TOTALS: Final = {Channel.EMAIL: 80, Channel.WEB_FORM: 60, Channel.CHAT: 60}
TIER_TOTALS: Final = {Tier.FREE: 80, Tier.PRO: 90, Tier.ENTERPRISE: 30}

_TIER_STRIDE: Final = 7  # coprime with 200: spreads tiers in a different order from channels


@dataclass(frozen=True)
class Scenario:
    id: str
    slice: Slice
    team: Team
    urgency: Urgency
    language: Language
    channel: Channel
    tier: Tier
    prior_tickets_7d: int
    premise: str = ""


def _interleave[K](counts: Mapping[K, int]) -> list[K]:
    """Each key spread evenly through a list of sum(counts) items, in a fixed order."""
    order = {key: i for i, key in enumerate(counts)}
    positions = [((i + 0.5) / n, order[key], key) for key, n in counts.items() for i in range(n)]
    return [key for _, _, key in sorted(positions, key=lambda p: (p[0], p[1]))]


def _urgencies(teams: list[Team], counts: Mapping[Urgency, int]) -> list[Urgency]:
    """Urgencies spread evenly, then swapped so that no sales scenario is P1 or P2."""
    urgencies = _interleave(counts)
    for i, team in enumerate(teams):
        if team is Team.SALES and urgencies[i] in (Urgency.P1, Urgency.P2):
            j = next(
                j
                for j, other in enumerate(teams)
                if other is not Team.SALES and urgencies[j] in (Urgency.P3, Urgency.P4)
            )
            urgencies[i], urgencies[j] = urgencies[j], urgencies[i]
    return urgencies


def _prior_tickets(slice_: Slice, position: int) -> int:
    """Angry repeat contacts: 2 to 5 earlier tickets. Elsewhere 70% have 0, the rest 1 or 2."""
    if slice_ is Slice.ANGRY_REPEAT:
        return 2 + position % 4
    if position % 10 < 7:
        return 0
    return 1 + position % 2


def allocate() -> list[Scenario]:
    """All 200 scenarios with empty premises, in slice order, ids S001 to S200."""
    rows: list[Scenario] = []
    for slice_ in Slice:
        teams = [team for team, n in TEAM_BY_SLICE[slice_].items() for _ in range(n)]
        languages = _interleave(LANGUAGE_BY_SLICE[slice_])
        urgencies = _urgencies(teams, URGENCY_BY_SLICE[slice_])
        for j, (team, language, urgency) in enumerate(
            zip(teams, languages, urgencies, strict=True)
        ):
            prior = _prior_tickets(slice_, j)
            rows.append(
                Scenario(
                    id=f"S{len(rows) + 1:03d}",
                    slice=slice_,
                    team=team,
                    urgency=urgency,
                    language=language,
                    channel=Channel.EMAIL,  # set below
                    tier=Tier.FREE,  # set below
                    prior_tickets_7d=prior,
                )
            )
    channels = _interleave(CHANNEL_TOTALS)
    tiers = _interleave(TIER_TOTALS)
    n = len(rows)
    return [
        replace(row, channel=channels[i], tier=tiers[(i * _TIER_STRIDE) % n])
        for i, row in enumerate(rows)
    ]


_COLUMNS: Final = [f.name for f in fields(Scenario)]


def write_csv(scenarios: Iterable[Scenario], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for s in scenarios:
            writer.writerow({name: str(getattr(s, name)) for name in _COLUMNS})


def read_csv(path: Path) -> list[Scenario]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            Scenario(
                id=row["id"],
                slice=Slice(row["slice"]),
                team=Team(row["team"]),
                urgency=Urgency(row["urgency"]),
                language=Language(row["language"]),
                channel=Channel(row["channel"]),
                tier=Tier(row["tier"]),
                prior_tickets_7d=int(row["prior_tickets_7d"]),
                premise=row["premise"],
            )
            for row in csv.DictReader(handle)
        ]
