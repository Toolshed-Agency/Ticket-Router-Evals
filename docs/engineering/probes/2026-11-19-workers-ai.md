# Probe: Workers AI

Date: 2026-11-19 · Phase 1, Task 8 · Decides: whether a free open model on Workers AI joins the
model comparison and could serve the live demo in every country (D9, S11)

## Question

Can an open model on Cloudflare Workers AI run v3 within the free daily allocation, and how does
its Urdu and Roman Urdu look?

## Setup

- The Cloudflare account is on **Workers Free** ("Current plan: Free", 2026-11-19). Free gets
  10,000 neurons a day; past that, requests fail with an error ("If you exceed any one of the
  above limits, further operations will fail with an error", [pricing
  page](https://developers.cloudflare.com/workers-ai/platform/pricing/)). It cannot bill.
- An API token limited to Workers AI. Requests used Workers AI's OpenAI-compatible endpoint
  (`/ai/v1/chat/completions`), so every model got the same request: the stand-in prompt, the
  six probe tickets, temperature 0, and the output schema as `response_format` JSON schema. Script:
  [scripts/workers_ai_probe.py](scripts/workers_ai_probe.py).
- The catalog listed 41 text-generation models; 9 of them need a paid plan. Three candidates were
  run once each: Gemma 4 26B (the same model family Google serves), Llama 3.3 70B (listed on the
  JSON-mode page) and gpt-oss-120b.
- Neurons per call are computed from token counts and the per-model rates on the pricing page
  (read 2026-11-19; the page was last modified 2026-11-12). The whole probe used about 1,300
  neurons.

## Results

| Model | Valid | Latency p50 | Output tokens | Neurons a call | Language labels | Draft language and script |
|---|---|---|---|---|---|---|
| Gemma 4 26B | 6 of 6 | 28.6 s | 900 to 1,800 (it reasons before answering) | 51 | All 6 right | All 6 right |
| Llama 3.3 70B | 6 of 6 | 6.4 s | 110 to 220 | 73 | Roman Urdu takeover ticket labelled `ur` | The Urdu-script ticket's reply contains **Devanagari (Hindi script)** |
| gpt-oss-120b | 6 of 6 | 13.8 s | 540 to 770 (reasoning) | 94 | Roman Urdu takeover ticket labelled `ur` | Replied to that Roman Urdu ticket in Urdu script |

All three resisted the injection ticket and marked the outage and the suspected takeover P1 with
escalation. Ajlal read every Urdu, Roman Urdu and mixed draft (2026-11-19): fine overall, except
Llama's reply mixing in Hindi.

## Arithmetic

With 10,000 free neurons a day, at the stand-in prompt's size (the real v3 prompt will be larger):

| Model | Calls a day | The demo's 50 a day | One v3 dev run (284 calls) |
|---|---|---|---|
| Gemma 4 26B | about 196 | 2,550 neurons (26%) | about 14,500 neurons: 1.5 days |
| Llama 3.3 70B | about 137 | 3,650 neurons (37%) | about 20,700 neurons: 2.1 days |
| gpt-oss-120b | about 106 | 4,700 neurons (47%) | about 26,700 neurons: 2.7 days |

## What it decides

1. **D9 is feasible on cost.** A Workers AI model can serve the demo's 50 requests a day within
   the free allocation, in every country. Whether it should is decided by its scores in phase 7,
   as D9 says.
2. **Not a development model.** One v3 dev run needs 1.5 to 2.7 days of allocation. Workers AI is a
   comparison entry only (S11).
3. **Gemma 4 26B is the candidate.** It was the only one with every language label and every
   draft's language and script right, and it is the cheapest per call. Its problem is speed: 28.6 s
   is too slow for a live demo, because it reasons first. Phase 7 checks whether reasoning can be
   turned down.
4. **Llama 3.3 70B is out for an Urdu-facing demo.** It is the fastest, but writing Hindi script to
   an Urdu customer is the kind of error this project exists to catch. gpt-oss-120b is slower and
   confused Roman Urdu with Urdu script.

## Recommendation

Carry **Gemma 4 26B** into phase 7 as the free Workers AI entry (S11), with its reasoning setting
recorded. The exact model is confirmed in the phase 7 plan, from the catalog of the day. The token
can stay until then; it is limited to Workers AI on a Free account.
