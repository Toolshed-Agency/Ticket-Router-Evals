"""Each definition has one home; the few copies that cannot be links are checked against it.

CLAUDE.md, "Writing rule documents", rule 1. The homes: allowed values in the contracts
(`router/schema.py`, `evals/dataset.py`), what each label means in the labelling guide, support
rules and numbers in the policy, grading in the rubric. Other documents link to them, so every
link must resolve.
"""

import re
from collections import Counter
from enum import StrEnum
from pathlib import Path

import pytest

from evals.dataset import Slice
from router.schema import Channel, Language, Team, Tier, Urgency
from tests import REPO_ROOT
from tests.test_scenarios import PII_KINDS

POLICY = REPO_ROOT / "context" / "policies.md"
GUIDE = REPO_ROOT / "docs" / "labeling-guide.md"
RUBRIC = REPO_ROOT / "evals" / "rubric.md"
SPEC = REPO_ROOT / "docs" / "engineering" / "specs" / "2026-11-17-ticket-router-evals-design.md"

# A number in figures, with a range and the word after it: "7 days", "5 to 10 business days",
# "5% VAT", "9am to 6pm", "500 is". Urgency levels ("P1") are not numbers: no word boundary
# comes before their digit. A number written in words ("within the hour") is not caught.
_FIGURE = r"\d+(?:[.,]\d+)*(?:%|am|pm)?"
NUMBER = re.compile(rf"\b{_FIGURE}(?: to {_FIGURE})?(?: business)?(?: [A-Za-z]+)?")
INLINE_LINK = re.compile(r"\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
REFERENCE_LINK = re.compile(r"(?m)^ {0,3}\[[^\]]+\]:\s*(\S+)")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def flat(text: str) -> str:
    """The text with every run of whitespace, line breaks included, made one space."""
    return " ".join(text.split())


def numbers(text: str) -> list[str]:
    """The numbers in the text, in order. Numbered-list markers ("1. ") are not numbers."""
    return NUMBER.findall(flat(re.sub(r"(?m)^\s*\d+\. ", "", text)))


def section(text: str, heading: str) -> str:
    """The text under a Markdown heading, up to the next heading of the same or a higher level."""
    lines = text.split("\n")
    assert heading in lines, f"heading not found: {heading!r}"
    start = lines.index(heading) + 1
    level = len(heading) - len(heading.lstrip("#"))
    next_heading = re.compile(rf"#{{1,{level}}} ")
    end = next((i for i in range(start, len(lines)) if next_heading.match(lines[i])), len(lines))
    return "\n".join(lines[start:end])


def table(text: str) -> list[tuple[str, ...]]:
    """The body rows of the Markdown tables in the text, in order, repeats kept. Bold marks are
    removed, and backticks from the first cell."""
    divider = re.compile(r"\|[|\s:-]+")
    lines = text.split("\n")
    rows = []
    for i, line in enumerate(lines):
        if not line.startswith("|") or divider.fullmatch(line):
            continue
        if i + 1 < len(lines) and divider.fullmatch(lines[i + 1]):
            continue  # a header row
        cells = [cell.strip().replace("**", "") for cell in line.strip().strip("|").split("|")]
        rows.append((cells[0].strip("`"), *cells[1:]))
    return rows


def values(enum: type[StrEnum]) -> list[str]:
    return sorted(member.value for member in enum)


def listed(text: str) -> list[str]:
    """A comma-separated list of values, backticks removed, sorted, repeats kept."""
    return sorted(value.strip().strip("`") for value in text.split(","))


def without_fences(text: str) -> str:
    return re.sub(r"(?ms)^```.*?^```", "", text)


def prose(text: str) -> str:
    """The text without code blocks or code spans, where brackets are code, not links."""
    return re.sub(r"`[^`\n]*`", "", without_fences(text))


def anchors(document: Path) -> set[str]:
    """GitHub's anchor for each heading: lowercased, punctuation dropped, spaces made hyphens;
    a repeated heading gets -1, -2 and so on."""
    seen: Counter[str] = Counter()
    found = set()
    for heading in re.findall(r"(?m)^#{1,6} .+$", without_fences(read(document))):
        text = heading.lstrip("#").strip().lower()
        base = re.sub(r"[^\w\- ]", "", text).replace(" ", "-")
        found.add(f"{base}-{seen[base]}" if seen[base] else base)
        seen[base] += 1
    return found


def response_times() -> dict[str, str]:
    """Each urgency level's first-response time, as the policy states it."""
    rows = table(section(read(POLICY), "## Response times"))
    return {row[0]: numbers(row[1])[0] for row in rows}


def pass_examples() -> dict[str, list[str]]:
    """Each rubric criterion's pass examples, each on one line."""
    parts = re.split(r"(?m)^(### .+)$", section(read(RUBRIC), "## The four criteria"))
    examples = {}
    for heading, body in zip(parts[1::2], parts[2::2], strict=True):
        items = [item.split("\n\n")[0] for item in re.split(r"\n(?=- )", body)]
        examples[heading] = [flat(i) for i in items if re.match(r"- \*{1,2}Pass\*{1,2}", i)]
    return examples


def test_the_guide_lists_the_contracts_values() -> None:
    given = {row[0]: row[1] for row in table(section(read(GUIDE), "## How to label"))}
    for label, enum in (("Team", Team), ("Urgency", Urgency), ("Language", Language)):
        assert listed(given[label]) == values(enum), label


@pytest.mark.parametrize(
    ("heading", "enum"),
    [
        ("## Team: who owns the ticket", Team),
        ("## Urgency: how fast it needs a first response", Urgency),
        ("## Language: what the customer wrote in", Language),
    ],
    ids=["team", "urgency", "language"],
)
def test_the_guide_defines_each_value_once(heading: str, enum: type[StrEnum]) -> None:
    rows = table(section(read(GUIDE), heading))
    assert sorted(row[0] for row in rows) == values(enum)


def test_the_policy_gives_one_response_time_per_level() -> None:
    rows = table(section(read(POLICY), "## Response times"))
    assert [row[0] for row in rows] == [level.value for level in Urgency]
    assert all(len(numbers(row[1])) == 1 for row in rows), rows


def test_the_specs_lists_of_values_match_the_contracts() -> None:
    spec = read(SPEC)
    output = {row[0]: row[1] for row in table(section(spec, "### Router output"))}
    for field, enum in (("team", Team), ("urgency", Urgency), ("language", Language)):
        assert sorted(re.findall(r"`([^`]+)`", output[field])) == values(enum), field
    record = flat(section(spec, "### Ticket record (one JSONL line)"))
    lists: tuple[tuple[str, type[StrEnum]], ...] = (
        (r"`input\.channel`: ([^.]+)\.", Channel),
        (r"`input\.customer_tier`: ([^.]+)\.", Tier),
        (r"`meta\.slice`: exactly one primary slice per ticket \(([^)]+)\)", Slice),
    )
    for pattern, contract in lists:
        found = re.search(pattern, record)
        assert found is not None, f"not found: {pattern}"
        assert listed(found.group(1)) == values(contract), pattern


def test_the_rubric_lists_the_contracts_languages() -> None:
    criterion = "### `matches_language`: the reply is in the customer's language and script"
    named = re.findall(r"`([^`]+)`", section(read(RUBRIC), criterion))
    assert sorted(set(named)) == values(Language)


def test_the_scenario_checks_know_every_kind_of_personal_data_in_the_policy() -> None:
    found = re.search(
        r"never repeats (.+?) back to a customer", flat(section(read(POLICY), "## Personal data"))
    )
    assert found is not None, "the policy's list of personal data was not found"
    kinds = {kind.strip().lower() for kind in re.split(r",| and | or ", found.group(1))}
    assert all(any(stem in kind for stem in PII_KINDS) for kind in kinds), kinds
    assert all(any(stem in kind for kind in kinds) for stem in PII_KINDS)


def test_every_rubric_criterion_has_a_pass_example() -> None:
    examples = pass_examples()
    assert examples, "no criteria found in the rubric"
    assert [heading for heading, found in examples.items() if not found] == []


def test_a_rubric_pass_example_quotes_only_what_the_policy_gives() -> None:
    # A passing example must not teach the judge a time or amount the policy does not give, or
    # the response time of a different urgency level. Only the quoted reply is read: numbers in
    # the example's context ("2 earlier tickets") are not promises.
    policy = set(numbers(read(POLICY)))
    times = response_times()
    checked = 0
    for example in (e for found in pass_examples().values() for e in found):
        context, _, rest = example.partition('"')
        quoted = numbers(rest.rpartition('"')[0])
        checked += len(quoted)
        assert set(quoted) <= policy, example
        quoted_times = [n for n in quoted if n in times.values()]
        if quoted_times:
            level = re.search(r"\bP[1-4]\b", context)
            assert level is not None, f"names no urgency level: {example}"
            assert set(quoted_times) == {times[level.group()]}, example
    assert checked, "no numbers found in the rubric's pass examples"


@pytest.mark.parametrize("document", [POLICY, GUIDE, RUBRIC, SPEC], ids=lambda p: p.name)
def test_every_link_resolves(document: Path) -> None:
    text = prose(read(document))
    targets = INLINE_LINK.findall(text) + REFERENCE_LINK.findall(text)
    assert targets, "no links found"
    broken = []
    for target in targets:
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path, _, anchor = target.partition("#")
        linked = (document.parent / path).resolve() if path else document
        checks_anchor = bool(anchor) and linked.suffix == ".md"
        if not linked.exists() or (checks_anchor and anchor not in anchors(linked)):
            broken.append(target)
    assert broken == []
