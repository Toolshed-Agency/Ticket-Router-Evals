# Probe: Langfuse Cloud free tier

Date: 2026-11-19 · Phase 1, Task 10 · Decides: whether S13 (optional Langfuse tracing) stays free

## Question

What does Langfuse Cloud's free plan allow, and does tracing our runs stay within it at $0? This
confirms spec S13 before tracing is first switched on in phase 4. No account was created.

## Method

Read Langfuse's own pages on 2026-11-19 (none shows a "last updated" date):
[pricing](https://langfuse.com/pricing),
[billable units](https://langfuse.com/docs/administration/billable-units),
[data regions](https://langfuse.com/security/data-regions),
[data access vs retention](https://langfuse.com/faq/all/data-access-vs-data-retention),
[API limits](https://langfuse.com/faq/all/api-limits).

## Results: the Hobby plan

| Item | Hobby (free) | Source |
|---|---|---|
| Price, card | Free; "No credit card required"; payment methods "--" | pricing |
| Included usage | 50k units a month. "Units = Count of Traces + Count of Observations + Count of Scores" | pricing, billable units |
| Overage | "Additional usage: --" (no overage billing listed) | pricing |
| At the monthly limit | **Not documented** on any page read | pricing, billable units, API limits |
| Data access | 30 days; older data is kept but hidden until an upgrade. No automatic deletion on Hobby | pricing, data access FAQ |
| Users, projects | 2 users; unlimited projects | pricing |
| Ingestion rate | 1,000 requests a minute; over a limit the API answers 429 with `Retry-After` | pricing, API limits |
| Regions | US (Oregon), EU (Ireland) or Japan (Tokyo); fully separate, switching means a new account | pricing, data regions |

## Usage estimate

Assume one trace per ticket and one observation per model call. v3 is assumed to make 2 calls per
ticket on the ~142 scored dev tickets; Task 6 kept the same assumption, and phase 5 measures it. That gives
about 3 units per ticket and about 430 units per run.

| Run | Units (approx.) |
|---|---|
| One v3 dev run | 430 |
| `--repeat 3` on v3 | 1,300 |
| Ablation (5 runs) | 2,150 |
| Judge on one run (one observation per draft) | 140 |

50k units a month covers about 100 traced dev runs. Prompt tuning in phase 5 is the heaviest use
and stays well inside it.

## What it decides

- **S13 holds.** Tracing stays optional, off unless its environment variables are set, and free.
  The Hobby plan has no payment method, so it cannot bill; at worst, traces past 50k in a month
  are not recorded. Scoring and results never depend on tracing, so nothing published is affected.
- **The limit behaviour is unknown.** Nothing in our runs relies on it, but phase 4's tracing code
  must treat any error from Langfuse (429 included) as "trace not sent" and carry on. A run never
  fails because tracing failed.

## Recommendation

Keep S13 as written. When phase 4 enables tracing, create the account on the work email in the EU
region (the inputs are synthetic either way, so the region is a default, not a requirement) and
confirm these limits again on that day.
