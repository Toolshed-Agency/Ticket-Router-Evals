# Open work

Everything still to do. Items leave this file when they ship. As of 2026-11-18.

## Now

- [x] Walk through the scope part by part and agree what each piece is for.
- [x] Review and approve the design spec (approved 2026-11-18):
      [specs/2026-11-17-ticket-router-evals-design.md](specs/2026-11-17-ticket-router-evals-design.md).
- [ ] Send the open questions (spec section 15) to the people who own them, plus one more: secret
      scanning and push protection switched on for the repo by an org admin.
- [x] Write the plan for phase 1: [plans/2026-11-18-phase-1-foundation.md](plans/2026-11-18-phase-1-foundation.md).
- [x] Phase 1, Tasks 1 to 5: the uv project, Ruff, mypy, pytest, the boundary test, secret checks
      and `ci.yml` (on `phase-1/foundation`, not yet pushed).
- [ ] Phase 1, Tasks 6 to 10: the five probes (Gemini free tier, Python Workers, Workers AI, Pages
      custom domain, Langfuse).
- [ ] Phase 1, Tasks 11 and 12: apply the probe results, review the branch, push and open pull
      requests.

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
