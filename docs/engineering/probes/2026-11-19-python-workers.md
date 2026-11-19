# Probe: Cloudflare Python Workers

Date: 2026-11-19 · Phase 1, Task 7 · Decides: S8 (Python Worker or the TypeScript fallback), the
minimum Python version in S2, how the demo calls Gemini, and whether the demo fits the Free plan's
CPU limit

## Question

Can the demo run our Python router code in a Python Worker on the Free plan? Which Python does the
runtime use? Do Pydantic and Google's SDK work, or only plain HTTP? What do start-up, CPU time and
a Durable Object look like?

## Setup

- A Cloudflare account on **Workers Free** ("Current plan: Free" on the plans page, 2026-11-19).
- A throwaway Worker, `zzz-probe-python-worker`, on the account's workers.dev subdomain. Its code
  is in [python-worker/](python-worker/): one route per question, a SQLite-backed Durable Object,
  and the stand-in prompt and one probe ticket embedded as data.
- `compatibility_date = "2026-11-18"` with the `python_workers` flag. Packages were vendored with
  pywrangler 1.17.9 (`pywrangler sync`) and deployed with wrangler 4.164.0. The only dependency is
  Pydantic. Gemini 3.5 Flash-Lite, the free tier's reliable model ([Gemini
  probe](2026-11-19-gemini-free-tier.md)), answered the Gemini calls.
- CPU and wall time per request come from `wrangler tail`, whose events carry `cpuTime` and
  `wallTime`. Latency was measured by the client, from Pakistan.

## Results

| Question | Answer |
|---|---|
| Python version | **3.14.2**, on Pyodide 314.0.6. pywrangler 1.17.9 maps any compatibility date from 2026-09-08 to Python 3.14 |
| Pydantic | Works. Pydantic 2.14.3 with its compiled core installs and validates the output schema |
| Gemini over plain HTTP | Works. `workers.fetch` to the Gemini REST API with native JSON-schema output returned a valid answer (Gemini's own time about 1.3 s). Over 20 calls, client latency was 2.5 s typical, 6.4 s at p95 |
| Google's SDK (google-genai) | Installs (25 packages, 6.3 MB compressed, accepted on Free), but **importing it exceeds the CPU limit**: the runtime stopped it at 1,935 ms of CPU with "Python Worker exceeded CPU time limit" |
| Durable Object from Python | Works. The SQLite counter returned 1, then 2; 11 ms of CPU inside the object |
| Upload and start-up | 7.3 MB (1.97 MB compressed) with Pydantic. Wrangler reported start-up times of 1,039 to 1,338 ms, and every deploy was accepted (see the limits table below) |

**CPU per request.** Workers Free documents 10 ms of CPU per request. Where the imports sit
decides whether we are near that or far over it:

| Route | Imports inside the request handler | Imports at module level |
|---|---|---|
| `/version` | 2 ms typical, 35 ms max (21 calls) | 8 ms typical, 15 ms max (20 calls) |
| `/gemini-http` (a v3-sized call) | 10 ms typical, **1,525 ms max**; 5 of 21 calls over 500 ms | **18 ms typical, 64 ms max** (20 calls) |
| `/pydantic` | 31 ms (1 call) | 36 ms (1 call) |

Python Workers snapshot what is imported at module level when the Worker deploys, so requests do
not pay for it. Imports inside a handler are paid again by every new copy of the Worker; those are
the 500 to 1,500 ms spikes. Every call completed, including handler-import calls of up to
1,525 ms; only the SDK import, at 1,935 ms, was stopped. Twenty calls in one session do not show
that Cloudflare tolerates overruns over time: its limits page allows only infrequent ones.

**Against the Free plan's documented limits** ([limits
page](https://developers.cloudflare.com/workers/platform/limits/), last modified 2026-11-18):

| Limit | Documented | Measured | Verdict |
|---|---|---|---|
| CPU per request | 10 ms, with "some built-in flexibility" for a Worker that "infrequently" runs over; one that hits the limit "consistently" is terminated (error 1102) | 18 ms typical, 64 ms max (imports at module level) | Over the limit on most calls: the demo's main risk |
| Start-up | 1 s to run the top-level code; deploys over it are rejected (error 10021) | 1,039 to 1,338 ms reported by wrangler; all four deploys accepted | Unexplained (the Python Workers pages could not be read); re-checked in phase 9 |
| Size | 64 MiB uncompressed; no compressed limit | 7.3 MB (27 MB with Google's SDK) | Fine |
| Memory | 128 MB per isolate | Not measured | Phase 9 |

**Cold start.** The first call after 15 minutes with no requests, three times (22:33, 22:48 and
23:04 UTC on 2026-11-18): `/version` answered in 0.74 to 0.93 s at the client, using 5 to 8 ms of
CPU; the `/gemini-http` call right after took 2.2 to 2.7 s, using 22 to 68 ms. That is no slower
than the warm calls: the deploy-time snapshot makes a new copy of the Worker cheap. (Fifteen idle
minutes does not guarantee the Worker was unloaded, but no first call showed a start-up penalty.)

## What it decides

1. **S8: the Python Worker works, provisionally.** The demo can run the same Python router code
   and Pydantic schema that were scored. Whether it stays within the Free plan's limits under real
   use is not shown: CPU is over the documented 10 ms on most calls, and start-up was reported over
   1 s. Phase 9 tests the real v3 code under sustained use; any 1102 error, or a deploy rejected for
   start-up time, switches the demo to the TypeScript fallback (S8). Decided by Ajlal, 2026-11-19:
   keep the Python Worker on these terms.
2. **S2: Workers run Python 3.14**, the same version as development and CI. CI stays on 3.14 alone;
   no second version is needed.
3. **The demo calls Gemini over plain HTTP, not through Google's SDK**, which cannot even be
   imported within the CPU limit. This touches S4, which puts our thin adapters "over each official
   SDK" (see the recommendation).
4. **Free-plan CPU: keep every import at module level.** A v3-sized call then used 18 ms typical
   and 64 ms at most, over the documented 10 ms on most calls. Cloudflare terminates Workers that
   overrun consistently, so this is the demo's main risk. If it bites, the options are the
   TypeScript fallback, which avoids the Python runtime, or Workers Paid ($5 a month), which breaks
   the $0 rule and needs approval.
5. **Cold starts are not a concern** for the demo.

The probe Worker, its Durable Object and its secret were deleted after measuring (2026-11-19).

## Recommendation (S4; approved by Ajlal, 2026-11-19)

Write the provider adapters over each provider's **HTTP API** rather than its SDK, with one small
transport interface: an ordinary HTTP client in CPython (CI, local runs) and `workers.fetch` in the
Worker. The request and response handling, which is what gets measured, is then the same code in
both places, and the demo never drifts from what was scored (an anti-goal in spec section 2). It
also drops the SDK dependencies from the repo, in line with S4's own reason ("fewer dependencies in
a repo whose CI holds keys").

The alternative, the SDK in CI and a separate HTTP client in the Worker, keeps S4 as written but
gives the demo a second code path for the same call.
