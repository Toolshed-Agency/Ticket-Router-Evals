# Phase 1: Foundation and probes. Implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** An empty but properly wired Python project with green checks, plus dated answers to the
five unknowns the design depends on.

**Architecture:** One uv project with three top-level packages (`harness`, `router`, `evals`),
checked by Ruff, mypy and pytest locally and in `ci.yml`, with a structural test that keeps
`harness/` free of Ledgerly code and tests that keep secrets out of git. The probes are throwaway
scripts and one throwaway Worker; their reports, not their code, are the deliverable.

**Tech stack:** Python 3.14, uv 0.13.9 with `uv_build`, Ruff 0.17.5, mypy 2.4.1, pytest 9.2.0,
actionlint, gitleaks 8.30.1, GitHub Actions. Probes only: google-genai, Pydantic, Cloudflare
Python Workers (`pywrangler`), Workers AI, Cloudflare Pages.

**Spec:** [docs/engineering/specs/2026-11-17-ticket-router-evals-design.md](../specs/2026-11-17-ticket-router-evals-design.md)
(phase 1 row in section 14; probes in section 15; S2, S3, S8, S11, S13, D1, D9, D10, D11).

**Branch:** `phase-1/foundation`, from `docs/design-spec`. As of 2026-11-18.

**Not in this phase:** schemas, the CLI, any router, the dataset, the site. Phase 1 creates no
runtime dependency; Pydantic joins the project with the schemas in phase 2. The spec's other
folders (`data/`, `context/`, `results/`, `site/`, `demo/`) appear with their first file, since
git does not keep empty folders.

## Preconditions

| Check | Result (2026-11-18) | How checked |
|---|---|---|
| Spec approved | Yes, at commit 866d332 | Ajlal, in conversation |
| Branch base | `docs/design-spec` (contains `phase-0/setup`); `main` has only the initial commit; nothing pushed | `git branch -a` |
| Python 3.14 | 3.14.3 at `C:\Python314` | `py -0p` |
| uv | Not installed (Task 1 installs it) | `uv --version` |
| Git author | Syed Ajlal Haider, work email; push account bound to `ajlalhaider-toolshed` | `git config user.email`, `git config credential.https://github.com.username` |
| Node and npm (for wrangler) | 24.14.0 and 11.9.0; wrangler not installed (latest 4.164.0) | `node --version`, `npx --no-install wrangler --version` |
| Google AI Studio key | **Ajlal to create** (Task 6) | |
| Cloudflare account | **Open: decision P1-D6** (Tasks 7 to 9) | |
| Subdomain and one CNAME at the DNS host | **Asks 1 and 6, not sent** (Task 9 only) | `project_reference/asks.md` |

## Environment facts (checked 2026-11-18)

| Tool | Latest | Source |
|---|---|---|
| uv / uv_build | 0.13.9 | PyPI |
| Ruff | 0.17.5 | PyPI |
| mypy | 2.4.1 | PyPI |
| pytest | 9.2.0 | PyPI |
| actionlint-py | 1.7.12.25 | PyPI |
| google-genai | 3.5.0 | PyPI |
| Pydantic | 2.14.3 | PyPI |
| workers-py (pywrangler) | 1.17.9 | PyPI |
| Pyodide | 314.0.8 (suggests Python 3.14; Task 7 confirms what Workers run) | GitHub releases |
| actions/checkout | v7.0.1 | GitHub releases |
| astral-sh/setup-uv | v10.3.3 | GitHub releases |
| gitleaks | v8.30.1 | GitHub releases |
| Workers AI free allocation | 10,000 neurons a day on Workers Free; Free cannot exceed it; some models need Paid | Cloudflare Workers AI pricing page |
| Gemini free-tier limits | Per project and per model, daily reset at midnight Pacific; the docs no longer list numbers, AI Studio shows them per project | Gemini API rate-limits page |

## Sticky decisions (approved with this plan)

