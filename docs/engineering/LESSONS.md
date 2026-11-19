# Lessons

What bit us (or nearly did), what to do about it, and where it came from. Added the moment it
happens. Newest first.

| Date | What happened | What to do | Source |
|---|---|---|---|
| 2026-11-18 | The first design spec, written from a part-by-part walkthrough of the scope of work, silently missed requirements nobody happened to discuss (Langfuse tracing, the README's contents, launch assets, and more). Two independent line-by-line audits found 73, then 17, gaps and inconsistencies. | Before handing over any spec, trace the source document line by line, ideally by a reviewer who hasn't seen your own list, and record every deliberate difference in the spec itself (section 17). | Design spec review |
| 2026-11-17 | GitHub's Python `.gitignore` template ignores `/site` (MkDocs output), the folder where our website lives. Nothing in it would have been committed. | Read a template `.gitignore` against the repo's layout before relying on it. | Setup |
| 2026-11-17 | Files stored as LF were checked out as CRLF on Windows. A hash of the same file would differ between a laptop and CI, breaking the test-set lock. | `.gitattributes` makes text files LF everywhere. Also normalise line endings in code before hashing data. | Setup |
