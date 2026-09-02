---
baseline_commit: b99e26e64b6cbff42c7418466a8b1a94c2c77032
---

# Story 1.1a: Repo Scaffold, Ports & Module Boundaries

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want a running modular monolith scaffold with ports and import-linter enforcement,
So that subsequent stories build on a clean architecture-compliant foundation.

## Acceptance Criteria

1. **Source tree** follows the architecture's minimal source tree exactly:
   - `src/domain/` with subpackages `profile/`, `engines/`, `messaging/` (pure — no framework imports)
   - `src/adapters/` with subpackages `crm_adapter/` (fixture CRM placeholder), `llm/`, `telegram/`, `clock/`, `config_store/`
   - `src/app/` (FastAPI wiring, DI, webhook endpoint placeholder)
   - `src/worker/` (scheduler entry, outbox dispatcher placeholder, sync-jobs placeholder)
   - `tests/unit/`, `tests/contract/`, `tests/golden/`
2. **Port Protocols are defined in `src/domain`**: `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore` — Python `typing.Protocol` interfaces with docstrings referencing the AD that governs each (AD-2, AD-3, AD-5, AD-6). Method signatures are minimal skeletons documented as evolving with their implementing stories — do NOT invent detailed CRUD signatures.
3. **import-linter forbids framework/adapter imports from `domain/`** and is locally runnable (`lint-imports` exits 0). The CI wiring itself is Story 1.1c — here the contracts must exist and pass.
4. **Module boundary contracts** (AD-11): import-linter also enforces that `domain` subpackages (`profile`, `engines`, `messaging`) do not import each other's internals — cross-module access is via each module's published interface (public `__init__.py` exports / interface modules). `adapters`, `app`, `worker` may import `domain` (ports/entities only).
5. **Dependency versions are pinned** in `pyproject.toml`: Python `3.12+` (requires-python `>=3.12`), FastAPI and aiogram 3 pinned to exact versions, plus dev tooling: ruff, mypy, pytest, pytest-asyncio, import-linter. PostgreSQL 17 and Redis 8 are declared as the target service versions (documented in `pyproject.toml` comments or a `README`/compose-placeholder note; the actual compose file lands in Story 1.1c).
6. **Skeleton runs**: `python -m src.app` (or uvicorn entry) starts a minimal FastAPI app with a root/health route that responds; `python -m src.worker` starts and idles (no external connections required — no DB, no Redis, no Telegram token needed for this story).
7. **Smoke unit tests pass**: `pytest` green, including a test asserting each port is a `Protocol` and importable from `src.domain`, and that `lint-imports` passes from the test or as a documented command.
8. **Naming conventions** (architecture "Consistency Conventions"): Python `snake_case` modules/packages; ports named `XxxPort`; canonical entity names reserved: `Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment` (referenced in port docstrings; entity models themselves land with Story 1.10 / Epic 2).

## Tasks / Subtasks

- [x] Task 1: Project scaffolding (AC: 1, 5, 8)
  - [x] Create `pyproject.toml`: `requires-python = ">=3.12"`; pinned runtime deps `fastapi`, `aiogram` (exact `==` pins, see Dev Notes → Stack versions); dev deps `ruff`, `mypy`, `pytest`, `pytest-asyncio`, `import-linter` (exact or `>=` minor-pinned)
  - [x] Configure `ruff` (line-length, target-version py312, import sorting rules per Effective Dart-equivalent Python conventions) and `mypy` (strict-ish: `disallow_untyped_defs` at least for `src/domain`) in `pyproject.toml`
  - [x] Create the full package tree with empty `__init__.py` files: `src/domain/{profile,engines,messaging}`, `src/adapters/{crm_adapter,llm,telegram,clock,config_store}`, `src/app`, `src/worker`, `tests/{unit,contract,golden}`
  - [x] Add `.gitignore` entries for Python (extend the existing one — do not delete current content)
  - [x] Add a short `README.md` (or extend) documenting: how to install, run app/worker, run tests, run `lint-imports`
- [x] Task 2: Port Protocols in domain (AC: 2, 8)
  - [x] `src/domain/ports.py` (or `src/domain/ports/` package with one module per port) defining the five `typing.Protocol` interfaces: `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore`
  - [x] Each Protocol carries a docstring citing its governing AD and owning module (see Dev Notes → Port guidance)
  - [x] Export all ports from `src/domain/__init__.py` (published interface)