| Id | Decision | Alternatives | Why |
|---|---|---|---|
| P1-D1 | **Build backend `uv_build`**, flat layout (`module-root = ""`), `module-name = ["harness", "router", "evals"]` | hatchling; a uv workspace of three packages | One project, as the spec accepts (section 5). uv's own backend, no extra tool. uv's docs prefer a workspace for several modules but support the list; a workspace would add three `pyproject.toml` files for no gain |
| P1-D2 | **mypy 2.4.1 in strict mode** as the type checker (spec section 16 left the choice to the builder) | pyright (runs on Node); ty (version 0.0.x, pre-release) | Pure Python, mature, has a Pydantic plugin for phase 2. A credibility-first repo should not depend on a pre-release checker |
| P1-D3 | **Pins.** Dev tools exact: `ruff==0.17.5`, `mypy==2.4.1`, `pytest==9.2.0`, `actionlint-py==1.7.12.25`. Probe libraries with lower bounds in a `probes` dependency group: `google-genai>=3.5.0`, `pydantic>=2.14.3`. `uv.lock` committed; CI runs `uv sync --locked`. `requires-python = ">=3.14"` and `.python-version` = `3.14` until Task 7 says otherwise (S2) | Ranges everywhere | A tool upgrade changes lint and type results; each bump becomes its own reviewed commit |
| P1-D4 | **Ruff rules:** `E, W, F, I, B, UP, SIM, RUF, PT, S`; line length 100; `ruff format` as the formatter. In tests, `S101` (assert) and `S603`/`S607` (subprocess) allowed | Ruff defaults (`E`, `F`); `ALL` | Catches real bugs and security smells without noise |
| P1-D5 | **CI:** every action pinned to a full commit SHA with its version in a comment; `permissions: contents: read`; triggers `push`, `pull_request`, `workflow_dispatch` | Version tags (`@v7`) | `ci.yml` will sit beside workflows that hold keys; a moved tag cannot change our CI |
| P1-D6 | **Cloudflare account for the probes.** Send ask 6 now. If Toolshed's account is not ready when Task 7 starts, Ajlal creates a free account with the work email, names probe resources `zzz-probe-*`, and deletes them after; the account is handed over or closed when Toolshed's exists | Wait for ask 6 | Unblocks Tasks 7 and 8 without spending anything. The account stays on Workers Free, which cannot bill |
| P1-D7 | **Probes deploy from the laptop**, an exception to S10 ("deploys only from GitHub Actions"): throwaway Workers and one Pages project, from folders with no `.env`, deleted after | Build a CI deploy for probes | S10 protects the product; the deploy pipeline is phase 9's job |
| P1-D8 | **Secret checks:** the gitleaks CLI (MIT licence) scans the full history in CI, its download checked against the release checksums; tests keep `.env` files out of git; GitHub secret scanning and push protection switched on for the repo (an org admin's setting, asked before changing) | The gitleaks GitHub Action (needs a licence key for organisation repos and sends the repo name to its licence server); trufflehog | No licence, no third-party call, one pinned binary |
| P1-D9 | **The Pages probe uses the production project name** (`ticket-router-evals`), so the CNAME made for the probe never changes. After verifying, the custom domain is detached, so nothing is public on the subdomain until launch | A throwaway project name, then a second CNAME change in phase 9 | One DNS change at the company's DNS host, as promised in D11 |

**Shaped (flagged, not blocking):**
- Probe scripts live in `docs/engineering/probes/scripts/`, the probe Worker in
  `docs/engineering/probes/python-worker/`, and reports in `docs/engineering/probes/`. This keeps
  the spec's layout unchanged. Probe code is never imported by the packages.
- Six synthetic probe tickets, used only by the probes and never reused in the dataset.
- Probe scripts are not test-first: CLAUDE.md's test-first list does not cover them, and their
  report is the deliverable. They still pass Ruff and fail closed.

**Stop rule for probes.** Where the spec has already decided the fallback (the S8 TypeScript
fallback, the D10 fallbacks, the D4 drop of the ablation, Workers AI left out of the comparison),
apply it and flag it in the report. Any result outside those stops work for a decision.

## Global constraints

- Python 3.14 for development and CI; the router package must also run on the Python Workers
  version, and CI tests both (S2).
- uv, Ruff, pytest, Pydantic v2 and a static type checker (S3).
- `harness/` must not import from `router/` or `evals/`, or read `data/` or `context/` (D1).
- $0 a month. Confirm each service's free-tier limits before enabling it; flag anything that could
  bill. A Gemini key must come from a project with **no billing account**, or usage is billed at
  paid rates.
- No secrets in the repo or its history. Keys only in `.env` (gitignored), GitHub secrets and
  Cloudflare secrets.
- Fail closed: missing config turns a feature off with a visible message.
- Anything Ledgerly-like, the probe tickets included, is obviously fake and resembles no real
  company.
- Text files are LF everywhere (`.gitattributes`).
- Commits follow CLAUDE.md (Conventional Commits, project scopes, imperative summary under 72
  characters). They are authored by Syed Ajlal Haider with the work email and carry **no AI
  attribution** (no `Co-Authored-By` trailer for any AI tool).
- Never commit to `main`; never push or open a pull request without asking.
- Engineering docs are public: write them for an outside developer.

## Review focus

Inputs and failures the spec implies but nothing else in this plan tests, most likely first. Each
has a test in the task named.

1. **An import that dodges the boundary check:** `importlib.import_module("router.v1")`,
   `__import__("evals")`, `import evals.metrics as m`. Expected: flagged. (Task 3)
2. **Windows-style or built paths:** `"data\\tickets_dev.jsonl"`, `Path("context") / "policies.md"`,
   `base / "data"`. Expected: flagged; `payload["data"]` and `"metadata/x"` are not. (Task 3)
3. **A harness file that does not parse.** Expected: a violation naming the file, never a silent
   skip. (Task 3)
4. **A boundary scan that finds no files** (wrong root, renamed folder). Expected: the test fails
   rather than passing with nothing checked. (Task 3)
5. **A change that pulls a secret into `ci.yml` or widens its permissions.** `ci.yml` runs on fork
   pull requests. Expected: a test fails. (Task 5)

## File structure

| Path | Task | Responsibility |
|---|---|---|
| `pyproject.toml`, `.python-version`, `uv.lock` | 1, 2 | Project, pins, tool configuration |
| `harness/__init__.py`, `router/__init__.py`, `evals/__init__.py` | 1 | The three packages (docstring only) |
| `tests/__init__.py`, `tests/test_packages.py` | 1 | Imports resolve to this repo |
| `tests/boundary_check.py`, `tests/test_boundary.py` | 3 | D1 boundary checker and its tests |
| `.env.example`, `tests/test_secret_hygiene.py` | 4 | Env file rules |
| `.github/workflows/ci.yml`, `tests/test_ci_workflow.py` | 5 | CI and its structural tests |
| `docs/engineering/probes/scripts/` | 6, 8 | Probe tickets, prompt stand-in, output schema, scripts |
| `docs/engineering/probes/python-worker/` | 7 | The throwaway Worker |
| `docs/engineering/probes/2026-11-DD-<name>.md` | 6 to 10 | Dated probe reports |
| `.gitignore` | 4, 7 | Adds `python_modules/`, `.wrangler/` |
| `CLAUDE.md`, `docs/engineering/OPEN-WORK.md`, spec | 2, 11 | Commands, status, probe outcomes |

---

### Task 1: uv project with three packages

**Files:**
- Create: `pyproject.toml`, `.python-version`, `uv.lock`, `harness/__init__.py`,
  `router/__init__.py`, `evals/__init__.py`, `tests/__init__.py`, `tests/test_packages.py`

**Interfaces:**
- Produces: importable packages `harness`, `router`, `evals`; `tests/__init__.py` defines
  `REPO_ROOT: Path = Path(__file__).resolve().parents[1]`, imported by every test module as
  `from tests import REPO_ROOT`.

- [ ] **Step 1: Install uv 0.13.9.** In PowerShell:
  `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/0.13.9/install.ps1 | iex"`.
  Verify: a new shell prints `uv 0.13.9` for `uv --version`.
- [ ] **Step 2: Install Python 3.14 through uv.** `uv python install 3.14`. Verify:
  `uv python find 3.14` prints a path.
- [ ] **Step 3: Write `pyproject.toml`** with name `ticket-router-evals`, version `0.1.0`, a
  one-line description, `requires-python = ">=3.14"`, `license = "MIT"`, no runtime
  dependencies, `[build-system]` on `uv_build>=0.13.9,<0.14`, and
  `[tool.uv.build-backend]` with `module-root = ""` and
  `module-name = ["harness", "router", "evals"]` (P1-D1). Dependency groups:
  `dev = ["pytest==9.2.0"]` for now. Write `.python-version` as `3.14`. Each package's
  `__init__.py` holds a one-line docstring saying what the package is for (spec section 5).
- [ ] **Step 4: Write the test** `tests/test_packages.py`:

```python
import evals
import harness
import router

def test_packages_resolve_to_this_repo() -> None:
    # `evals` is also the name of OpenAI's package on PyPI; a stray install must never shadow ours.
    for module in (harness, router, evals):
        assert module.__file__
        assert Path(module.__file__).resolve().parent == REPO_ROOT / module.__name__
```

- [ ] **Step 5: Run it.** `uv run pytest tests/test_packages.py -v`. Expected: PASS.
- [ ] **Step 5b: Watch it fail.** Put a fake `evals/__init__.py` in a scratch folder outside the
  repo and run the test with `PYTHONPATH` set to that folder. Expected: FAIL on `evals`. Unset it;
  PASS again.
- [ ] **Step 6: Check the wheel carries exactly the three packages.**
  `uv build --wheel` then list the wheel's top-level entries (Python `zipfile`). Expected:
  `harness/`, `router/`, `evals/` and the `.dist-info` folder only. Delete `dist/`.
- [ ] **Step 7: Commit.**
  `git add pyproject.toml .python-version uv.lock harness router evals tests && git commit -m "build: add uv project with harness, router and evals packages"`

### Task 2: Lint, format, type check and test configuration

**Files:**
- Modify: `pyproject.toml` (`[dependency-groups]`, `[tool.ruff]`, `[tool.mypy]`,
  `[tool.pytest.ini_options]`), `uv.lock`, `CLAUDE.md` (Commands)

- [ ] **Step 1: Add the pinned dev tools** (P1-D3): `uv add --dev ruff==0.17.5 mypy==2.4.1`.
- [ ] **Step 2: Configure Ruff** (P1-D4): `target-version = "py314"`, `line-length = 100`,
  `lint.select` as decided, per-file ignores `"tests/**" = ["S101", "S603", "S607"]`, each
  ignore with a comment saying why.
- [ ] **Step 3: Configure mypy:** `strict = true`, `python_version = "3.14"`,
  `files = ["harness", "router", "evals", "tests"]`.
- [ ] **Step 4: Configure pytest:** `testpaths = ["tests"]`, `pythonpath = ["."]`,
  `addopts = "-ra --strict-markers --strict-config"`, `xfail_strict = true`.
- [ ] **Step 5: Verify all four pass:**
  `uv run ruff format --check . ; uv run ruff check . ; uv run mypy ; uv run pytest`. Expected:
  no findings, 1 test passed.
- [ ] **Step 6: Break each once.** Add an unused `import os` to `harness/__init__.py`: `ruff check`
  fails with F401. Add `def f(x): return x`: `mypy` fails (missing annotations). Revert both;
  all pass again.
- [ ] **Step 7: Update CLAUDE.md "Commands"** with `uv sync`, `uv run ruff format .`,
  `uv run ruff check .`, `uv run mypy`, `uv run pytest`, one line each on what it does.
- [ ] **Step 8: Commit.**
  `git add pyproject.toml uv.lock CLAUDE.md && git commit -m "build: configure ruff, mypy and pytest"`

### Task 3: Boundary test (D1)

**Files:**
- Create: `tests/boundary_check.py`, `tests/test_boundary.py`

**Interfaces:**
- Produces:
  - `@dataclass(frozen=True) class Violation: path: Path; line: int; reason: str`
  - `def find_violations(root: Path) -> list[Violation]`. Raises `ValueError` naming `root` when
    it contains no `.py` files.
  - `FORBIDDEN_MODULES = ("router", "evals")`, `FORBIDDEN_DIRS = ("data", "context")`.

**Rules the checker applies** to every `.py` file under `root`:
- An import of a forbidden module or its submodules: `import`, `from … import`, and string
  arguments to `importlib.import_module` and `__import__`.
- A string constant that contains `/` or `\` and has a segment equal to `data` or `context`
  (`"data/x"`, `"data\\x"`; not `"metadata/x"`).
- A bare `"data"` or `"context"` used as a path: an argument to a call named `Path`, `PurePath`,
  `open`, `join` or `joinpath`, or an operand of `/`. A subscript such as `payload["data"]` is not
  a path.
- The word "ledgerly" anywhere in the file, comments included (case-insensitive).
- A file that does not parse is a violation, with the parser's message.
- One violation per offending node, so the tests can count them.

- [ ] **Step 1: Write the failing tests.** Each writes a module into `tmp_path / "harness"` and
  calls `find_violations`:

```python
@pytest.mark.parametrize("source", [
    "import router", "from evals.metrics import x", "import evals.metrics as m",
    "import importlib\nimportlib.import_module('router.v1')", "__import__('evals')",
    "p = 'data/tickets_dev.jsonl'", "p = 'data\\\\tickets_dev.jsonl'",
    "from pathlib import Path\np = Path('context') / 'policies.md'",
    "from pathlib import Path\np = Path('.') / 'data'", "open('data')",
    "# Ledgerly-specific shortcut", "def f(:\n",
])
def test_flags(tmp_path: Path, source: str) -> None:
    assert len(find_violations(write(tmp_path, source))) == 1

@pytest.mark.parametrize("source", [
    "x = {}\ny = x['data']", "p = 'metadata/x'", "d = 'dataset'", "import json",
])
def test_allows(tmp_path: Path, source: str) -> None:
    assert find_violations(write(tmp_path, source)) == []

def test_reports_file_and_line(tmp_path: Path) -> None:
    [v] = find_violations(write(tmp_path, "import json\nimport router"))
    assert (v.path.name, v.line) == ("mod.py", 2)

def test_empty_root_fails(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="no .py files"):
        find_violations(tmp_path)

def test_harness_respects_the_boundary() -> None:
    assert find_violations(REPO_ROOT / "harness") == []
```

  `write(tmp_path, source) -> Path` is a test helper that writes `harness/mod.py` and returns the
  `harness` folder.
- [ ] **Step 2: Run them.** `uv run pytest tests/test_boundary.py -v`. Expected: FAIL
  (`ModuleNotFoundError: tests.boundary_check`).
- [ ] **Step 3: Implement `find_violations`** in `tests/boundary_check.py` with `ast` for imports,
  calls and constants, plus a plain-text search for "ledgerly" (comments are not in the AST).
- [ ] **Step 4: Run them.** Expected: all PASS.
- [ ] **Step 5: Break it once.** Add `import router` to `harness/__init__.py`:
  `test_harness_respects_the_boundary` fails naming the file and line 1 or 2. Revert.
- [ ] **Step 6: Lint and type check.** `uv run ruff check . ; uv run mypy`. Expected: clean.
- [ ] **Step 7: Commit.**
  `git add tests/boundary_check.py tests/test_boundary.py && git commit -m "test(harness): enforce the harness boundary (D1)"`

### Task 4: Secret hygiene

**Files:**
- Create: `.env.example`, `tests/test_secret_hygiene.py`
- Modify: `.gitignore` (add `python_modules/` and `.wrangler/` under a "Cloudflare probes" comment)

- [ ] **Step 1: Write the failing tests.** A module helper
  `git(*args: str) -> subprocess.CompletedProcess[str]` runs git in `REPO_ROOT` with captured
  text output. If `git` is missing the tests fail, never skip.

```python
@pytest.mark.parametrize("name", [".env", ".env.local", ".env.production"])
def test_env_files_are_ignored(name: str) -> None:
    assert git("check-ignore", "-q", name).returncode == 0

def test_env_example_is_tracked() -> None:
    assert git("check-ignore", "-q", ".env.example").returncode == 1
    assert git("ls-files", ".env.example").stdout.strip() == ".env.example"

def test_env_example_holds_names_only() -> None:
    for line in (REPO_ROOT / ".env.example").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            assert re.fullmatch(r"[A-Z][A-Z0-9_]*=", line), line

def test_no_env_file_is_tracked() -> None:
    names = {Path(p).name for p in git("ls-files").stdout.splitlines()} - {".env.example"}
    assert {n for n in names if n.startswith(".env") or n.endswith(".env")} == set()
```

- [ ] **Step 2: Run them.** Expected: `test_env_example_is_tracked` and
  `test_env_example_holds_names_only` FAIL (no file).
- [ ] **Step 3: Write `.env.example`**: a header comment ("Copy to `.env`. Never commit `.env`."),
  then `GEMINI_API_KEY=`, `CLOUDFLARE_ACCOUNT_ID=`, `CLOUDFLARE_API_TOKEN=`, each under a comment
  saying where to get it and which task uses it. `git add .env.example`. Update `.gitignore`.
- [ ] **Step 4: Run them.** Expected: all PASS.
- [ ] **Step 5: Scan the full history locally.** Download the gitleaks 8.30.1 Windows zip and the
  checksums file into the scratch folder (outside the repo), check the SHA-256, then run
  `gitleaks git --redact -v .` from the repo root. Expected: "no leaks found" over every commit on
  the branch. A finding is investigated, never allowlisted without a comment saying why.
- [ ] **Step 6: Check GitHub's own secret scanning.** Ask before changing anything. Read the
  repo's setting with `gh api repos/Toolshed-Agency/Ticket-Router-Evals --jq .security_and_analysis`
  (it may need an org admin). If secret scanning or push protection is off, add it to the asks for
  an org admin.
- [ ] **Step 7: Commit.**
  `git add .env.example .gitignore tests/test_secret_hygiene.py && git commit -m "test: keep env files and secrets out of git"`

### Task 5: `ci.yml`

**Files:**
- Create: `.github/workflows/ci.yml`, `tests/test_ci_workflow.py`
- Modify: `pyproject.toml`, `uv.lock` (`actionlint-py==1.7.12.25` in `dev`)

- [ ] **Step 1: Write the failing tests:**

```python
CI = REPO_ROOT / ".github" / "workflows" / "ci.yml"

def test_ci_uses_no_secrets() -> None:  # it runs on fork pull requests
    text = CI.read_text(encoding="utf-8")
    assert "secrets." not in text and "pull_request_target" not in text

def test_ci_is_read_only() -> None:
    text = CI.read_text(encoding="utf-8")
    assert re.search(r"^permissions:\n  contents: read$", text, re.MULTILINE)
    assert "write" not in text

def test_actions_are_pinned_to_commits() -> None:
    uses = re.findall(r"uses:\s*(\S+)", CI.read_text(encoding="utf-8"))
    assert uses and all(re.search(r"@[0-9a-f]{40}$", u) for u in uses)

def test_actionlint_passes() -> None:
    assert shutil.which("actionlint"), "actionlint missing: uv sync"
    assert subprocess.run(["actionlint", str(CI)]).returncode == 0
```

- [ ] **Step 2: Run them.** Expected: FAIL (`ci.yml` missing).
- [ ] **Step 3: Resolve the action SHAs.**
  `gh api repos/actions/checkout/commits/v7.0.1 --jq .sha` and the same for
  `astral-sh/setup-uv` at `v10.3.3`. Record both in the execution log.
- [ ] **Step 4: Write `ci.yml`:**

```yaml
name: ci
on: { push: {}, pull_request: {}, workflow_dispatch: {} }
permissions:
  contents: read
concurrency:
  group: ci-${{ github.event_name }}-${{ github.ref }}
  cancel-in-progress: true
jobs:
  checks:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    strategy:
      matrix:
        python: ["3.14"]  # Task 11 adds the Python Workers version if it differs (S2)
    steps:
      - uses: actions/checkout@<sha>  # v7.0.1
        with: { persist-credentials: false }
      - uses: astral-sh/setup-uv@<sha>  # v10.3.3
        with: { python-version: "${{ matrix.python }}", enable-cache: true }
      - run: uv sync --locked
      - run: uv run ruff format --check .
      - run: uv run ruff check .
      - run: uv run mypy
      - run: uv run pytest
  secret-scan:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@<sha>  # v7.0.1
        with: { fetch-depth: 0, persist-credentials: false }
      # Download gitleaks_8.30.1_linux_x64.tar.gz and gitleaks_8.30.1_checksums.txt from the
      # v8.30.1 release, `sha256sum --check --ignore-missing`, extract, then:
      - run: ./gitleaks git --redact --exit-code 1 -v .
```

  Steps added by later phases (`validate-data`, the site build, the numbers-match test) are not
  added now.
- [ ] **Step 5: Run the tests.** `uv run pytest -v`. Expected: all PASS.
- [ ] **Step 6: Break one.** Change `contents: read` to `contents: write`:
  `test_ci_is_read_only` fails. Revert.
- [ ] **Step 7: Prove `uv sync --locked` guards the lockfile.** Add a dependency to
  `pyproject.toml` without `uv lock`: `uv sync --locked` fails. Revert.
- [ ] **Step 8: Commit.**
  `git add .github/workflows/ci.yml tests/test_ci_workflow.py pyproject.toml uv.lock && git commit -m "ci: add lint, type check, test and secret scan workflow"`

  The workflow first runs on GitHub when the branch is pushed (Task 12, after asking).

### Task 6: Probe: Gemini free tier

**Question:** what are the real free-tier limits for the development model and a candidate judge,
and how long does one v3 dev run take? Decides CI timing, whether the ablation fits (D4), and
whether D10's fallbacks are needed.

**Files:**
- Create: `docs/engineering/probes/scripts/probe_tickets.jsonl`,
  `docs/engineering/probes/scripts/probe_prompt.md`,
  `docs/engineering/probes/scripts/probe_schema.py`,
  `docs/engineering/probes/scripts/gemini_probe.py`,
  `docs/engineering/probes/2026-11-DD-gemini-free-tier.md`
- Modify: `pyproject.toml`, `uv.lock` (group `probes = ["google-genai>=3.5.0", "pydantic>=2.14.3"]`)

**Interfaces:**
- Produces, for Tasks 7 and 8: `probe_tickets.jsonl` (six records: `id`, `channel`, `subject`,
  `body`, `customer_tier`, `prior_tickets_7d`); `probe_prompt.md`; and in `probe_schema.py`,
  `class ProbeOutput(BaseModel)` with the seven router-output fields and their allowed values
  (spec section 6) plus `PROBE_OUTPUT_JSON_SCHEMA: dict[str, object]`.

- [ ] **Step 1: Ajlal creates the key.** In Google AI Studio, on a work-owned project with **no
  billing account** (otherwise calls are billed at paid rates), create an API key and put it in
  `.env` as `GEMINI_API_KEY`. Read the project's rate limits page and copy requests per minute,
  tokens per minute and requests per day for each candidate model into the report, with the date.
- [ ] **Step 2: Write the probe inputs.** Six tickets for Ledgerly, obviously fake, and labelled
  "probe only, never part of the dataset": two `en`, two `roman_ur`, one `ur`, one `mixed`.
  Among them, one outage during month-end close (P1) and one injection attempt. The prompt
  stand-in is about v3's size: team and urgency definitions, escalation and language rules, and a
  one-page stand-in policy, headed "Probe stand-in; not the Ledgerly policy".
- [ ] **Step 3: Write `gemini_probe.py`**, run as `uv run --env-file .env --group probes python docs/engineering/probes/scripts/gemini_probe.py <model-id>`.
  - If `GEMINI_API_KEY` is unset, it prints "GEMINI_API_KEY is not set; copy .env.example to .env"
    and exits 2.
  - `--list` prints every model id available to the key.
  - Otherwise it sends each ticket three times with the prompt, native structured output
    (`PROBE_OUTPUT_JSON_SCHEMA`) and temperature 0, waiting between calls to stay under the
    recorded RPM.
  - It prints per call: latency, input and output tokens, and whether `ProbeOutput` validated.
- [ ] **Step 4: Run it** without a key (expect the message and exit 2), then `--list`, then on the
  current Flash-class model and on one candidate judge model. Record exact model ids.
- [ ] **Step 5: Confirm the enforced limit.** A burst of RPM + 2 calls inside one minute on the
  development model, stopping at the first 429. Record the quota metric and value from the error
  details.
- [ ] **Step 6: Write the report:** question, date, method, results (limits, latency p50 and p95,
  tokens per call, validity), then the arithmetic. Assume v3 makes 2 calls per ticket on ~142 dev
  tickets. Work out:
  - minutes per run
  - calls per day for a pull-request gate run with re-runs
  - the ablation (5 switches)
  - `--repeat 3`

  End with what each result decides (D4, D10, CI timing) and a recommendation.
- [ ] **Step 7: Commit.**
  `git add docs/engineering/probes pyproject.toml uv.lock && git commit -m "docs: record the gemini free tier probe"`

### Task 7: Probe: Python Workers

**Question:** which Python version do Python Workers run? Do Pydantic and Google's SDK work, or
only plain HTTP? How long are cold starts and CPU time? Can Python reach a Durable Object?
Decides S8 and the minimum Python version in S2.

**Files:**
- Create: `docs/engineering/probes/python-worker/` (`pyproject.toml`, `wrangler.toml`,
  `src/entry.py`, a copy of `probe_schema.py`),
  `docs/engineering/probes/2026-11-DD-python-workers.md`

- [ ] **Step 1: Account** per P1-D6. Confirm the account is on Workers Free (dashboard, Workers
  plans) before deploying.
- [ ] **Step 2: Install pywrangler.** `uv tool install workers-py==1.17.9`. Verify
  `pywrangler --help` runs.
- [ ] **Step 3: Write the Worker** `zzz-probe-python-worker`. `wrangler.toml` sets an explicit
  `account_id`, today's `compatibility_date`, the `python_workers` flag, and a Durable Object
  binding `COUNTER` with a `new_sqlite_classes` migration. The routes:
  - `/version`: `sys.version` and the Pyodide version
  - `/pydantic`: validates a sample output with `ProbeOutput`; returns the Pydantic version and
    the time taken
  - `/gemini-http`: one probe ticket to Gemini over plain HTTP with structured output; returns
    the validated output and latency
  - `/gemini-sdk`: tries `from google import genai` and one call; returns success or the error
  - `/counter`: increments the Durable Object's SQLite counter and returns the count

  If the `GEMINI_API_KEY` secret is missing, the Gemini routes answer 503 "probe not configured".
- [ ] **Step 4: Deploy.** `pywrangler deploy`; set the key with `wrangler secret put
  GEMINI_API_KEY`. Record the reported startup time and upload size against the Free plan's
  limit.
- [ ] **Step 5: Measure.**
  - Call every route once.
  - Twenty warm calls to `/version` and to `/gemini-http`: record p50 and p95.
  - First-call latency after 15 minutes idle, three times.
  - CPU time per request from the dashboard's Worker metrics (Free documents 10 ms).
- [ ] **Step 6: Delete the Worker.** Run `wrangler delete`, then confirm it no longer appears in
  the dashboard.
- [ ] **Step 7: Write the report.** What it decides:
  - **S8:** a Python Worker, or the TypeScript fallback.
  - **S2:** the Workers Python version, applied in Task 11.
  - **Demo client:** whether it uses Google's SDK or plain HTTP.
  - **Free plan CPU:** whether the demo fits Free's CPU limit.
- [ ] **Step 8: Commit.**
  `git add docs/engineering/probes .gitignore && git commit -m "docs: record the python workers probe"`

### Task 8: Probe: Workers AI

**Question:** can an open model on Workers AI run v3 within the free daily allocation, and how
does its Urdu and Roman Urdu read? Decides whether it joins the comparison and could serve the
demo everywhere (D9).

**Files:**
- Create: `docs/engineering/probes/scripts/workers_ai_probe.py`,
  `docs/engineering/probes/2026-11-DD-workers-ai.md`

- [ ] **Step 1: Token.** A Cloudflare API token limited to Workers AI on the probe account, in
  `.env` as `CLOUDFLARE_API_TOKEN`, with `CLOUDFLARE_ACCOUNT_ID`. The script exits 2 with a
  message if either is unset.
- [ ] **Step 2: Choose candidates.** List text-generation models through the REST API. Pick two
  or three that work on Workers Free and support JSON-schema output. Record ids and their neuron
  rates from the pricing page, with the date.
- [ ] **Step 3: Run** the six probe tickets with `probe_prompt.md` and `PROBE_OUTPUT_JSON_SCHEMA`.
  Record per call: validity, tokens, latency and neurons.
- [ ] **Step 4: First look at language.** Quote the Urdu, Roman Urdu and mixed drafts in the
  report with Ajlal's one-line read of each. This is a first look, not a score.
- [ ] **Step 5: Write the report** with the arithmetic:
  - neurons per request against 10,000 a day
  - demo capacity at 50 requests a day
  - days for one v3 dev run (~142 tickets, 2 calls each)

  Then what it decides (D9, S11) and a recommendation.
- [ ] **Step 6: Revoke the token** unless Task 11 keeps Workers AI in the plan. Commit.
  `git add docs/engineering/probes && git commit -m "docs: record the workers ai probe"`

### Task 9: Probe: Pages custom domain through a CNAME

**Question:** does a Pages project serve the chosen subdomain through one CNAME at an external DNS
host (D11)? **Needs asks 1 and 6 answered.** If they are still open at the end of the phase, this
task moves to OPEN-WORK. It blocks phase 9 only.

**Files:**
- Create: `docs/engineering/probes/2026-11-DD-pages-custom-domain.md`

- [ ] **Step 1: Create the project** `ticket-router-evals` (P1-D9). Deploy a one-file
  `index.html` ("Coming soon", `noindex`) with `wrangler pages deploy` from a scratch folder.
- [ ] **Step 2: Add the custom domain** in the dashboard and copy the CNAME target it asks for.
  The person with DNS access adds it.
- [ ] **Step 3: Verify.** `nslookup <subdomain>` shows the CNAME, and `curl -sI https://<subdomain>`
  answers 200 with a valid certificate. Record the time from adding the record to active.
- [ ] **Step 4: Detach the custom domain** (P1-D9). Keep the project and the record for phase 9.
- [ ] **Step 5: Write the report and commit.**
  `git add docs/engineering/probes && git commit -m "docs: record the pages custom domain probe"`

### Task 10: Probe: Langfuse free tier

**Question:** what does Langfuse Cloud's free plan allow? Confirms S13 before tracing is first
switched on in phase 4. No account is created.

**Files:**
- Create: `docs/engineering/probes/2026-11-DD-langfuse-free-tier.md`

- [ ] **Step 1: Record** the free plan's limits from Langfuse's pricing page and docs, with the
  date and source URLs. Cover: units per month, data retention, users, data region, whether a
  credit card is needed, and what happens at the limit (stops or bills).
- [ ] **Step 2: Work out** the units one traced v3 dev run would use (calls per run from Task 6).
  State whether tracing stays optional and off by default as S13 says.
- [ ] **Step 3: Commit.**
  `git add docs/engineering/probes && git commit -m "docs: record langfuse free tier limits"`

### Task 11: Apply the probe results

**Files:**
- Modify (as the results require): `pyproject.toml`, `.github/workflows/ci.yml`, the spec,
  `CLAUDE.md`, `docs/engineering/OPEN-WORK.md`, `docs/engineering/LESSONS.md`

- [ ] **Step 1: The Workers Python version** (from Task 7), if it is not 3.14:
  - Set `requires-python` to it, along with Ruff's `target-version` and mypy's `python_version`.
  - Add it to the CI matrix.
  - Run `uv run --python <version> pytest`. Expected: PASS.
- [ ] **Step 2: Fix the spec where the probes settled something**, in the same commit:
  - S2: the version
  - S8: the Python Worker or the fallback
  - S11 and D9: Workers AI in or out
  - D4 and D10: whether the ablation fits, and which fallbacks apply
  - section 15: each probe marked done, with a link to its report

  Anything outside the spec's own fallbacks follows the stop rule.
- [ ] **Step 3: Update the docs.**
  - **CLAUDE.md:** status line, commands.
  - **OPEN-WORK:** remove what shipped; add the open probes (Task 9 if waiting) and the follow-ups
    the reports name.
  - **LESSONS:** add anything that bit.
- [ ] **Step 4: Verify the whole suite.** Run `uv sync --locked`, `uv run ruff format --check .`,
  `uv run ruff check .`, `uv run mypy`, `uv run pytest` and `gitleaks git --redact -v .`. Expected:
  all clean.
- [ ] **Step 5: Commit**, with the `docs:` type, or `build:` if Step 1 changed the version.

### Task 12: End of phase

- [ ] **Step 1: Review.** Run one review of the whole branch against this plan and the spec, by a
  reviewer who has not seen the work. Fix what holds up; record what does not, with the reason.
- [ ] **Step 2: Ask Ajlal** before pushing. Then push `phase-0/setup`, `docs/design-spec` and
  `phase-1/foundation`, and open their pull requests into `main` in that order.
- [ ] **Step 3: Verify on GitHub.** Both `ci.yml` jobs are green on the pull request. Paste the
  run URL into the execution log.

## Known pitfalls

- **Git Bash path rewriting.** Git Bash rewrites `/`-prefixed arguments: prefix
  `MSYS_NO_PATHCONV=1` for `gh api` paths and wrangler routes. PowerShell 5.1 has no `&&`.
- **Line endings.** Python's `write_text` writes CRLF on Windows. `.gitattributes` makes commits
  LF; check new files with `git ls-files --eol`.
- **Gemini free-tier data use.** Google may use free-tier content to improve its products, so
  only the synthetic probe tickets are sent.
- **Gemini limits.** Limits are per project and per model, not per key, and daily quotas reset at
  midnight Pacific.
- **Wrangler accounts.** Wrangler will not guess between two visible accounts: set `account_id`
  in the file.
- **A missing `wrangler.toml` key** can keep a previously deployed value.
- **gh's active account** is not the push account. Use the per-repo credential binding for git,
  and `gh auth switch` only for `gh` itself.

## Rollback

Everything in the repo is additive on this branch: drop the branch to undo it. Cloud resources
are listed and deleted:
- the probe Worker (Task 7)
- the Workers AI token (Task 8)
- the Pages project, if phase 9 should not reuse it (Task 9)

The Gemini key stays for development.

## Execution log

| Date | Task | What happened | Evidence |
|---|---|---|---|
| | | | |
