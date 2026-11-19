# Probe scripts

Throwaway scripts for the phase 1 probes
([plan](../../plans/2026-11-18-phase-1-foundation.md), Tasks 6 to 8). Each probe's report in the
folder above is the deliverable; these files are kept so the measurements can be repeated. Nothing
in `harness/`, `router/` or `evals/` imports them.

| File | What it is |
|---|---|
| `probe_tickets.jsonl` | Six synthetic tickets written for the probes only. **Never part of the dataset.** Names, emails and account ids are obviously fake |
| `probe_prompt.md` | A stand-in system prompt about the size of v3's. **Not** the Ledgerly prompt, labelling guide or policy, which are written in phases 2 and 5 |
| `probe_schema.py` | The router output fields (spec section 6) as a Pydantic model and JSON schema |
| `gemini_probe.py` | Task 6: Gemini free-tier limits, latency, tokens and structured-output validity |
| `workers_ai_probe.py` | Task 8: open models on Workers AI: validity, latency and neurons per call |

Run from the repo root, with keys in `.env` (see `.env.example`):

```
uv run --env-file .env --group probes python docs/engineering/probes/scripts/gemini_probe.py --help
```

Scripts exit with status 2 and a message when a key they need is not set.
