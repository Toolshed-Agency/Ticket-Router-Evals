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

Status as of 2026-11-18: phase 1 (foundation and probes) in progress on `phase-1/foundation`. The
project, its checks and CI are built; the probes are next. The design spec is approved:
[docs/engineering/specs/2026-11-17-ticket-router-evals-design.md](docs/engineering/specs/2026-11-17-ticket-router-evals-design.md).
Phase 1 plan: [docs/engineering/plans/2026-11-18-phase-1-foundation.md](docs/engineering/plans/2026-11-18-phase-1-foundation.md).
See also [docs/engineering/OPEN-WORK.md](docs/engineering/OPEN-WORK.md).

## Non-negotiables

- **This repo is public, history included.** No real customer data, no secrets, no internal notes.
  API keys live only in `.env` (gitignored) and GitHub secrets.
- **Tune on the dev set only.** The test set runs once per final router version and is reported
  separately.
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
| Sticky | dependencies and version pins, schemas, label definitions and gold labels, metric definitions, CI thresholds, model choices, anything public-facing, anything destructive | Stop. Give options with a recommendation. Wait. |
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

## Docs

| Where | What | Public |
|---|---|---|
| `CLAUDE.md` | This file: what the project is, the rules, how we work | yes |
| `docs/` | Labeling guide, methodology, agreement report, written for readers of the site | yes |
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