- [x] Task 3: import-linter contracts (AC: 3, 4)
  - [x] Add `.importlinter.toml` (or `[tool.importlinter]` in `pyproject.toml`) with:
    - contract "domain is pure": `forbidden` = `domain` importing `adapters`, `app`, `worker`, `fastapi`, `aiogram`, `redis`, `sqlalchemy`/`psycopg`, `httpx` (external clients), `pydantic` is ALLOWED (Pydantic is the schema-layer convention, not a framework dependency to exclude)
    - contract "module boundaries": `profile`, `engines`, `messaging` mutually independent (each `forbidden` to import the other two's private internals; access only via published interfaces)
  - [x] Verify `lint-imports` passes
- [x] Task 4: Minimal app + worker entry points (AC: 6)
  - [x] `src/app/main.py`: FastAPI app factory with a `GET /health` (and `/`) route returning `{"status": "ok"}`; runnable via `uvicorn` or `python -m src.app`
  - [x] `src/worker/main.py`: async entry loop that starts, logs a startup line, and idles (no DB/Redis/Telegram required); placeholders (functions or TODO comments) for scheduler, outbox dispatcher, sync jobs — they land in later stories
  - [x] No Telegram bot token, DB DSN, or Redis URL is required to run either entry (env-driven config placeholders only)
- [x] Task 5: Tests + verification (AC: 7)
  - [x] `tests/unit/test_ports.py`: each of the five ports is a class, is (or uses) `typing.Protocol`, importable from `src.domain`
  - [x] `tests/unit/test_app.py`: FastAPI app factory produces an app; health route returns 200 (use `httpx`/`fastapi.testclient`)
  - [x] Run: `pytest`, `ruff check .`, `mypy src`, `lint-imports` — all green
- [x] Task 6: Record completion (AC: all)
  - [x] Fill Dev Agent Record (files created, completion notes)

## Dev Notes

### Critical context — what this story is and is NOT

This is the FIRST story in the entire project. The repository is greenfield — no `src/`, no `pyproject.toml` exist today (only `_bmad/`, `_bmad-output/`, `docs/`, `design-artifacts/` planning artifacts and tooling scripts). Do not modify anything outside the new Python project tree and root config files.

**Explicitly OUT of scope** (owned by later stories — do not implement, leave placeholders + `# TODO:` comments only):
- Versioned config store & audit log schemas → **Story 1.1b**
- CI pipeline files, docker compose, health-check-in-compose, image build → **Story 1.1c** (but your `lint-imports`, `ruff`, `mypy`, `pytest` must be runnable locally with single commands so 1.1c just wires them)
- Telegram bot wiring, `/start`, webhook/polling modes → **Story 1.2**
- Any database schema, migrations, Postgres/Redis connections → **Epic 2 / Story 1.1b** (schemas: `crm_mirror`, `profile`, `engines`, `messaging`, `config`, `audit`)
- Fixture CRM, canonical entity models (`Master`, `Client`, …) → **Story 1.10**
- `RenderFacts` / `TriggerCandidate` models, output validator → **Stories 3.4c, 6.3** (may be referenced in docstrings only)

### Architecture compliance (must follow)

- **Paradigm:** hexagonal modular monolith — "pipeline, not agent". One deployable, six modules (`crm_sync`, `profile`, `engines`, `messaging`, `llm`, `config`) + append-only `audit`. No microservices, no message broker, no K8s. [Source: ARCHITECTURE-SPINE.md#Design Paradigm]
- **AD-2 (all externals behind ports):** the domain defines Protocol interfaces — `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore` — implemented by adapters, wired at the edge (FastAPI DI). No external call from the domain layer. `Clock` is injectable everywhere time is read. `LlmPort` is a single port. **This story creates the port definitions; adapters get real implementations in later stories — stub adapter packages here may be empty or contain TODO-only files.**
- **AD-11 (module boundaries):** one deployable; cross-module calls via published interfaces only; one Postgres schema per module + append-only `audit`; import-linter + schema-ownership CI checks. You implement the import-linter half now; the schema-ownership check arrives with 1.1b/1.1c.
- **Naming (Consistency Conventions):** Python `snake_case` modules/tables; ports named `XxxPort`; canonical entities `Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment`. **Pydantic models are the single schema-layer definition** from transport to storage — keep this convention from day one.
- **Source tree is normative** — the spine's "Minimal source tree" section (reproduced in AC-1). Note `crm_sync` is a module name used for ownership/schema discussion; in the source tree its code home is `src/adapters/crm_adapter/` (fixture CRM included) plus sync jobs in `src/worker/`.

### Port guidance (keep signatures skeletal)

Define minimal Protocols with docstrings; later stories extend them:

| Port | Governing ADs | Docstring essence (do not implement) |
|---|---|---|
| `CrmPort` | AD-3, AD-9, AD-12 | Read-only, one-way CRM access; canonical model exposure; freshness via `synced_at`; surrogate IDs assigned at ingestion. Stub method ideas: entity fetch/replay methods — leave as documented TODOs, not full APIs. |
| `LlmPort` | AD-1, AD-2, AD-5 | Single port for all three LLM roles (narrator / structured-output classifier / bounded dialogue partner); provider swap behind the port; never returns figures it wasn't handed. |
| `TelegramPort` | AD-10 | Send-side quiet hours, pacing, inline keyboards are enforced by the dispatcher before this port is called; port is the raw send abstraction. |
| `Clock` | AD-2, AD-8 | Injectable time source (`now()` returning timezone-aware UTC datetimes); all time reads go through it — this is what makes quiet-hours/DST logic testable. |
| `ConfigStore` | AD-6 | Insert-only versioned config + prompt artifacts; read by version at decision time; Pydantic-validated at editing boundary. |

### Stack versions (pin in `pyproject.toml`)

Architecture stack seed (verified 2026-08-16/18, "loose versions pinned at M0" — **this story is M0 pinning time**):

| Component | Version guidance |
|---|---|
| Python | `>=3.12` (3.12+) |
| FastAPI | Pin the exact latest stable you verify locally via `pip index versions fastapi` at implementation time. The spine's 2026-08-18 gate noted 0.141.x current; a September 2026 web check surfaced 0.136.3 — **verify and pin; the architecture requires the pin, not a specific patch**. |
| aiogram | 3.x — current is 3.31.0 ([PyPI](https://pypi.org/project/aiogram/)); pin exact |
| PostgreSQL | 17 (managed Yandex Cloud; declared now, connected in later stories) |
| Redis | 8.x (declared now; used from Story 1.6 onward for dedup/pacing only — never durable state, AD-4) |
| Dev tooling | ruff, mypy, pytest + pytest-asyncio, import-linter (latest stable); promptfoo arrives with Story 6.5 |

### Testing standards

- pytest + pytest-asyncio is the stack (no other test framework — do not introduce one). Test dirs: `tests/unit`, `tests/contract`, `tests/golden` — create all three now even though only `unit` has content.
- Import-linter passing is itself a testable acceptance — document the command (`lint-imports`) in the README so Story 1.1c wires it into CI unchanged.

### Project Structure Notes

- New tree is strictly additive at repo root: `src/`, `tests/`, `pyproject.toml`, `.importlinter.toml`, extended `.gitignore`, `README.md`. Existing `_bmad/`, `_bmad-output/`, `docs/`, `design-artifacts/`, `.claude/`, `.agents/` are untouched.
- No conflicts with the unified structure expected by the architecture — this story IS the reference implementation of the "Minimal source tree" [Source: ARCHITECTURE-SPINE.md#Structural Seed].

### Previous Story Intelligence

None — this is the first story of Epic 1 (and of the project). No prior dev notes, no review feedback, no established code patterns. Git history (5 commits) contains planning documentation only.

### Git Intelligence

Recent commits are documentation-only (`final pre sprint documantation`, `answer from buisness refactor`, `architecture`, `letter last draft`, `initial`). No code conventions established yet — you are establishing them.

### Latest Tech Information

- aiogram 3.31.0 is current on PyPI (September 2026 check).
- FastAPI: verify current stable at implementation time (`pip index versions fastapi`); spine noted 0.141.x at its 2026-08-18 gate. Either way: exact pin required by AC-5.
- Python: 3.12+ per spine; if the dev machine has 3.13 available it is also acceptable (`>=3.12`), but do not require >3.12.

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1a: Repo Scaffold, Ports & Module Boundaries]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md#Design Paradigm]
- [Source: ARCHITECTURE-SPINE.md#AD-2 — All externals behind ports]
- [Source: ARCHITECTURE-SPINE.md#AD-11 — Modular monolith boundaries and the inter-module contracts]
- [Source: ARCHITECTURE-SPINE.md#Consistency Conventions]
- [Source: ARCHITECTURE-SPINE.md#Stack]
- [Source: ARCHITECTURE-SPINE.md#Structural Seed (minimal source tree)]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/SOLUTION-DESIGN.md#3. The shape]
- [Source: SOLUTION-DESIGN.md#6. Testing strategy (three layers)]
- [Source: SOLUTION-DESIGN.md#9. Practical norms]

## Dev Agent Record

### Agent Model Used

GLM 5.2 (via Claude Code CLI)

### Debug Log References

- Verification commands run from repo root (all green, 2026-09-02):
  - `uv run pytest` → 17 passed, 1 warning (starlette TestClient/httpx deprecation inside fastapi 0.141.1 — library-level, not project code; non-blocking)
  - `uv run ruff check .` → All checks passed
  - `uv run mypy src` → Success: no issues found in 23 source files
  - `uv run lint-imports` → Contracts: 2 kept, 0 broken
- Live smoke (AC-6): `uv run python -m src.app` served `GET /health` and `GET /` → 200 `{"status": "ok"}`; `uv run python -m src.worker` logged startup, idled 3s, exited cleanly on SIGINT. No DB/Redis/Telegram env vars set.
- Negative contract test: temporarily injecting `import fastapi` into `src/domain/profile/__init__.py` made `lint-imports` fail with `src.domain.profile -> fastapi` — the purity contract genuinely catches violations (then reverted to green).

### Completion Notes List

- Versions verified and pinned at implementation time (2026-09-02): fastapi 0.141.1, aiogram 3.31.0, uvicorn 0.52.4, pydantic 2.13.5; dev: ruff 0.16.5, mypy 2.3.1, pytest 9.1.1, pytest-asyncio 1.4.0, import-linter 2.14, httpx 0.28.1. PostgreSQL 17 / Redis 8.x declared as comments in `pyproject.toml` (connections land in later stories).
- Ports implemented as `src/domain/ports/` package (one module per port) per the task's "or" option — keeps later stories additive. All five re-exported from `src/domain/__init__.py` (published interface). Signatures kept skeletal per AC-2: only `Clock.now()` is fully specified (tz-aware UTC `datetime`); the other four carry docstrings + TODO markers citing owning stories (1.1b, 1.2, 1.10, Epic 2, Epic 6). Canonical entity names (`Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment`) referenced in `CrmPort` docstrings.
- import-linter config lives in `pyproject.toml` `[tool.importlinter]` (not a separate `.importlinter.toml`). Two contracts: "domain is pure" (forbidden: src.adapters/src.app/src.worker + fastapi/uvicorn/aiogram/redis/sqlalchemy/psycopg/httpx; pydantic allowed) and independence of `profile`/`engines`/`messaging`. Required `include_external_packages = true` for the external forbidden modules. Enforced from the test suite too (`tests/unit/test_import_contracts.py` runs `lint-imports` via subprocess) so Story 1.1c wires CI unchanged.
- Tooling notes: project runs as `src.*` packages from repo root (uv "virtual project", `package = false`); `pythonpath = ["."]` in pytest config; mypy uses `mypy_path = "."` + `explicit_package_bases` for the same reason; `disallow_untyped_defs` enforced for `src.domain.*` via mypy overrides. ruff excludes `_bmad`/`_bmad-output`/`docs`/`design-artifacts` (pre-existing planning tooling — `memlog.py` there fails line-length but is out of story scope).
- Dev environment note: system python is 3.9; used `uv` (0.11.33) which resolved CPython 3.12 — commands in README are `uv run`-prefixed so 1.1c CI just needs uv or a 3.12+ interpreter.

### File List

- pyproject.toml (new — deps, ruff, mypy, pytest, import-linter config)
- README.md (new)
- .gitignore (modified — Python section appended)
- uv.lock (new — generated by `uv sync`)
- src/__init__.py (new)
- src/domain/__init__.py (new — port re-exports, published interface)
- src/domain/ports/__init__.py (new)
- src/domain/ports/crm.py (new — CrmPort)
- src/domain/ports/llm.py (new — LlmPort)
- src/domain/ports/telegram.py (new — TelegramPort)
- src/domain/ports/clock.py (new — Clock)
- src/domain/ports/config_store.py (new — ConfigStore)
- src/domain/profile/__init__.py (new)
- src/domain/engines/__init__.py (new)
- src/domain/messaging/__init__.py (new)
- src/adapters/__init__.py (new)
- src/adapters/crm_adapter/__init__.py (new)
- src/adapters/llm/__init__.py (new)
- src/adapters/telegram/__init__.py (new)
- src/adapters/clock/__init__.py (new)
- src/adapters/config_store/__init__.py (new)
- src/app/__init__.py (new)
- src/app/main.py (new — FastAPI app factory + health routes)
- src/app/__main__.py (new — `python -m src.app` entry)
- src/worker/__init__.py (new)
- src/worker/main.py (new — idle async run loop + placeholders)
- src/worker/__main__.py (new — `python -m src.worker` entry)
- tests/__init__.py (new)
- tests/unit/__init__.py (new)
- tests/contract/__init__.py (new — empty, content lands with Story 1.10)
- tests/golden/__init__.py (new — empty, content lands with Story 6.5)
- tests/unit/test_ports.py (new)
- tests/unit/test_app.py (new)
- tests/unit/test_worker.py (new)
- tests/unit/test_import_contracts.py (new)

## Change Log

- 2026-09-02: Story 1.1a implemented — modular-monolith scaffold, five domain port Protocols, import-linter purity + boundary contracts, FastAPI app and worker skeletons, 17 unit tests. All verification green (pytest / ruff / mypy / lint-imports).
