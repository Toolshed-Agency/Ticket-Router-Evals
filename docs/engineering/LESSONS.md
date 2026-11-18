# Lessons

What bit us (or nearly did), what to do about it, and where it came from. Added the moment it
happens. Newest first.

| Date | What happened | What to do | Source |
|---|---|---|---|
| 2026-11-18 | A commit went through with a Ruff error: the checks ran with `;` between them, so the failure did not stop `git commit`. | Chain the checks and the commit with `&&`, so any failing check blocks the commit. | Phase 1, Task 5 |
| 2026-11-18 | Ruff 0.17 also formats Python code inside Markdown, and would have rewrapped the plan's snippets. | `extend-exclude = ["*.md"]` in `pyproject.toml`: code in docs is illustrative. | Phase 1, Task 2 |
| 2026-11-18 | A test that `evals` imports from this repo passed even with a fake `evals` package placed ahead of it: pytest puts the repo root first on `sys.path`. OpenAI publishes a package named `evals`. | Check import resolution in a fresh interpreter started outside the repo, the way the installed command runs. Watch a test fail before trusting it. | Phase 1, Task 1 |
| 2026-11-18 | uv's PowerShell installer hung at 0 bytes on Windows PowerShell 5.1. | Download the release zip, check it against its `.sha256`, and extract it to `~/.local/bin`. | Phase 1, Task 1 |
| 2026-11-18 | The first design spec, written from a part-by-part walkthrough of the scope of work, silently missed requirements nobody happened to discuss (Langfuse tracing, the README's contents, launch assets, and more). Two independent line-by-line audits found 73, then 17, gaps and inconsistencies. | Before handing over any spec, trace the source document line by line, ideally by a reviewer who hasn't seen your own list, and record every deliberate difference in the spec itself (section 17). | Design spec review |
| 2026-11-17 | GitHub's Python `.gitignore` template ignores `/site` (MkDocs output), the folder where our website lives. Nothing in it would have been committed. | Read a template `.gitignore` against the repo's layout before relying on it. | Setup |
| 2026-11-17 | Files stored as LF were checked out as CRLF on Windows. A hash of the same file would differ between a laptop and CI, breaking the test-set lock. | `.gitattributes` makes text files LF everywhere. Also normalise line endings in code before hashing data. | Setup |
