# Ticket Router Evals

An open-source exam for an AI support-ticket router, plus a public website that shows its scores.
Built by [Toolshed](https://toolshedservices.com).

The router triages support tickets for **Ledgerly**, a fictional cloud accounting SaaS for small
businesses in Pakistan and the UAE. Three router versions (naive, structured, production) are
scored on 200 hand-labelled tickets, compared across models, and published with every ticket's
result visible.

**The defining requirement:** every published number is real, reproducible from this repo, and
traceable to a committed results file. Credibility is the product. A number that is fudged, typed
in by hand or cannot be reproduced destroys it.

Status as of 2026-11-20: phases 1 and 2 are merged; phase 3 (the dataset) is next, and its plan
is not written yet. Phase 1 built the project, its checks and CI, and four of the five probes (the
Pages domain probe waits for the subdomain and a DNS record). Phase 2 added the contracts, the
policy, the labelling guide, the scenario list and the rubric draft. The
design spec is approved and updated with the probe results and the phase 2 contracts:
[docs/engineering/specs/2026-11-17-ticket-router-evals-design.md](docs/engineering/specs/2026-11-17-ticket-router-evals-design.md).
Phase 1 plan: [docs/engineering/plans/2026-11-18-phase-1-foundation.md](docs/engineering/plans/2026-11-18-phase-1-foundation.md).
Phase 2 plan: [docs/engineering/plans/2026-11-19-phase-2-contracts.md](docs/engineering/plans/2026-11-19-phase-2-contracts.md).
See also [docs/engineering/OPEN-WORK.md](docs/engineering/OPEN-WORK.md).

## Non-negotiables

- **This repo is public, history included.** No real customer data, no secrets, no internal notes.
  API keys live only in `.env` (gitignored), GitHub secrets and the demo Worker's Cloudflare
  secrets.
- **Tune on the dev set only.** The test set runs once per final router version per model and is
  reported separately.
- **Publish the real numbers**, unflattering ones included, with the explanation.
- **The site shows only numbers read from `results/`.** Nothing is typed in by hand.
- **Ledgerly resembles no real company.** Names, emails, phone numbers and account ids are
  obviously fake.
- **$0 a month to run.** Confirm free-tier limits before enabling a service; flag anything that
  could create a bill before turning it on.
- **Ticket routing only.** This is not a general-purpose eval framework.
- **Fail closed.** Missing config turns a feature off with a visible message. The live demo's
  daily cap refuses requests when it cannot read the count.

## How we work

Developed with the superpowers plugin (the process: brainstorm, spec, plan, build, review, verify)
and the maintainer's `app-build-playbook` skill (the engineering rules). Neither is part of this
repo. Where they conflict, this file wins.

**Decision tiers**

| Tier | Examples | Do |
|---|---|---|
| Sticky | dependencies and version pins, schemas, label definitions and gold labels, policy and rubric wording, metric definitions, CI thresholds, model choices, anything public-facing, anything destructive | Stop. Give options with a recommendation. Wait. |
| Shaped | a module's internals, a helper, file placement | Do it; flag it on its own line |
| Trivial | naming, comments | Do it |

A question is not a go: answer it, then wait for an explicit go.

**Planning.** One design spec for the whole project. Then one plan per phase, written just before
that phase starts, not weeks ahead. Each plan lists its sticky decisions, and they are approved
with the plan.

**Execution.** Inside an approved phase, work continues without pausing. It stops for a new sticky
decision, for anything that contradicts the plan (say so before continuing), or at the end of the
phase. Superpowers' "rulings, not stalls" covers shaped and trivial decisions only.

**Branches and commits.** Each phase works on its own branch, with a commit per task. The review
gate is the pull request into `main`. Never commit to `main` directly. Never push or open a pull
request without asking: pushing publishes.

**One pull request at a time.** Branch from an up-to-date `main`, finish, open the pull request,
merge it, and only then start the next branch. A fix between phases gets its own short pull
request first. Stacked branches made GitHub show earlier pull requests' commits again (phase 1,
2026-11-19). Merge with "Create a merge commit", never squash or rebase: results files record the
commit they ran on, and squash or rebase would leave those commits off `main`.

**Branch names.** Phase work: `phase-<n>/<name>` (for example `phase-1/foundation`), matching its
plan in `docs/engineering/plans/`. Anything else: a Conventional Commits type and a short name
(`docs/design-spec`, `fix/demo-cap`).

**Commit messages** follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/),
plus these project rules:
- Scopes, when used, come from this list (add to it here first): `router`, `prompts`, `data`,
  `harness`, `metrics`, `judge`, `cli`, `site`, `demo`, `ci`, `docs`.
- One extra type, `eval`, for result runs committed without a code change (model comparisons,
  test-set runs): `eval(v3): test-set run on <model>`.
