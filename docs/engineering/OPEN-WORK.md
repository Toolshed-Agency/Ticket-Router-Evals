# Open work

Everything still to do. Items leave this file when they ship. As of 2026-11-19.

## Now

- [x] Walk through the scope part by part and agree what each piece is for.
- [x] Review and approve the design spec (approved 2026-11-18):
      [specs/2026-11-17-ticket-router-evals-design.md](specs/2026-11-17-ticket-router-evals-design.md).
- [ ] Send the open questions (spec section 15) to the people who own them, plus one more: secret
      scanning and push protection switched on for the repo by an org admin.
- [x] Write the plan for phase 1: [plans/2026-11-18-phase-1-foundation.md](plans/2026-11-18-phase-1-foundation.md).
- [x] Phase 1, Tasks 1 to 5: the uv project, Ruff, mypy, pytest, the boundary test, secret checks
      and `ci.yml`.
- [x] Phase 1, Tasks 6, 7, 8 and 10: the Gemini, Python Workers, Workers AI and Langfuse probes
      ([reports](probes/)).
- [ ] Phase 1, Task 9: the Pages custom-domain probe. Waits for the subdomain and one DNS record;
      blocks phase 9 only.
- [x] Phase 1, Task 11: the probe results and the decisions they needed are in the spec.
- [x] Phase 1, Task 12: reviewed, pushed and merged (pull requests #1, #2 and #3).
- [x] Write the plan for phase 2 (contracts and guides):
      [plans/2026-11-19-phase-2-contracts.md](plans/2026-11-19-phase-2-contracts.md).
- [x] Phase 2, Tasks 1 to 5: the router, ticket record and results file contracts, the mix
      checks and the published JSON Schemas.
- [x] Phase 2: a consistency review of the drafts, spec, plans and code; the fixes Ajlal approved
      are in (plan execution log, 2026-11-19).
- [x] Phase 2, Tasks 6 to 9: the policy, labelling guide, scenario list and rubric draft,
      reviewed by Ajlal.
- [ ] Phase 2, Task 10: docs, an independent review of the branch, and the pull request.

## Follow-ups for later phases

- Phase 3, before labelling: both labellers read and accept the labelling guide; the split script
  (seeded, stratified) assigns tickets to dev and test at the freeze and writes `data/VERSION`.
  `data/scenarios.csv` is not read while tuning: its premises summarise every ticket.
- Phase 4: the file format for re-run coverage verdicts after a gold `issues` correction (spec
  section 7, corrections), committed beside the runs it updates.
- Phase 4: the parser for model answers rejects a JSON object that repeats a key before
  validating it (`json.loads` keeps the last one silently), as the ticket loader already does.
  Otherwise a sloppy answer is quietly repaired and schema validity is flattered.
- Phase 4: results files record a bring-your-own ticket file's path relative to the repo, or its
  name only, never an absolute local path, which could expose a username.
- Phase 4 plan, a sticky choice for Ajlal: a bring-your-own file named `dev.jsonl` or
  `test.jsonl` gives the same run id as a Ledgerly split run (P2-D4). Options include prefixing
  file stems (for example `file-dev`). Provenance tells them apart either way.
- Noted, not done: frozen models hold lists, so `issues.append()` still works on a frozen model.
  Tuples would make them immutable without changing the published JSON contract, so this can be
  changed later without breaking any file.
- Phase 4 plan: choose the HTTP client the provider adapters use (S4). It is a dependency, so it
  comes with options and a recommendation.
- Phase 4: a timeout on every model call, and retries with backoff on 429, 503, 504 and timeouts
  (spec section 6).
- Phase 5, before tuning: run v1 on the frozen dev set with Gemini 3.1 and 3.5 Flash-Lite; the
  better becomes the development model, the other the judge candidate (S11).
- Phase 7: check whether Gemma 4 26B's reasoning can be turned down (28 s a call in the probe).
- Phase 9: the website renders the reader-facing docs (`docs/methodology.md`, the labeling guide,
  the agreement report) from those same Markdown files, not copies, so the site and GitHub show
  one source. No separate documentation site (MkDocs, Zensical): GitHub renders the engineering
  docs, and the harness is copied, not installed, so it needs no API reference site.
- Phase 9: re-measure the demo's CPU with the real v3 code; decide whether the demo gets its own
  Gemini project, after checking Google's terms on rate limits.
- Wrangler was logged out on the development laptop after the probes (2026-11-19); Task 9 logs in
  again and out when done. The Workers AI token stays until phase 7 (it is limited to Workers AI
  on a Free account), then is revoked.
- Deferred from the phase 1 review (minor): the CI secret test misses `secrets[...]`, `secrets:
  inherit` and `workflow_run`; the boundary check rejects files saved with a UTF-8 BOM and has no
  way to mark a false positive; a stale comment in `ci.yml` about a second Python version; pushes
  to `main` can cancel each other's CI runs; CI jobs have no display names; probe scripts send the
  prompt file's header comment; the phase 1 plan's execution log is empty and it cites internal
  asks; no uv version pin for laptops (a sticky choice).

## Questions found while reading the scope

All seven are answered in the design spec:

1. How much the test set can prove: confidence intervals everywhere (D3, section 8).
2. A CI gate that does not fail at random: confirm flips before failing (D7, section 11).
3. Pull requests from forks: no keys for fork code; maintainer-run eval with a no-billing key
   (section 11).
4. Site numbers match `results/`: the numbers-match test (section 12).
5. Test-set lock: `data/test.lock`, checked in CI (section 7).
6. Python version: 3.14 for development (S2).
7. A demo cap that holds under load: a Durable Object, failing closed (S9, section 13).

## Roadmap

See the design spec, section 14 (phases, dependencies and the critical path).
