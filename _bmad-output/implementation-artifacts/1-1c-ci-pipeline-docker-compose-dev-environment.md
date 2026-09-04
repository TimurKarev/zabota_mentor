---
baseline_commit: 854253897ae485a4baa29bfd467038301778fdce
---

# Story 1.1c: CI Pipeline & Docker Compose Dev Environment

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want CI and a runnable dev environment,
so that merges are gated and local development is reproducible.

## Acceptance Criteria

1. **Given** the scaffold from 1.1a and config/audit from 1.1b exist
   **When** CI and dev environment are configured
   **Then** CI runs ruff, mypy, unit tests, import-linter, schema-ownership check

2. **And** docker compose dev environment runs and health check endpoint responds

3. **And** CI blocks merges on any failure

## Tasks / Subtasks

- [x] Task 1: Create `Dockerfile` (AC: #2)
  - [x] 1.1 Multi-stage build: builder stage uses `ghcr.io/astral-sh/uv:<pinned>-python3.12-bookworm-slim`, runtime stage uses `python:3.12-slim-bookworm`
  - [x] 1.2 Builder: copy `pyproject.toml` + `uv.lock` first, run `uv sync --frozen --no-install-project --no-dev` for runtime deps layer, then copy source and `uv sync --frozen --no-dev`
  - [x] 1.3 Runtime: copy `.venv` and app source from builder, set `PATH` to include `.venv/bin`, set `PYTHONPATH=.`
  - [x] 1.4 Default `CMD` runs the app (`python -m src.app`); worker uses an override in compose
  - [x] 1.5 Set `ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never`

- [x] Task 2: Create `.dockerignore` (AC: #2)
  - [x] 2.1 Exclude: `.git`, `.venv`, `__pycache__`, `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.import_linter_cache`, `_bmad`, `_bmad-output`, `docs`, `design-artifacts`, `.DS_Store`, `*.md` (except README.md is not needed in image)

- [x] Task 3: Create `docker-compose.yml` — dev environment (AC: #2)
  - [x] 3.1 Service `postgres`: image `postgres:17-alpine`, healthcheck `pg_isready`, named volume for data, env `POSTGRES_DB=zabota POSTGRES_USER=zabota POSTGRES_PASSWORD=zabota`, port `127.0.0.1:5432:5432`
  - [x] 3.2 Service `redis`: image `redis:8-alpine`, healthcheck `redis-cli ping`, port `127.0.0.1:6379:6379` (forward-looking — not wired until Story 1.6, but included per architecture stack)
  - [x] 3.3 Service `app`: build from Dockerfile, depends_on postgres + redis with `condition: service_healthy`, env `DATABASE_URL`, `TEST_DATABASE_URL`, `APP_HOST=0.0.0.0`, `APP_PORT=8000`, port `8000:8000`, healthcheck hitting `/health`
  - [x] 3.4 Service `worker`: same image as app, command override `python -m src.worker`, depends_on postgres + redis with `condition: service_healthy`, env `DATABASE_URL`
  - [x] 3.5 No `version:` key (obsolete in Compose v2+); start directly with `services:`

- [x] Task 4: Create `.env.example` (AC: #2)
  - [x] 4.1 Document all env vars: `APP_HOST`, `APP_PORT`, `DATABASE_URL`, `TEST_DATABASE_URL`, `REDIS_URL` (future), `BOT_TOKEN` (future, Story 1.2)
  - [x] 4.2 Use placeholder values, not real secrets; add comment that secrets live in Yandex Lockbox in prod (AD-5)

- [x] Task 5: Create `.github/workflows/ci.yml` — CI pipeline (AC: #1, #3)
  - [x] 5.1 Trigger on push to `main` and all pull requests
  - [x] 5.2 `runs-on: self-hosted` (architecture: self-hosted RU runner; GitLab CE fallback noted but not implemented here)
  - [x] 5.3 Step: checkout, install uv via `astral-sh/setup-uv@v6` (pinned version), `uv python install` (respects `requires-python = ">=3.12"`)
  - [x] 5.4 Step: `uv sync --frozen --dev` (install runtime + dev deps from lockfile, fail if lockfile stale)
  - [x] 5.5 Step: `uv run ruff check .` (lint)
  - [x] 5.6 Step: `uv run mypy src` (type check)
  - [x] 5.7 Step: `uv run lint-imports` (import-linter: AD-2 domain purity + AD-11 module boundaries)
  - [x] 5.8 Step: `uv run pytest` (unit + contract + golden tests; includes schema-ownership check via `tests/unit/test_schema_ownership.py` and import-linter guard via `tests/unit/test_import_contracts.py`)
  - [x] 5.9 Step: Spin up Postgres 17 service container (or docker run), set `TEST_DATABASE_URL`, run `uv run pytest` again so DB-backed contract tests execute (not skipped)
  - [x] 5.10 Step: Run migrations against the test DB: `DATABASE_URL=$TEST_DATABASE_URL uv run python -m src.adapters.db.migrate`
  - [x] 5.11 Step: Build Docker image (AC: architecture CI includes image build) — `docker build -t zabota-mentor:ci .`
  - [x] 5.12 Configure branch protection: CI must block merges on any failure (this is a GitHub repo setting — document it in README; the workflow itself fails on any non-zero exit)

- [x] Task 6: Update `.gitignore` (AC: #2)
  - [x] 6.1 Add `.env` to the Python section (secrets must never be committed — AD-5)
  - [x] 6.2 Add `.env.local` if using layered env files
  - [x] 6.3 Keep all existing entries intact (BMad, macOS, editor, Python sections)

- [x] Task 7: Update `README.md` (AC: #2)
  - [x] 7.1 Replace the "CI wiring arrives with Story 1.1c" note with actual CI status
  - [x] 7.2 Add "Docker Compose dev environment" section: `docker compose up -d`, `docker compose ps`, health check at `http://localhost:8000/health`
  - [x] 7.3 Update DB-backed tests section: replace the throwaway `docker run` one-liner with the compose-based `TEST_DATABASE_URL` that compose provides automatically
  - [x] 7.4 Add "CI" section documenting what CI runs and that branch protection blocks merges on failure
  - [x] 7.5 Keep existing sections (Setup, Run, Test & verify, Migrations) intact — only add and update the noted lines

- [x] Task 8: Verify end-to-end (AC: #1, #2, #3)
  - [x] 8.1 `docker compose up -d` — all services reach healthy state
  - [x] 8.2 `curl http://localhost:8000/health` returns `{"status":"ok"}`
  - [x] 8.3 `docker compose down` cleans up
  - [x] 8.4 Local CI simulation: run all 5 gate commands green (`ruff`, `mypy`, `lint-imports`, `pytest` without DB, `pytest` with DB via compose)
  - [x] 8.5 `docker build -t zabota-mentor:ci .` succeeds
  - [x] 8.6 Confirm `src.app` and `src.worker` still start DB-free when run outside compose (regression from 1.1a/1.1b)

### Review Findings

- [x] [Review][Decision] Branch protection on `main` not verifiable from repo — confirmed by Timurkarev: "require status checks" is already enabled. Dismissed.
- [x] [Review][Patch] Add fork-PR guard to CI — `pull_request` trigger with `runs-on: self-hosted` would run fork code (and its Dockerfile) on the persistent RU box; guard the job so same-repo PRs only (resolved from decision: repo is/will be public) [.github/workflows/ci.yml:13-17]
- [x] [Review][Patch] "Tests without DB" step actually runs with DB — `TEST_DATABASE_URL` is set at job level so it leaks into the no-DB pytest step; both pytest steps are identical and the skip path is never exercised in CI (violates Task 5.8/5.9 intent) [.github/workflows/ci.yml:32-33,59-60]
- [x] [Review][Patch] Self-hosted runner hardcodes host port 5432 for the Postgres service — collides with the dev compose Postgres (README instructs running it) or concurrent CI jobs; second bind fails or tests hit a foreign DB [.github/workflows/ci.yml:25-26]
- [x] [Review][Patch] CI interpreter unpinned — bare `uv python install` resolves the newest `>=3.12` (3.13/3.14) while the image and mypy pin 3.12; CI can diverge from what ships [.github/workflows/ci.yml:44-45]
- [x] [Review][Patch] App port published on all interfaces — `"8000:8000"` binds 0.0.0.0, inconsistent with the deliberate 127.0.0.1 posture on Postgres/Redis; exposes dev app to the LAN [docker-compose.yml:51]
- [x] [Review][Patch] Third-party actions pinned to mutable major tags on a self-hosted runner — `actions/checkout@v5`, `astral-sh/setup-uv@v6`; a retargeted tag runs arbitrary code on the persistent runner. Pin to full commit SHAs [.github/workflows/ci.yml:36,39]
- [x] [Review][Patch] `TEST_DATABASE_URL` aliases the persistent dev database — compose sets it on the `app` service pointing at the dev DB (dead weight now, footgun if tests ever run in-container), and `.env.example` points it at the dev DB too instead of a throwaway `zabota_test` [docker-compose.yml:49, .env.example:20]
- [x] [Review][Patch] No `concurrency` group — push + PR double-run the full pipeline; stale runs for superseded commits pile up on the single runner [.github/workflows/ci.yml:10-15]
- [x] [Review][Patch] BuildKit assumed but not enforced — `RUN --mount=type=cache` requires BuildKit and there is no `# syntax=` directive; a legacy-builder daemon fails gate 7 [.github/workflows/ci.yml:71, Dockerfile:21]
- [x] [Review][Patch] CI image accumulates on the runner — every run layers another `zabota-mentor:ci` with no prune; disk fills over time [.github/workflows/ci.yml:71]
- [x] [Review][Patch] No `timeout-minutes` on the job — a hung step holds the self-hosted runner for the 360-min default, blocking queued CI [.github/workflows/ci.yml:15-16]
- [x] [Review][Patch] Worker builds its own image instead of sharing the app's — both services use bare `build: .` with no shared `image:`; two anonymous images, doubled build time, possible drift (deviates from Task 3.4 "same image as app") [docker-compose.yml:39,61]
- [x] [Review][Patch] Postgres flavor skew CI vs dev — `postgres:17` (Debian) in CI vs `postgres:17-alpine` in compose; collation/locale behavior can differ between environments [.github/workflows/ci.yml:20, docker-compose.yml:9]
- [x] [Review][Patch] Container runs as root — no `USER` directive in the runtime stage; any future RCE executes as root inside the container [Dockerfile:32-47]
- [x] [Review][Patch] `sprint-status.yaml` `last_updated` regressed 2026-09-04 → 2026-09-03 — audit-trail timestamp went backwards in this commit [_bmad-output/implementation-artifacts/sprint-status.yaml:2,44]
- [x] [Review][Defer] No restart policy on app/worker in compose — deferred, design choice for a dev environment (crash-looping a dev container is arguably worse than staying down); revisit if compose gains prod-like usage [docker-compose.yml:38-69] — deferred, dev-env design choice (2026-09-04)

## Dev Notes

### Architecture Compliance (MUST follow)

- **AD-2 (Ports):** Domain purity enforced by import-linter in CI. The CI workflow MUST run `uv run lint-imports` as a dedicated step. This is already tested by `tests/unit/test_import_contracts.py` which invokes `lint_imports_command` via `sys.executable` — but CI must also run the console script explicitly.
- **AD-11 (Module boundaries):** Schema-ownership check on migrations enforced by `tests/unit/test_schema_ownership.py` — this runs as part of `uv run pytest`. No separate command needed; the AC lists it separately for visibility but it IS a pytest test. The CI step `uv run pytest` covers it.
- **AD-4 (Outbox):** Redis is dedup/pacing only, never durable state. Redis is NOT wired until Story 1.6+. Including a `redis:8-alpine` service in compose is forward-looking and matches the architecture stack, but the app and worker must NOT connect to Redis in this story.
- **AD-5 (Depersonalization):** Secrets live in Yandex Lockbox in prod. The `.env.example` must use placeholders only — no real secrets. Compose env vars use `${VAR}` interpolation referencing `.env` (gitignored).
- **Stack pinning (M0):** Architecture says "loose versions pinned in pyproject/compose at M0." This story is where compose version pinning happens: `postgres:17-alpine`, `redis:8-alpine`, `python:3.12-slim-bookworm`, `ghcr.io/astral-sh/uv:<pinned>-python3.12-bookworm-slim`.

### Library & Framework Requirements (exact versions — already in pyproject.toml)

| Component | Version | Source |
|-----------|---------|--------|
| Python | >=3.12 | `pyproject.toml:6` |
| FastAPI | 0.141.1 | `pyproject.toml:9` |
| uvicorn | 0.52.4 | `pyproject.toml:10` |
| aiogram | 3.31.0 | `pyproject.toml:11` |
| Pydantic | 2.13.5 | `pyproject.toml:14` |
| psycopg[binary] | 3.3.5 | `pyproject.toml:17` |
| ruff | 0.16.5 | `pyproject.toml:25` |
| mypy | 2.3.1 | `pyproject.toml:26` |
| pytest | 9.1.1 | `pyproject.toml:27` |
| pytest-asyncio | 1.4.0 | `pyproject.toml:28` |
| import-linter | 2.14 | `pyproject.toml:29` |
| httpx | 0.28.1 | `pyproject.toml:31` |
| PostgreSQL | 17 | Architecture stack |
| Redis | 8.x | Architecture stack |
| uv (CI) | pin to latest stable (currently 0.12.x) | `astral-sh/setup-uv` |

**Do NOT change any pyproject.toml dependency versions.** They are pinned and verified. The Dockerfile and CI must use `uv sync --frozen` to respect the lockfile exactly.

### File Structure Requirements

**NEW files to create:**
```
Dockerfile                          # multi-stage build, uv-based
.dockerignore                       # exclude non-image files
docker-compose.yml                  # dev environment: app, worker, postgres, redis
.env.example                        # documented env vars (placeholders only)
.github/workflows/ci.yml            # CI pipeline (5 gates + DB tests + image build)
```

**UPDATE files (read fully before editing):**
```
.gitignore                          # add .env entry (secrets must never be committed)
README.md                           # add compose + CI sections, update "Story 1.1c" notes
```

**DO NOT modify (regression risk):**
```
pyproject.toml                      # deps are pinned — no changes needed
src/app/main.py                     # /health endpoint already works
src/app/__main__.py                 # uvicorn entry already works
src/worker/main.py                  # idle loop already works
src/worker/__main__.py              # entry point already works
src/adapters/db/migrate.py          # migration runner already works
tests/                              # all existing tests must stay green unchanged
migrations/                         # SQL migrations unchanged
```

### Testing Requirements

**CI must run these exact commands (already documented in README.md:45-49):**
1. `uv run ruff check .` — lint
2. `uv run mypy src` — type check (src only, not tests — matches existing convention)
3. `uv run lint-imports` — import-linter architecture contracts
4. `uv run pytest` — unit + contract + golden (without DB, DB tests skip)
5. `uv run pytest` with `TEST_DATABASE_URL` set — DB-backed contract tests run (not skipped)

**Schema-ownership check:** Already implemented as `tests/unit/test_schema_ownership.py` — runs as part of `uv run pytest`. No separate CI step needed, but the AC lists it for visibility. The test parses `migrations/*.sql` and enforces the `SCHEMA_OWNERS` map (AD-11).

**Import-linter:** Runs both as `uv run lint-imports` (CI step) AND as `tests/unit/test_import_contracts.py` (pytest test via subprocess). Both must pass. The pytest version invokes `lint_imports_command` through `sys.executable` to avoid PATH dependency.

**DB-backed tests:** `tests/contract/test_config_store_db.py` skips without `TEST_DATABASE_URL` (lines 22-26). CI MUST set this env var and run a Postgres 17 service so these tests execute. The 1.1b review caught a PG16 deviation — CI must use `postgres:17` exactly.

**Health check endpoint:** Already exists at `/health` returning `{"status":"ok"}` (`src/app/main.py:16-18`). Tested by `tests/unit/test_app.py:20-24`. The compose healthcheck for the `app` service should hit this endpoint.

**Regression guard:** `src.app` and `src.worker` must still start without DB/Redis/Telegram env vars when run outside compose (1.1a/1.1b requirement). The Dockerfile/compose must not break this — the app reads `APP_HOST`/`APP_PORT` with `or` fallback (`src/app/__main__.py:14-15`), and the worker needs no env vars (`src/worker/main.py:21`).

### Previous Story Intelligence

**Story 1.1a (repo scaffold) — done, commit b946792:**
- Stack pinned: Python 3.12+, FastAPI 0.141.1, aiogram 3.31.0, uvicorn 0.52.4, Pydantic 2.13.5, ruff 0.16.5, mypy 2.3.1, pytest 9.1.1, pytest-asyncio 1.4.0, import-linter 2.14, httpx 0.28.1
- `uv` is the package manager (system Python is 3.9; uv resolves CPython 3.12)
- Project runs as `src.*` packages from repo root: `pythonpath=["."]`, `mypy_path="."`, `explicit_package_bases`, `package = false` for uv
- import-linter configured in `pyproject.toml` `[tool.importlinter]` — two contracts: domain purity + module independence
- ruff excludes `_bmad`, `_bmad-output`, `docs`, `design-artifacts`
- `test_import_contracts.py` invokes `lint-imports` via `sys.executable` (no PATH dependency) — CI must do the same or use the console script
- `/health` endpoint returns `{"status":"ok"}`; `test_app.py` parametrized with TestClient fixture
- Worker idles with `asyncio.Event().wait()`, exits on SIGINT

**Story 1.1b (config store + audit) — done, commit 8542538:**
- Added `psycopg[binary]==3.3.5` (bundles libpq, no local pg_config needed)
- DB tests gated on `TEST_DATABASE_URL` — skip without it, unit layer stays green
- DB tests use unique `scope` per test (not TRUNCATE, which is blocked by immutability triggers)
- Migration runner: `python -m src.adapters.db.migrate`, uses `DATABASE_URL`, idempotent, plain SQL, no Alembic
- Schema-ownership check: `tests/unit/test_schema_ownership.py` parses SQL with regex, enforces `SCHEMA_OWNERS` map
- Review caught PG16 deviation — re-ran on `postgres:17` (17.11), 42 passed
- `src.app` and `src.worker` kept DB-free (no wiring in this story)
- README already documents: throwaway Postgres one-liner, `TEST_DATABASE_URL` pattern, migrations section, and notes "(The compose file with a proper dev DB service arrives with Story 1.1c.)"

**Deferred work (from deferred-work.md):**
- Migration runner TOCTOU (no advisory lock) — not relevant for CI (single-threaded runs), but noted if CI ever runs migrations concurrently
- Schema-ownership parser limitations (block comments, quoted identifiers, DROP/ALTER SCHEMA) — no current migration triggers these; improve when needed

### Git Intelligence

Last 2 code commits (HEAD = 8542538):
1. `8542538` — Story 1.1b: Versioned Config Store & Audit Log (done) — 21 files, +1533/-17
2. `b946792` — Story 1.1a: repo scaffold, domain ports, module boundaries (done) — 37 files, +2077/-4

All verification was green at HEAD: pytest 42 passed (with DB), ruff clean, mypy clean, lint-imports 2 contracts kept, app/worker start DB-free.

### Latest Technical Information

**uv in GitHub Actions (verified 2026-09-03):**
- Use `astral-sh/setup-uv@v6` (current stable) — installs uv, caches, optionally pins version
- Pin uv version explicitly (e.g., `version: "0.12.9"` or latest stable at implementation time)
- `uv python install` respects `requires-python` from pyproject.toml
- `uv sync --frozen --dev` installs runtime + dev deps from lockfile; fails if lockfile is stale (good for CI)
- `uv run <cmd>` executes in the project venv, ensuring deps are installed first
- All CI commands should use `uv run` prefix (matches README and existing test conventions)

**Docker multi-stage with uv (verified 2026-09-03):**
- Builder: `ghcr.io/astral-sh/uv:<pinned>-python3.12-bookworm-slim`
- Key env vars: `UV_COMPILE_BYTECODE=1`, `UV_LINK_MODE=copy`, `UV_PYTHON_DOWNLOADS=never`
- Install deps first (copy `pyproject.toml` + `uv.lock` only) for layer caching: `uv sync --frozen --no-install-project --no-dev`
- Then copy source and: `uv sync --frozen --no-dev`
- Runtime: `python:3.12-slim-bookworm`, copy `.venv` and app, set `PATH="/app/.venv/bin:$PATH"` and `PYTHONPATH=.`
- Use `--mount=type=cache,target=/root/.cache/uv` for build caching (if BuildKit available)

**Docker Compose healthchecks (verified 2026-09-03):**
- No `version:` key (obsolete in Compose v2+)
- Use `depends_on` with `condition: service_healthy` (not just start order)
- Postgres healthcheck: `["CMD-SHELL", "pg_isready -U zabota -d zabota"]` with `start_period: 10s`
- Redis healthcheck: `["CMD", "redis-cli", "ping"]` with `start_period: 5s`
- App healthcheck: `["CMD-SHELL", "python -c \"import urllib.request; urllib.request.urlopen('http://localhost:8000/health')\""]` or use `curl`/`wget` if available in slim image
- Bind DB/Redis ports to `127.0.0.1` only (not `0.0.0.0`) for dev security
- Use named volumes for postgres data (survives `compose down`)
- Never put literal passwords in compose — use `${VAR}` with `.env` file (gitignored)

### Project Structure Notes

- The project is a **virtual project** for uv (`package = false` in `pyproject.toml:37`) — it installs deps but not the project itself. The Dockerfile must handle this: `uv sync --no-install-project` is the correct flag.
- Source runs from repo root as `src.*` packages (`pythonpath=["."]`, `mypy_path="."`). The Dockerfile must set `WORKDIR /app` and `PYTHONPATH=.` so `python -m src.app` works.
- `ruff` excludes `_bmad`, `_bmad-output`, `docs`, `design-artifacts` — the `.dockerignore` should also exclude these to keep the image lean.
- The `.gitignore` has Python patterns but does NOT include `.env` — Task 6 adds it (verified: `.gitignore` lines 1-32 have no `.env` entry).

### References

- [Source: epics.md#Story 1.1c] — lines 339-351 (user story + BDD acceptance criteria)
- [Source: ARCHITECTURE-SPINE.md#Stack] — lines 186-201 (technology stack, version pinning at M0)
- [Source: ARCHITECTURE-SPINE.md#AD-2] — line 80 (ports, import-linter enforced in CI)
- [Source: ARCHITECTURE-SPINE.md#AD-11] — lines 132-137 (module boundaries, schema-ownership CI check)
- [Source: ARCHITECTURE-SPINE.md#AD-4] — lines 90-94 (Redis role: dedup/pacing only)
- [Source: ARCHITECTURE-SPINE.md#AD-5] — line 100 (secrets in Yandex Lockbox)
- [Source: SOLUTION-DESIGN.md#Testing strategy] — lines 109-113 (three test layers)
- [Source: SOLUTION-DESIGN.md#CI] — line 139 (trunk-based, self-hosted RU runner, CI gates)
- [Source: pyproject.toml] — lines 1-112 (all deps, tool configs, import-linter contracts)
- [Source: README.md] — lines 45-68 (existing test/verify commands, DB test gating, "Story 1.1c" notes)
- [Source: src/app/main.py] — lines 15-18 (existing /health endpoint)
- [Source: src/app/__main__.py] — lines 14-16 (APP_HOST/APP_PORT env with fallback)
- [Source: tests/unit/test_schema_ownership.py] — lines 1-114 (schema-ownership check implementation)
- [Source: tests/unit/test_import_contracts.py] — lines 1-62 (import-linter guard test)
- [Source: tests/contract/test_config_store_db.py] — lines 22-26 (TEST_DATABASE_URL gating)
- [Source: 1-1a-repo-scaffold-ports-module-boundaries.md] — full file (scaffold patterns, stack pins)
- [Source: 1-1b-versioned-config-store-audit-log.md] — full file (DB test patterns, migration runner, review fixes)
- [Source: deferred-work.md] — full file (deferred items from 1.1b review)

## Dev Agent Record

### Agent Model Used

claude-5-sonnet (Claude Code CLI, glm-5.2)

### Debug Log References

- `uv run ruff check .` — All checks passed
- `uv run mypy src` — Success: no issues found in 29 source files
- `uv run lint-imports` — Contracts: 2 kept, 0 broken
- `uv run pytest` (no DB) — 35 passed, 7 skipped (DB-backed skip as designed)
- `TEST_DATABASE_URL=… uv run pytest` (compose Postgres 17) — 42 passed, 1 warning
- `docker compose up -d --build` — app/postgres/redis (healthy), worker up
- `curl http://localhost:8000/health` → `{"status":"ok"}`
- `docker compose down` — clean teardown
- `docker build -t zabota-mentor:ci .` — built; runtime deps import OK in-container
- `python -m src.app` / `python -m src.worker` outside compose — start DB-free (1.1a/1.1b regression guard)
- ghcr.io/astral-sh/uv tag audit (paginated registry API, 7544 tags): composite
  `<version>-python3.12-bookworm-slim` tags discontinued after 0.9.30; `0.12.9`
  exists only as the plain (distroless) image

### Completion Notes List

- **Deviation from subtask 1.1 (documented):** the literal builder image
  `ghcr.io/astral-sh/uv:<pinned>-python3.12-bookworm-slim` no longer exists for
  current uv — Astral stopped publishing composite variant tags after 0.9.30
  (verified against the ghcr registry API on 2026-09-03). Used the equivalent
  officially supported pattern: `FROM python:3.12-slim-bookworm` +
  `COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /uvx /usr/local/bin/`. Pin
  (uv 0.12.9 = latest stable from PyPI) and base-image intent are preserved.
- uv version pinned to 0.12.9 in BOTH the Dockerfile and `setup-uv` CI step.
- Compose credentials default to throwaway dev values (`zabota`/`zabota`) via
  `${VAR:-default}` interpolation — works with zero config, overridable from a
  gitignored `.env` (AD-5); Postgres/Redis ports bound to 127.0.0.1 only.
- `.dockerignore` additionally excludes `.env` (not in the task list, but AD-5:
  secrets must never enter an image) — belt-and-braces since only `src/`,
  `migrations/`, `pyproject.toml`, `uv.lock` are COPYed anyway.
- CI includes a `postgres:17` service (exact major per the 1.1b review
  finding), runs pytest twice (no-DB skips, with-DB executes), then the
  migration runner as a smoke check, then `docker build`.
- Branch protection (AC #3): the workflow fails on any non-zero exit; the
  actual GitHub repo setting (require status checks on `main`) is a manual
  admin action — documented in README "CI" section per subtask 5.12.
- No new dependencies; pyproject.toml, src/, tests/, migrations/ untouched.

### File List

- `.dockerignore` (new)
- `.env.example` (new)
- `.github/workflows/ci.yml` (new)
- `.gitignore` (modified — added `.env`, `.env.local` secrets section)
- `Dockerfile` (new)
- `docker-compose.yml` (new)
- `README.md` (modified — compose dev-environment section, compose-based DB
  tests, CI section; replaced "arrives with Story 1.1c" notes)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (status updates)
- `_bmad-output/implementation-artifacts/deferred-work.md` (appended: worker SIGTERM
  graceful-shutdown deferral, observed during user verification)

## Change Log

- 2026-09-03: Story implemented — Dockerfile (multi-stage uv build),
  .dockerignore, docker-compose.yml (postgres 17 / redis 8 / app / worker),
  .env.example, CI workflow (5 gates + DB tests + migrations + image build),
  .gitignore + README updates. All AC verified end-to-end locally.
- 2026-09-04: Code review patches (15 applied) — CI: TEST_DATABASE_URL moved
  from job-level to the with-DB step (skip path now actually exercised),
  Postgres service host port 15432 (collision-free), Python pinned to 3.12,
  actions pinned to commit SHAs, fork-PR guard, concurrency group,
  timeout-minutes, DOCKER_BUILDKIT=1, post-build image prune, step-name YAML
  bug fixed (pre-existing). Compose: app port 127.0.0.1-only, TEST_DATABASE_URL
  removed from app service, shared `zabota-mentor:dev` image for app+worker,
  `scripts/create-test-db.sh` creates throwaway `zabota_test` DB. Dockerfile:
  non-root `appuser`. .env.example/README: TEST_DATABASE_URL points at
  `zabota_test`, not the persistent dev DB. sprint-status `last_updated`
  regression corrected. Local verify: `uv run pytest` → 35 passed, 7 skipped;
  `docker compose config` OK.
