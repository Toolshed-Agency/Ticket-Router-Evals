# Lessons

What bit us (or nearly did), what to do about it, and where it came from. Added the moment it
happens. Newest first.

| Date | What happened | What to do | Source |
|---|---|---|---|
| 2026-11-19 | In a Python Worker, imports inside a request handler cost up to 1.5 s of CPU for every new copy of the Worker; importing Google's SDK was stopped at 1.9 s ("exceeded CPU time limit"). | Import at module level, which Python Workers snapshot at deploy (a v3-sized call then used 18 ms typical). Keep heavy SDKs out of Workers. | Phase 1, Task 7 |
| 2026-11-19 | `npx --yes wrangler` hung twice with no output, and pywrangler calls wrangler that way. Separately, piping wrangler through `\| tail` held back its login link until it exited. | Run `pywrangler sync`, then wrangler from its installed path (`node .../wrangler/bin/wrangler.js`). Send CLI output to a file, never through a pipe that buffers. | Phase 1, Task 7 |
| 2026-11-19 | Cloudflare rejected a `compatibility_date` of the local date as "in the future": it checks in UTC. | Use the UTC date. | Phase 1, Task 7 |
| 2026-11-19 | Google's Python SDK has no request timeout by default: one free-tier call hung for 8 minutes. | Set a timeout on every model call. | Phase 1, Task 6 |
| 2026-11-19 | AI Studio listed free quota for Gemini 2.5 Flash, but the API refused it with 404 "no longer available to new users". | Trust a real call over the dashboard. | Phase 1, Task 6 |
| 2026-11-19 | Printing Urdu model output crashed a script on the Windows console, whose default encoding cannot hold it. | `sys.stdout.reconfigure(encoding="utf-8")` in scripts that print model output. | Phase 1, Task 6 |
| 2026-11-18 | A commit went through with a Ruff error: the checks ran with `;` between them, so the failure did not stop `git commit`. | Chain the checks and the commit with `&&`, so any failing check blocks the commit. | Phase 1, Task 5 |
| 2026-11-18 | Ruff 0.17 also formats Python code inside Markdown, and would have rewrapped the plan's snippets. | `extend-exclude = ["*.md"]` in `pyproject.toml`: code in docs is illustrative. | Phase 1, Task 2 |
| 2026-11-18 | A test that `evals` imports from this repo passed even with a fake `evals` package placed ahead of it: pytest puts the repo root first on `sys.path`. OpenAI publishes a package named `evals`. | Check import resolution in a fresh interpreter started outside the repo, the way the installed command runs. Watch a test fail before trusting it. | Phase 1, Task 1 |
| 2026-11-18 | uv's PowerShell installer hung at 0 bytes on Windows PowerShell 5.1. | Download the release zip, check it against its `.sha256`, and extract it to `~/.local/bin`. | Phase 1, Task 1 |
| 2026-11-18 | The first design spec, written from a part-by-part walkthrough of the scope of work, silently missed requirements nobody happened to discuss (Langfuse tracing, the README's contents, launch assets, and more). Two independent line-by-line audits found 73, then 17, gaps and inconsistencies. | Before handing over any spec, trace the source document line by line, ideally by a reviewer who hasn't seen your own list, and record every deliberate difference in the spec itself (section 17). | Design spec review |
| 2026-11-17 | GitHub's Python `.gitignore` template ignores `/site` (MkDocs output), the folder where our website lives. Nothing in it would have been committed. | Read a template `.gitignore` against the repo's layout before relying on it. | Setup |
| 2026-11-17 | Files stored as LF were checked out as CRLF on Windows. A hash of the same file would differ between a laptop and CI, breaking the test-set lock. | `.gitattributes` makes text files LF everywhere. Also normalise line endings in code before hashing data. | Setup |
