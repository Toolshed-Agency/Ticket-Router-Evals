# Lessons

What bit us (or nearly did), what to do about it, and where it came from. Added the moment it
happens. Newest first.

| Date | What happened | What to do | Source |
|---|---|---|---|
| 2026-11-17 | GitHub's Python `.gitignore` template ignores `/site` (MkDocs output), the folder where our website lives. Nothing in it would have been committed. | Read a template `.gitignore` against the repo's layout before relying on it. | Setup |
| 2026-11-17 | Files stored as LF were checked out as CRLF on Windows. A hash of the same file would differ between a laptop and CI, breaking the test-set lock. | `.gitattributes` makes text files LF everywhere. Also normalise line endings in code before hashing data. | Setup |
