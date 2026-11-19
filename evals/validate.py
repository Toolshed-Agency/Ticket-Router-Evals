"""Whole-dataset checks for the Ledgerly dataset (spec section 7).

Record-level rules live on the models in `evals.dataset`; these are the rules that need every
ticket at once: ids, meta, the canary, and the mix targets.
"""

import re
from collections import Counter
from collections.abc import Mapping, Sequence

from evals.dataset import CANARY, TicketRecord
from evals.mix import LANGUAGE_TOTALS, SLICE_SPLIT, TEAM_TOTALS, TOLERANCE

ID_PATTERN = re.compile(r"LDG-[0-9]{4}")  # \d would also match non-ASCII digits


def validate_dataset(dev: Sequence[TicketRecord], test: Sequence[TicketRecord]) -> list[str]:
    """Every problem found, one line each; an empty list means the dataset is valid."""
    problems: list[str] = []
    everything = [*dev, *test]

    for record in everything:
        if not ID_PATTERN.fullmatch(record.id):
            problems.append(f"{record.id}: id does not match LDG-0000")
        if record.meta is None:
            problems.append(f"{record.id}: meta is missing")
        if record.canary != CANARY:
            problems.append(f"{record.id}: canary is missing or wrong")

    for ticket_id, n in sorted(Counter(r.id for r in everything).items()):
        if n > 1:
            problems.append(f"{ticket_id}: id used {n} times across dev and test")

    for name, split, index in (("dev", dev, 0), ("test", test, 1)):
        counts = Counter(r.meta.slice for r in split if r.meta is not None)
        for slice_, targets in SLICE_SPLIT.items():
            if counts[slice_] != targets[index]:
                problems.append(
                    f"{name}: {slice_} has {counts[slice_]} tickets, expected {targets[index]}"
                )

    problems += _within_tolerance(
        "language", Counter(r.gold.language for r in everything), LANGUAGE_TOTALS
    )
    problems += _within_tolerance("team", Counter(r.gold.team for r in everything), TEAM_TOTALS)
    return problems


def _within_tolerance[K: str](
    label: str, counts: Mapping[K, int], targets: Mapping[K, int]
) -> list[str]:
    return [
        f"{label} {key}: {counts.get(key, 0)} tickets, target {target} (within {TOLERANCE})"
        for key, target in targets.items()
        if abs(counts.get(key, 0) - target) > TOLERANCE
    ]
