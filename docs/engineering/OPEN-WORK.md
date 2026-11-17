# Open work

Everything still to do. Items leave this file when they ship. As of 2026-11-17.

## Now

- [ ] Walk through the scope part by part and agree what each piece is for.
- [ ] Write the design spec for the whole project, in `docs/engineering/specs/`.

## Questions the design spec must answer

Found while reading the scope on 2026-11-17.

1. **How much the test set can prove.** 50 tickets at 10% P1 is about 5 emergencies. Even a
   perfect 5 out of 5 has a 95% confidence interval reaching down to about 48%. Options:
   confidence intervals on every headline number, a test set with more emergencies, or both.
2. **A CI gate that does not fail at random.** "Fail if P1 recall drops at all" runs on about 15
   dev-set P1s, so one flipped ticket is a 6.7-point drop, and model output varies between runs.
   Needs a defined method: temperature 0, repeated runs, or comparison against a stored baseline.
3. **Pull requests from forks.** They get no secrets and a read-only token, so they cannot run the
   eval or post the score comment. `pull_request_target` with a checkout of the pull request's
   code is a known security hole. Needs a safe design.
4. **Site numbers match `results/`, enforced by a test** rather than by care.
5. **The test-set lock, enforced:** a committed hash of the test set that CI checks.
6. **Python version.** The scope says 3.12, which has received only security fixes since 2025;
   3.13 and 3.14 are current. Confirm.
7. **A live demo cap that holds when visitors arrive at once.** 50 requests a day across all
   visitors, refusing requests when the count cannot be read. Workers KV is eventually consistent,
   so a KV counter can overshoot. Probe the options before designing.

## Roadmap

The order is confirmed in the design spec.

1. Repo foundation: Python project with uv, lint, tests, CI skeleton, secret checks.
2. Labeling guide, policy document, ticket and output schemas.
3. Dataset: scenario list, drafted tickets, hand edits, two independent labels, agreement report,
   freeze and lock. Needs two people and is the slowest phase; it runs alongside phase 4.
4. Harness: run, score, compare, response cache, results files.
5. Routers v1, v2 and v3, tuned on the dev set.
6. Judge, rubric, and calibration against 40 human-graded draft replies.
7. Model comparison and the test-set runs.
8. Regression check in CI.
9. Website and live demo.
10. Launch: walkthrough video, pinned repo.
