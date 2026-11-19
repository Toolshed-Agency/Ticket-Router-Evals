# Probe: Gemini API free tier

Date: 2026-11-19 · Phase 1, Task 6 · Decides: the development model (S11, D10), whether the
ablation fits (D4), CI timing (section 11)

## Question

What are the real free-tier limits for a development model and a judge candidate, how reliable
and fast are they, and how long does one v3 dev run take?

## Setup

- **Project:** one Google AI Studio project, on the **Free tier** with no billing account (checked
  in AI Studio's API keys page on 2026-11-19). The 429 below confirms it: the quota that tripped
  is `generate_content_free_tier_requests`.
- **Client:** google-genai 3.5.0, retries off (errors show as they are), 120-second timeout,
  temperature 0, the provider's native JSON-schema output (S5).
- **Inputs:** the six synthetic probe tickets and a stand-in prompt about v3's size (both in
  [scripts/](scripts/)). The stand-in measured about 1,640 input tokens; the real v3 prompt, with
  the full policy and few-shot examples, will be larger.
- **When:** 2026-11-18, 21:24 to 21:55 UTC (the US afternoon). Raw output is not committed; the
  script reproduces it.

## Free limits, as AI Studio shows them for this project (2026-11-19)

| Model | Requests a minute | Tokens a minute | Requests a day |
|---|---|---|---|
| Gemini 2.5, 3, 3.6 and 3.8 Flash; Gemini 4 Hydrogen | 5 | 250K | **20** |
| Gemini 3.1 and 3.5 Flash-Lite | 15 | 250K | **500** |
| Gemma 4 26B and 31B | 30 | **16K** | 14,400 |
| Gemini 2.5 Pro, 3.1 Pro, Gemini 4 Argon and Carbon | none | | |

Limits are per project and per model; daily quotas reset at midnight Pacific.

**Enforced limit, measured:** 15 back-to-back calls to 3.5 Flash-Lite succeeded in 16.1 seconds;
the 16th was refused with 429, quota `GenerateRequestsPerMinutePerProjectPerModel-FreeTier`,
value 15, retry after 33 seconds. The page's numbers are the real ones.

## Results

| Model | Calls | Valid | Errors | Latency p50 / p95 | Tokens in / out / thinking |
|---|---|---|---|---|---|
| Gemini 3.5 Flash-Lite | 18 | **18** | none (one 503 in an earlier attempt) | 1.8 s / 2.3 s | 1,639 / 170 / none |
| Gemini 3.1 Flash-Lite | 18 | **18** | none | 1.9 s / 3.2 s | 1,639 / 175 / none |
| Gemini 3.8 Flash | 6 | 0 | 3 × 504 deadline (about 119 s each), 3 × 503 "high demand"; an earlier call hung 8 minutes with no timeout | | |
| Gemini 4 Hydrogen | 6 | 2 | 2 × 504, 2 × 503 | 33 s and 116 s for the two that answered | 2,066 / 235 / 842 |
| Gemma 4 31B | 18 | 6 | 12 × 503 | 28 s / 53 s | 1,633 / 171 / none |
| Gemini 2.5 Flash | 6 | 0 | 6 × 404 "no longer available to new users", although AI Studio lists its quota | | |

Both Flash-Lite models gave identical team, urgency, escalation and language on all three rounds
of every ticket. A first look at what they chose, not a score: both resisted the injection ticket
(not refunds, not P1), marked the outage and the suspected takeover P1 with escalation, and
labelled the Roman Urdu, Urdu-script and mixed tickets correctly.

The drafts were not identical across rounds, even at temperature 0. Ajlal read every non-English
draft (2026-11-19): fine overall, but 3.5 Flash-Lite answered the Roman Urdu takeover ticket in
English in one of its three rounds (in Roman Urdu in the other two). 3.1 Flash-Lite answered it in
Roman Urdu all three times. One draft in nine is too few to separate the two models, but it is the
kind of error the judge's "matches the customer's language" criterion exists to catch.

## Arithmetic

Assumptions: about 142 scored dev tickets; v3 makes 2 calls a ticket (284 calls a run), v1 and v2
make 1 (142 calls).

| Workload | Calls | Flash class (20 a day) | One Flash-Lite model (500 a day) |
|---|---|---|---|
| One v3 dev run | 284 | 15 days | 19 minutes at 15 a minute; 1.7 runs a day |
| Pull-request gate (v3, plus about 20 re-run calls for flips) | about 300 | 15 days | about 20 minutes; about one gate a day |
| Ablation (5 runs of v3) | 1,420 | months | about 3 days of quota, resumed from the cache (D10) |
| Consistency, `--repeat 3` on v1, v2 and v3 | 1,704 | months | about 3.5 days |

The two Flash-Lite models have separate quotas (500 a day each).

## What it decides

1. **D10's fallback applies: a Flash-class model cannot be the development model.** At 20
   requests a day, one v3 dev run takes 15 days, before counting the 503s and 504s. The newest
   models were also overloaded when measured; Flash-Lite was the only reliable family.
2. **Reliability needs the harness's retries.** 503 and 504 are routine on the free tier, and the
   SDK has no request timeout by default. Phase 4's model client needs a timeout, retries with
   backoff on 429, 503 and 504 (honouring `retry after`), and resume from the cache. Section 6 of
   the spec already requires retries and resume; the timeout is new.
3. **The ablation fits (D4)** on Flash-Lite, spread over about three days through the cache.
4. **CI timing:** a pull-request gate takes about 20 minutes, and about one gate a day fits beside
   local tuning on the same quota. CI reports "incomplete" when quota runs out (D10).
5. **Judge (section 10):** the second Flash-Lite model has its own 500-a-day quota, so the judge
   need not share the router's. The judge is chosen and calibrated in phase 6.

## Recommendation (needs a decision: model choice is sticky)

**Development model: Gemini 3.5 Flash-Lite. Judge candidate: Gemini 3.1 Flash-Lite**, each on its
own free quota. The model comparison in phase 7 still covers a full Flash model and the other
providers, on the paid credits.

Alternatives considered: Gemma 4 31B on the Gemini API (large daily quota, but 16K tokens a
minute caps it near 9 calls a minute, and two thirds of calls failed with 503); a Workers AI
model ([Workers AI probe](2026-11-19-workers-ai.md): 10,000 neurons a day buys about 200 Gemma 4
26B calls, under one v3 dev run, at about 28 seconds each).

For the demo (D8, phase 9), Flash-Lite's 500 a day covers the 50-a-day cap. Whether the demo gets
its own project, so visitors and development never share a quota, is a phase 9 decision; Google's
terms forbid working around rate limits, so that needs checking then.
