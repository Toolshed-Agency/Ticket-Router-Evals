"""Each definition has one home; the few copies that cannot be links are checked against it.

CLAUDE.md, "Writing rule documents", rule 1. The homes: allowed values in the contracts
(`router/schema.py`, `evals/dataset.py`), what each label means in the labelling guide, support
rules and numbers in the policy, grading in the rubric. Other documents link to them, so every
link must resolve.
"""

import re
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
LINK = re.compile(r"\]\(([^)\s]+)\)")


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


def table(text: str) -> dict[str, tuple[str, ...]]:
    """A Markdown table's body rows by their first cell, bold marks and backticks removed."""
    rows = {}
    for line in text.split("\n"):
        if line.startswith("|") and not re.fullmatch(r"[|\s:-]+", line):
            cells = [c.strip().replace("**", "") for c in line.strip().strip("|").split("|")]
            rows[cells[0].strip("`")] = tuple(cells[1:])
    return rows


def values(enum: type[StrEnum]) -> set[str]:
    return {member.value for member in enum}


def prose(text: str) -> str:
    """The text without code blocks or code spans, where brackets are code, not links."""
    return re.sub(r"`[^`\n]*`", "", re.sub(r"(?ms)^```.*?^```", "", text))


def slug(heading: str) -> str:
    """GitHub's anchor for a heading."""
    text = heading.lstrip("#").strip().lower()
    return re.sub(r"[^\w\- ]", "", text).replace(" ", "-")


def test_the_guide_lists_the_contracts_values() -> None:
    labels = table(section(read(GUIDE), "## How to label"))
    for label, enum in (("Team", Team), ("Urgency", Urgency), ("Language", Language)):
        assert set(labels[label][0].split(", ")) == values(enum), label


@pytest.mark.parametrize(
    ("document", "heading"),
    [
        (GUIDE, "## Urgency: how fast it needs a first response"),
        (POLICY, "## Response times"),
    ],
    ids=["guide", "policy"],
)
def test_each_urgency_table_has_one_row_per_level(document: Path, heading: str) -> None:
    rows = table(section(read(document), heading))
    assert [label for label in rows if re.fullmatch(r"P\d+", label)] == [u.value for u in Urgency]


def test_the_specs_lists_of_values_match_the_contracts() -> None:
    spec = read(SPEC)
    output = table(section(spec, "### Router output"))
    for field, enum in (("team", Team), ("urgency", Urgency), ("language", Language)):
        assert set(re.findall(r"`([^`]+)`", output[field][0])) == values(enum), field
    record = flat(section(spec, "### Ticket record (one JSONL line)"))
    lists: tuple[tuple[str, type[StrEnum]], ...] = (
        (r"`input\.channel`: ([^.`]+)\.", Channel),
        (r"`input\.customer_tier`: ([^.`]+)\.", Tier),
        (r"`meta\.slice`: exactly one primary slice per ticket \(([^)]+)\)", Slice),
    )
    for pattern, contract in lists:
        listed = re.search(pattern, record)
        assert listed is not None, f"not found: {pattern}"
        assert set(listed.group(1).split(", ")) == values(contract), pattern


def test_the_scenario_checks_know_every_kind_of_personal_data_in_the_policy() -> None:
    listed = re.search(
        r"never repeats (.+?) back to a customer", flat(section(read(POLICY), "## Personal data"))
    )
    assert listed is not None, "the policy's list of personal data was not found"
    kinds = {kind.strip().lower() for kind in re.split(r",| and | or ", listed.group(1))}
    assert all(any(stem in kind for stem in PII_KINDS) for kind in kinds), kinds
    assert all(any(stem in kind for kind in kinds) for stem in PII_KINDS)


def test_every_number_a_rubric_pass_example_quotes_is_in_the_policy() -> None:
    # A passing example must not teach the judge a time or amount the policy does not give.
    rubric = read(RUBRIC)
    items = [item.split("\n\n")[0] for item in re.split(r"\n(?=- )", rubric)]
    passes = [flat(item) for item in items if re.match(r"- \*{1,2}Pass\*{1,2}", item)]
    criteria = re.findall(r"(?m)^### ", section(rubric, "## The four criteria"))
    assert len(passes) >= len(criteria) > 0, "a criterion's pass example was not found"
    quoted = [n for example in passes for n in numbers(re.sub(r"\bP[1-4]\b", "", example))]
    assert quoted, "no numbers found in the rubric's pass examples"
    assert set(quoted) <= set(numbers(read(POLICY)))


@pytest.mark.parametrize("document", [POLICY, GUIDE, RUBRIC, SPEC], ids=lambda p: p.name)
def test_every_link_resolves(document: Path) -> None:
    broken = []
    for target in LINK.findall(prose(read(document))):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        path, _, anchor = target.partition("#")
        linked = (document.parent / path).resolve() if path else document
        if not linked.exists():
            broken.append(target)
        elif anchor and linked.suffix == ".md":
            headings = re.findall(r"(?m)^#{1,6} .+$", read(linked))
            if anchor not in {slug(heading) for heading in headings}:
                broken.append(target)
    assert broken == []
