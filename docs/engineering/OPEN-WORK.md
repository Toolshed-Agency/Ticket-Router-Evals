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
      and `ci.yml` (on `phase-1/foundation`, not yet pushed).
- [x] Phase 1, Tasks 6, 7, 8 and 10: the Gemini, Python Workers, Workers AI and Langfuse probes
      ([reports](probes/)).
- [ ] Phase 1, Task 9: the Pages custom-domain probe. Waits for the subdomain and one DNS record;
      blocks phase 9 only.
- [x] Phase 1, Task 11: the probe results and the decisions they needed are in the spec.
- [ ] Phase 1, Task 12: review the branch, then push and open pull requests (after asking).

## Follow-ups from the phase 1 probes

- Phase 4 plan: choose the HTTP client the provider adapters use (S4). It is a dependency, so it
  comes with options and a recommendation.
- Phase 4: a timeout on every model call, and retries with backoff on 429, 503, 504 and timeouts
  (spec section 6).
- Phase 5, before tuning: run v1 on the frozen dev set with Gemini 3.1 and 3.5 Flash-Lite; the
  better becomes the development model, the other the judge candidate (S11).
- Phase 7: check whether Gemma 4 26B's reasoning can be turned down (28 s a call in the probe).
- Phase 9: re-measure the demo's CPU with the real v3 code; decide whether the demo gets its own
  Gemini project, after checking Google's terms on rate limits.
- After Task 9: `wrangler logout` on the development laptop. The Workers AI token stays until
  phase 7 (it is limited to Workers AI on a Free account), then is revoked.

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