- A change to a public contract (the ticket JSONL format, the router output schema, the results
  file format, the CLI flags) is marked breaking: `!` after the type and a `BREAKING CHANGE:`
  footer.
- A commit that changes router behaviour (a prompt, router code, or the model) carries an
  `Eval-Run: results/<run-id>.json` trailer naming the run that measured it.
- The summary is imperative, under 72 characters, lowercase after the colon. The body says why.

**Testing**
- Code is written test-first: the harness, metrics, scoring, cache, CLI, schemas, and the demo
  Worker with its cap.
- Prompts are tested by the eval on the dev set. A prompt change is done when its run is committed
  and compared against the previous one.
- The dataset is tested by validation in CI: schema, allowed values, mix targets, and the test-set
  lock.
- Metric tests use hand-computed fixtures written from the metric's definition, not from the code.
  Break the code once to watch a new test fail.
- Evidence before claims: run the command, read the output, then say it passes.

## Writing rule documents

Rule documents decide a label or a grade: the policy (`context/policies.md`), the labelling guide
(`docs/labeling-guide.md`) and the rubric (`evals/rubric.md`), with the approved tables their
rules come from (the spec's decisions and each phase plan's). Every score depends on them, so they
get the same discipline as code. In phase 2 these documents and the scenario list were drafted
one after another, late in a long session, and held about 100 contradictions between them. The
maintainer caught the first; audits once everything was written found the rest (LESSONS,
2026-11-19).

1. **One home for each definition, and as few copies as possible.** The homes: allowed values in
   the contracts (`router/schema.py`, `evals/dataset.py`, published as JSON Schemas); what each
   label means in the labelling guide; support rules and numbers in the policy; grading in the
   rubric. Every other document, the spec and code comments included, links to the home instead
   of rewording it. Decision tables (the spec's decisions and its differences from the scope of
   work, and each plan's) record approvals; they are not copies kept in sync.
   Where a copy cannot be a link (the spec lists the allowed values; the rubric's examples quote
   the policy's times), a test in `tests/test_documents.py` checks it against its home.
2. **Cases before rules.** Before writing a rule document, write about 30 boundary cases with the
   label or grade each should get, and have the maintainer approve them: those are the real
   decisions. Then write rules that produce them. The cases are committed, and a test checks that
   the document's worked examples agree with them. A later change to a rule updates the cases it
   affects first.
3. **One narrow, fresh reviewer per document, at draft time.** As each draft is finished, a
   reviewer who did not write it gets one brief: check this draft against these named files and
   list the conflicts. This replaces broad audits of all the rule documents once they are
   written; the review of the whole branch at the end of a phase stays.
4. **A fresh session for each phase,** loading superpowers' executing-plans and
   test-driven-development skills at the start. Drafts written late in a long session, after its
   earlier context has been summarised, pick up stale text from earlier work.
5. **No silent decisions.** Label definitions, policy wording and rubric wording are sticky
   (Decision tiers): a rule choice that is not already in an approved table is asked.
   Superpowers' "rulings, not stalls" never covers them.

## Docs

| Where | What | Public |
|---|---|---|
| `CLAUDE.md` | This file: what the project is, the rules, how we work | yes |
| `docs/` | Labeling guide, methodology, labelling report, written for readers of the site | yes |
| `docs/engineering/specs/` | Design specs (superpowers writes here, not to `docs/superpowers/`) | yes |
| `docs/engineering/plans/` | One plan per phase | yes |
| `docs/engineering/OPEN-WORK.md` | Everything still to do; items leave when they ship | yes |
| `docs/engineering/LESSONS.md` | What bit us and what to do about it | yes |
| `project_reference/` | Scope of work, internal asks, anything not for the public | no (gitignored) |

Engineering docs are public: write them for an outside developer. When reality disagrees with a
doc, fix the doc in the same change and update its "as of" date.

## Environment

- Developed on Windows 11 (PowerShell 5.1 and Git Bash); CI runs on Linux. Text files are LF in
  the repo and in every working copy (`.gitattributes`), so file hashes match on every machine.
- Planned stack (design spec, section 4): Python 3.14 with uv, Ruff, pytest and Pydantic; Astro
  on Cloudflare Pages; a Python Worker for the live demo; GitHub Actions. Development uses free
  model tiers only.

## Commands

Add each one here when it exists. All run from the repo root; uv installs Python 3.14 itself.

| Command | Does |
|---|---|
| `uv sync` | Installs the project and its pinned dev tools from `uv.lock` |
| `uv run ruff format .` | Formats the code (`--check` to only report) |
| `uv run ruff check .` | Lints |
| `uv run mypy` | Type checks in strict mode |
| `uv run pytest` | Runs the tests |
| `uv run python -m evals.export_schemas` | Rewrites the published JSON Schemas in `docs/schemas/` after a contract changes |
