---
baseline_commit: b946792cea64914f5011cdc5978eabeeba372b19
---

# Story 1.1b: Versioned Config Store & Audit Log

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want an insert-only versioned config store and an append-only audit log,
So that every behavioral parameter is reproducible and every decision is traceable.

## Acceptance Criteria

1. **Insert-only versioned config store** is implemented behind the `ConfigStore` port (AD-6, AD-2):
   - The `ConfigStore` Protocol in `src/domain/ports/config_store.py` evolves from its 1.1a skeleton into real method signatures (see Dev Notes → ConfigStore port contract); the `# TODO (Story 1.1b)` marker is removed and the adapter home `src/adapters/config_store/` gets the real implementation.
   - Config rows live in the Postgres `config` schema in the AD-6 shape: `(version, params JSONB, author, created_at, valid_from)` — plus `kind` (discriminates `params` vs future `prompt` artifacts, Story 6.1) and `scope` (default `'global'`; per-salon owner settings arrive with Story 3.0).
   - Rows are **immutable after insert**: the store API exposes no update/delete methods, AND the database enforces it (permissions and/or trigger guard rejecting `UPDATE`/`DELETE` on `config.config_version`).
   - Every edit creates a **new versioned row**; activating a prior version is itself a new row (AD-6: no UPDATE-based rollback) — this is what makes config rollback an insert, satisfying the < 5 min rollback requirement (FR-14.1) mechanically.
   - Params are **Pydantic-validated at the editing boundary** before insert (see Dev Notes → Validation at the editing boundary).
   - Version resolution: the active version at decision time = the row with the greatest `valid_from <= now` for its (`kind`, `scope`); readers fetch **by version** at decision time so compute and send never span versions (AD-6).
2. **Append-only audit log schema** exists in the `audit` schema (AD-11, FR-14.2):
   - `audit.event` rows carry **justification (NOT NULL) + inputs (JSONB)** plus: `occurred_at` (timestamptz, UTC — AD-8), `event_type`, `actor`, `subject` (JSONB identifying what the event is about), and nullable `salon_id` (AD-7 salon key where the event is salon-scoped; global events like config changes are null).
   - Append-only is enforced at the database level (`UPDATE`/`DELETE` rejected), not just by convention.
   - An audit-writer component (see Dev Notes → Where the audit writer lives) records config inserts and activations as audit events — the first real users of the log; the full event catalogue (consent, egress, validator failures, erasure, sync runs) lands with its owning stories.
3. **Audit integration with config**: every config insert (new version) and every activation writes an audit event with justification + inputs (which version, which params hash/snapshot reference, who, why). The audit write is testable and tested.
4. **Schema-ownership CI check** enforces no cross-module table access (AD-11): a test-time check parses the SQL migrations and validates every schema/object against a schema→owner map; creating or altering objects outside a migration's declared ownership fails the check. It runs locally as part of `pytest` (CI wiring itself is Story 1.1c).
5. **Verification green**: `uv run pytest`, `uv run ruff check .`, `uv run mypy src`, `uv run lint-imports` all pass. DB-backed tests are env-gated (see Dev Notes → Testing without compose) and all run green when `TEST_DATABASE_URL` points at a PostgreSQL 17 instance. Domain purity is preserved: `psycopg` (and any DB code) appears only in `src/adapters/` — never in `src/domain/` (the existing import-linter forbidden list already names `psycopg`, and the 1.1a guard test keeps that list synced with runtime deps — both must stay green).

## Tasks / Subtasks

- [x] Task 1: Add the DB driver dependency (AC: 5)
  - [x] Add `psycopg[binary]` to `[project] dependencies` in `pyproject.toml` with an exact `==` pin (verify current at implementation time via `pip index versions psycopg` — 3.3.x line, see Dev Notes → Latest tech)
  - [x] Confirm the 1.1a guard test (forbidden-modules list ↔ runtime deps) stays green — `psycopg` is already in the import-linter forbidden list, so no config change should be needed
- [x] Task 2: Migrations — `config` and `audit` schemas (AC: 1, 2, 4)
  - [x] Create `migrations/` at repo root with versioned plain-SQL files (naming: `NNNN_description.sql`, starting `0001_config_and_audit_schemas.sql`) — no Alembic (see Dev Notes → Why plain SQL migrations)
  - [x] `0001` creates: schema `config`; table `config.config_version` (AD-6 columns + `kind` + `scope`, unique `(kind, scope, version)`, index on `(kind, scope, valid_from)`); schema `audit`; table `audit.event` (columns per AC-2); a `schema_migrations` bookkeeping table
  - [x] Enforce immutability in DDL: `REVOKE UPDATE, DELETE ON config.config_version FROM app role` and/or a BEFORE UPDATE/DELETE trigger raising an exception (belt-and-braces: trigger survives superuser/migration roles); same treatment for `audit.event`
  - [x] Implement a minimal idempotent migration runner (Python, lives in `src/adapters/config_store/` or a small `src/adapters/db/` helper — runner applies pending `migrations/*.sql` in order inside transactions, records them in `schema_migrations`; runnable as a module entry `python -m …` and importable from tests)
  - [x] Optionally seed `config.config_version` v1 (`kind='params'`, `scope='global'`, `params={}` baseline, `valid_from=now()`) so later stories always resolve an active version — keep it truly empty of behavioral values
- [x] Task 3: `ConfigStore` port contract (AC: 1)
  - [x] Replace the 1.1a TODO skeleton in `src/domain/ports/config_store.py` with real method signatures per Dev Notes → ConfigStore port contract; docstrings keep citing AD-6; fully typed (mypy strict applies to `src.domain.*`)
  - [x] Define the Pydantic result model(s) the port returns (e.g., `ConfigVersion` with `version`, `kind`, `scope`, `params`, `author`, `created_at`, `valid_from`) — Pydantic is allowed in domain (schema-layer convention)
- [x] Task 4: Config store implementation + audit writer (AC: 1, 2, 3)
  - [x] `src/adapters/config_store/`: implement the port over psycopg — `insert` (validate → insert row → write audit event), `get(version)`, `active(as_of)` (greatest `valid_from <= as_of`), `activate(prior_version, author, justification)` (insert a NEW row copying the prior version's params with a fresh `valid_from`, audited)
  - [x] `src/adapters/audit/`: audit-writer class (see Dev Notes → Where the audit writer lives) — one method: append an event (`event_type`, `actor`, `subject`, `inputs`, `justification`, optional `salon_id`); justification is required (NOT NULL both in schema and in the writer's signature)
  - [x] Pydantic validation at the editing boundary: an insert-payload model (author non-empty, justification non-empty, `valid_from` timezone-aware, params is a JSON object) plus a registry hook mapping `kind` → typed params model, so owning stories register their typed schemas later without touching the store
  - [x] No new domain port for audit in this story (see Dev Notes); the writer is consumed from adapter/edge code only
- [x] Task 5: Schema-ownership check (AC: 4)
  - [x] `tests/unit/test_schema_ownership.py`: maintain a schema→owner map (`config` → `src.adapters.config_store`, `audit` → cross-cutting `src.adapters.audit`); parse `migrations/*.sql` (schema-qualified `CREATE/ALTER` statements) and fail if a migration touches a schema/object it does not own or creates an undeclared schema. Pattern follows the 1.1a `test_import_contracts.py` approach (a real check, runnable locally, wired into CI unchanged by 1.1c)
- [x] Task 6: Tests (AC: 1–5)
  - [x] Unit (always run): editing-boundary Pydantic validation (rejects empty author/justification, naive datetime, non-object params); active-version resolution logic; schema-ownership check; migration files parse and are ordered
  - [x] DB-backed (gated on `TEST_DATABASE_URL`, skip with an explanatory message otherwise): insert → read back by version; UPDATE/DELETE on `config.config_version` and `audit.event` raise; activation-of-prior-version produces a new row and moves `active()`; audit rows carry justification + inputs; migration runner is idempotent (re-run applies nothing)
  - [x] Extend `README.md`: how to run a throwaway Postgres 17 (`docker run --rm -e POSTGRES_PASSWORD=… -p 5432:5432 postgres:17`) and set `TEST_DATABASE_URL` — the compose file arrives in Story 1.1c
- [x] Task 7: Record completion (AC: all)
  - [x] Fill Dev Agent Record (files created, completion notes, verification output)

## Dev Notes

### Critical context — what exists today (READ before coding)

The scaffold from Story 1.1a exists and is verified green (pytest 18 passed / ruff / mypy / lint-imports, 2026-09-02). Files this story touches:

- `src/domain/ports/config_store.py` — currently a skeletal Protocol with `# TODO (Story 1.1b)`. **Current state:** docstring-only, no methods. **This story replaces the TODO with the real contract** (Task 3). **Preserve:** the AD-6 docstring citation and the convention that ports live in `src/domain/ports/` and re-export from `src/domain/__init__.py` (the 1.1a port tests assert importability from `src.domain` — keep them passing; extend, don't rewrite).
- `src/adapters/config_store/__init__.py` — TODO-only docstring; becomes the real implementation home.
- `pyproject.toml` — dependency pins, ruff (line-length 100, py312), mypy (`disallow_untyped_defs` for `src.domain.*`), pytest config (`pythonpath=["."]`, `asyncio_mode="auto"`), import-linter contracts (domain purity forbids `psycopg` already; module independence). **Do not loosen any of these.**
- `src/app/main.py`, `src/worker/main.py` — must keep starting with no DB required (no env vars needed). **This story adds NO wiring into app/worker** — the store is a library + tests until later stories consume it. Regression check: `python -m src.app` and `python -m src.worker` still start with nothing set.

Project runs via `uv` (`uv run pytest` etc., system python is 3.9 — never call bare `python`/`pytest` in docs or verification).

### Architecture compliance (must follow)

- **AD-6 (insert-only versioned config + prompts):** immutable rows `(version, params JSONB, author, created_at, valid_from)`; Pydantic-validated at the editing boundary; activation of a prior version is a new row; every outbound message later stores `(config_version, prompt_version)`; config changes are audit events. This story builds the substrate — engines read config **by version at decision time**; the `active(as_of)` resolution must never be cached across a decision.
- **AD-11 (module boundaries):** one Postgres schema per module + append-only `audit`. This story creates ONLY the `config` and `audit` schemas — `crm_mirror`, `profile`, `engines`, `messaging` land with their owning stories (2.3 et al.). Cross-module table access is forbidden; the schema-ownership check (Task 5) is the migrations-side enforcement that pairs with import-linter.
- **AD-2 (externals behind ports):** Postgres access is adapter-side only. The domain sees `ConfigStore`; `psycopg` must never appear in `src/domain/`. Pydantic IS allowed in domain (schema-layer convention — port result models belong there).
- **AD-8 (time):** all timestamps `timestamptz`, stored UTC. `valid_from` and `occurred_at` are tz-aware; the editing boundary rejects naive datetimes. The `Clock` port exists for domain time reads; adapter/DB code may use DB `now()` (UTC).
- **AD-7 (tenancy):** salon key on domain rows — `audit.event.salon_id` nullable (config events are global; salon-scoped audit events start with Story 1.3 consent capture).
- **FR-14.1/14.2 (config & audit):** insert-only versioning, changeable without release, rollback < 5 min (mechanically: rollback = insert an activation row — document this in the store's docstring); every significant decision audited with justification and inputs.

### ConfigStore port contract (keep it this small)

```python
class ConfigStore(Protocol):
    def insert(self, params: Mapping[str, Any], *, author: str, justification: str,
               valid_from: datetime, kind: str = "params", scope: str = "global") -> ConfigVersion: ...
    def get(self, version: int, *, kind: str = "params", scope: str = "global") -> ConfigVersion | None: ...
    def active(self, as_of: datetime, *, kind: str = "params", scope: str = "global") -> ConfigVersion | None: ...
    def activate(self, prior_version: int, *, author: str, justification: str,
                 valid_from: datetime, kind: str = "params", scope: str = "global") -> ConfigVersion: ...
```

(Sync or async signatures are both acceptable — pick ONE and be consistent; the adapter is the only implementation so far. `activate` = insert-new-row-with-prior-params, per AD-6.)

### Validation at the editing boundary

The AC's "Pydantic-validated" has two layers — implement both, invent neither's future:
1. **Structural (now):** an insert-payload Pydantic model enforcing non-empty author/justification, tz-aware `valid_from`, `params` as a JSON object, known `kind`. This is the editing boundary.
2. **Typed per-kind params (extension point):** a registry `kind -> type[BaseModel]`; when a later story registers e.g. `SmoothingAlphaParams`, inserts of that kind validate against it. Register nothing yet — behavioral parameter schemas (α, corridors, quiet hours…) land with their owning stories; the full seed set is Story 7.5b. **Do NOT invent behavioral config values in this story.**

### Where the audit writer lives (structural decision)

`src/adapters/audit/` — a small class, no domain port in this story. Rationale: AD-2 names exactly five ports; audit writes in this story come from the config adapter (edge-side). When domain modules need to emit audit events (Story 1.3 consent, Story 1.5 profile changes), THAT story decides how (e.g., an audit port or a durable-record-first pattern per the Mutation convention) — do not pre-build that coupling now.

### Why plain SQL migrations (no Alembic)

The architecture mandates no migration tool and only 6 schemas total; a directory of ordered, transactional SQL files + a ~50-line idempotent runner is fully auditable, parseable by the schema-ownership check, and avoids a new dependency + its config surface. If migration complexity ever grows, Alembic can be adopted then (it can wrap these files). Keep the runner dead simple: ordered apply, `schema_migrations` bookkeeping, no down-migrations (schema changes in this project are additive; AD-6 insert-only culture applies to structure too where practical).

### Testing without compose (docker compose is Story 1.1c)

- DB-backed tests are gated: no `TEST_DATABASE_URL` → skip with a visible reason; CI provides the service from 1.1c. `pytest` must stay fully green without Docker for the unit layer.
- README documents the one-liner throwaway Postgres 17.
- Immutability AC is proven at the DB level (trigger/permission rejects UPDATE/DELETE) in the gated tests, and structurally (no mutating methods on the store) everywhere.

### Library / framework requirements

| Component | Requirement |
|---|---|
| `psycopg[binary]` | Exact `==` pin, 3.3.x line current (3.3.5 per Sept 2026 check — verify via `pip index versions psycopg` and pin what you install). Python ≥3.10 required — fine on 3.12. |
| Pydantic 2.13.5 | Already pinned (1.1a) — use for port result models + editing-boundary validation. JSONB round-trips through the same models (schema-layer convention). |
| PostgreSQL 17 | Target service; DDL uses JSONB + timestamptz (no PG-only exotic features beyond these). |
| No new deps otherwise | No Alembic, no SQLAlchemy, no testcontainers (env-gating replaces them). |

### Previous Story Intelligence (from 1.1a — apply all of it)

- Commands are `uv run`-prefixed (system python is 3.9; uv resolves 3.12).
- mypy is strict for `src.domain.*` — new port signatures must be fully typed; `ConfigVersion | None` returns need `if` handling, no assertions.
- Existing tests to keep green: `tests/unit/test_ports.py` (asserts port Protocols importable from `src.domain` — extend for the evolved `ConfigStore`, don't break), `test_import_contracts.py` (runs lint-imports via `sys.executable`; guard test syncs forbidden list ↔ runtime deps), `test_app.py`, `test_worker.py`.
- Naming conventions established: modules `snake_case`; ports `XxxPort`; adapters live in `src/adapters/<name>/`; config files in `pyproject.toml` sections (not separate dotfiles) where 1.1a chose that.
- ruff excludes planning dirs; line-length 100.

### Git Intelligence

HEAD = `b946792` (Story 1.1a, done). Working tree clean. Only one code commit exists — the patterns in it ARE the project conventions (see Previous Story Intelligence). Commit messages follow `Story X.Yz: title (status)` with a detailed body.

### Latest Tech Information

- **psycopg 3.3.5** is current on the 3.3.x line (May 2026 release; supports Python 3.10–3.14). Use `psycopg[binary]` to avoid needing libpq/pg_config locally. Sources: [PyPI – psycopg](https://pypi.org/project/psycopg/), [psycopg release notes](https://psycopg.org/psycopg3/docs/news.html).
- PostgreSQL 17 JSONB + timestamptz semantics are stable; nothing version-sensitive in this story's DDL.

### Project Structure Notes

- New at repo root: `migrations/` (SQL files). New packages: `src/adapters/audit/`. Modified: `src/domain/ports/config_store.py`, `src/adapters/config_store/__init__.py`, `pyproject.toml` (dep pin), `README.md`, `tests/unit/…`. Nothing under `_bmad/`, `_bmad-output/`, `docs/`, `design-artifacts/` is touched.
- No conflicts with the architecture's minimal source tree — `migrations/` is standard monolith territory; the schema-ownership check makes it a governed one.

### Explicitly OUT of scope (leave TODOs/extension points only)

- Behavioral config values (quiet hours, caps, α, bar corridor, hysteresis thresholds…) — owning stories; full seed set Story 7.5b
- Prompt artifact content/versioning mechanics — Story 6.1 (only the `kind` discriminator column anticipates it)
- Per-salon/per-owner config scopes (`scope` column exists; salon-scoped owner settings — Story 3.0)
- CI pipeline wiring, docker compose, DB service in CI, healthcheck-in-compose — Story 1.1c
- Other module schemas (`profile`, `engines`, `messaging`, `crm_mirror`) — Story 2.3+
- Wiring the store into `src/app` / `src/worker` runtime DI — first consumer arrives with Story 1.6 (scheduler reads config); both entry points must keep starting DB-free
- Audit events other than config insert/activate; any domain-layer audit coupling — owning stories

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 1.1b: Versioned Config Store & Audit Log]
- [Source: _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md#AD-6 — Insert-only versioned config and prompts]
- [Source: ARCHITECTURE-SPINE.md#AD-11 — Modular monolith boundaries and the inter-module contracts]
- [Source: ARCHITECTURE-SPINE.md#AD-2 — All externals behind ports]
- [Source: ARCHITECTURE-SPINE.md#AD-8 — UTC in the DB, dual local time at the decision point]
- [Source: ARCHITECTURE-SPINE.md#Consistency Conventions] (Mutation: no side effect without a durable record first; Pydantic single schema layer)
- [Source: _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/SOLUTION-DESIGN.md#6. Testing strategy / practical norms] (config changes are code-like: reviewed, Pydantic-validated, instantly rollable)
- [Source: _bmad-output/implementation-artifacts/1-1a-repo-scaffold-ports-module-boundaries.md] (previous story intelligence, verification commands, file inventory)

## Dev Agent Record

### Agent Model Used

Claude Code (VSCode extension), model glm-5.2, 2026-09-03.

### Debug Log References

- `uv run pytest` (no DB env): 35 passed, 7 skipped (DB-gated skip with reason) — 2026-09-03
- `TEST_DATABASE_URL=postgresql://postgres:test@127.0.0.1:55432/zabota uv run pytest`
  against a throwaway `postgres:17` Docker container (PG 17.11 on aarch64, port 55432,
  removed after): **42 passed, 0 failed** — 2026-09-04. AC-5 deviation closed: DB tests now
  verified on PostgreSQL 17 as required by the spec.
- `uv run ruff check .`: All checks passed — 2026-09-04
- `uv run mypy src`: Success: no issues found in 29 source files — 2026-09-04
- `uv run lint-imports`: Contracts: 2 kept, 0 broken — 2026-09-04
- Regression: `uv run python -m src.app` serves `/health` -> `{"status":"ok"}` with no DB env;
  `test_worker.py` green — both entry points still start DB-free — 2026-09-04
- `DATABASE_URL=postgresql://postgres:test@127.0.0.1:55432/zabota uv run python -m src.adapters.db.migrate`
  -> "No pending migrations." (idempotent) — 2026-09-04

Issues hit and fixed during dev:
- 1.1a guard test failed on the new dep: it parsed `psycopg[binary]==3.3.5` without stripping
  the PEP 508 extras — fixed the name normalization in the test (forbidden list unchanged).
- Schema-ownership parser v1 missed `CREATE SCHEMA` (unqualified names) and INDEX/TRIGGER
  `ON` targets — rewritten with keyword-anchored regexes + self-check tests.
- DB immutability tests: the first expected UPDATE failure aborted the psycopg implicit
  transaction — each probe now runs in its own `conn.transaction()` savepoint.

### Completion Notes List

- **AC-1 (insert-only store):** `ConfigStore` port evolved to the full 4-method contract
  (insert/get/active/activate — sync psycopg style, consistent) with `ConfigVersion`
  Pydantic result model in `src/domain/ports/config_store.py`; TODO marker removed.
  `PostgresConfigStore` implements it; no update/delete methods anywhere, and migration
  0001 enforces immutability with BEFORE UPDATE/DELETE triggers (belt-and-braces: triggers
  survive any role). Activation of a prior version = new row with fresh `valid_from`
  (rollback = insert). Active resolution = greatest `valid_from <= as_of` with version
  tiebreak, in a pure helper (`resolution.py`) shared by prod and unit tests.
- **AC-2 (audit log):** `audit.event` with justification NOT NULL + inputs JSONB,
  occurred_at timestamptz UTC, event_type, actor, subject JSONB, nullable salon_id (AD-7);
  append-only via DB trigger. `AuditWriter` in `src/adapters/audit/` — one `append` method,
  justification required in the signature; no domain port (deliberate, per Dev Notes).
- **AC-3 (audit integration):** every insert -> `config.insert`, every activation ->
  `config.activate` audit event (actor, subject incl. version/prior_version, params in
  inputs, justification). Tested both unit-side (shape) and DB-side (rows written).
- **AC-4 (schema-ownership check):** `tests/unit/test_schema_ownership.py` — schema->owner
  map (config -> src.adapters.config_store, audit -> src.adapters.audit, public ->
  src.adapters.db bookkeeping), keyword-anchored SQL parsing, fails on undeclared schemas
  both directions; migration ordering check included. Runs in plain `pytest`.
- **AC-5 (verification green):** all four commands pass (see Debug Log). DB tests gated on
  `TEST_DATABASE_URL`, skip with explanatory message otherwise; ran fully green against a
  throwaway `postgres:17` Docker container (PG 17.11, 2026-09-04) — AC-5 deviation from the
  initial PG 16 run is now closed. Domain purity kept: psycopg appears only in
  src/adapters/**; import-linter + the 1.1a guard test both green.
- Editing boundary: structural `ConfigInsertPayload` (non-empty author/justification/kind/
  scope, tz-aware valid_from per AD-8, params as JSON object) + `KIND_PARAMS_MODELS`
  registry extension point; only `params` registered (structural-only). No behavioral
  values invented.
- Migration 0001 seeds global params v1 with empty `{}` (system author) so `active()`
  always resolves for later stories.
- Out of scope respected: no wiring into src.app/src.worker (both still start DB-free),
  no new domain port for audit, no CI/compose changes (1.1c).

### File List

- migrations/0001_config_and_audit_schemas.sql (new)
- pyproject.toml (modified: psycopg[binary]==3.3.5 pin)
- README.md (modified: DB-test gating + throwaway Postgres 17 one-liner, migrations section)
- src/domain/ports/config_store.py (modified: TODO -> real contract + ConfigVersion)
- src/domain/__init__.py (modified: export ConfigVersion)
- src/adapters/config_store/__init__.py (modified: TODO -> package exports)
- src/adapters/config_store/models.py (new)
- src/adapters/config_store/resolution.py (new)
- src/adapters/config_store/store.py (new)
- src/adapters/audit/__init__.py (new)
- src/adapters/db/__init__.py (new)
- src/adapters/db/migrate.py (new)
- tests/unit/test_config_store_models.py (new)
- tests/unit/test_schema_ownership.py (new)
- tests/unit/test_ports.py (modified: ConfigStore full-contract test)
- tests/unit/test_import_contracts.py (modified: PEP 508 extras stripping in guard test)
- tests/contract/test_config_store_db.py (new)
- uv.lock (modified: lockfile for the new dep)

## Change Log

- 2026-09-03: Story created — ultimate context engine analysis completed; comprehensive developer guide created from epics, architecture spine, Story 1.1a intelligence, and current scaffold code.
- 2026-09-03: Implementation complete — config + audit schemas (migration 0001 + idempotent runner), ConfigStore port contract + PostgresConfigStore, AuditWriter, editing-boundary validation with kind registry, schema-ownership check, 24 new tests (17 unit + 7 DB-gated). All verification commands green. Status -> review.
- 2026-09-03: Code review complete — 3 parallel adversarial layers (Blind Hunter, Edge Case Hunter, Acceptance Auditor). 2 decision-needed, 13 patch, 8 deferred, 2 dismissed.
- 2026-09-03: Review patches applied — 14 code fixes (advisory lock for version race, TRUNCATE triggers, frozen ConfigVersion, lowercase kind/scope normalization, validate_params in activate, tz-aware as_of guard, AuditEvent justification validator, valid_from:datetime, activate validation order, register_kind validation, AuditWriter docstring, unused argv removed, seed valid_from fixed). Verification green: pytest 35 passed/7 skipped, ruff, mypy, lint-imports. Status -> in-progress (PG 17 re-run pending).
- 2026-09-04: AC-5 deviation closed — DB-backed tests re-run against a throwaway `postgres:17` Docker container (PG 17.11): 42 passed, 0 failed. Full verification sweep re-run green (pytest 42 passed, ruff, mypy 29 files clean, lint-imports 2/2, app/worker DB-free regression, migration runner idempotent). Status -> done.

### Review Findings

- [x] [Review][Decision→Patch] AC-5 deviation: DB tests verified on PostgreSQL 16, not PostgreSQL 17 — RESOLVED 2026-09-04: re-ran `TEST_DATABASE_URL=… uv run pytest` against a `postgres:17` Docker container (PG 17.11): 42 passed, 0 failed. Dev Agent Record updated; status -> done.
- [x] [Review][Decision→Patch] Kind/scope case normalization — RESOLVED: normalize to lowercase at the editing boundary. Add a Pydantic validator to ConfigInsertPayload that lowercases kind and scope before insert/activate. Update validate_params and the registry to use lowercase keys consistently.
- [x] [Review][Patch] Concurrent version allocation race (MAX+1 without locking) [src/adapters/config_store/store.py:148-160] — medium. Fixed: added pg_advisory_xact_lock(hashtext(kind:scope)) inside the insert transaction to serialize concurrent inserts for the same group.
- [x] [Review][Patch] test_seeded_global_params_v1_is_active is a time-bomb [tests/contract/test_config_store_db.py:28,179-184] — high. Fixed: migration seed now uses a fixed valid_from of '1970-01-01T00:00:00+00:00' instead of now(), so the seed is always eligible regardless of when migrations are applied.
- [x] [Review][Patch] activate() bypasses validate_params [src/adapters/config_store/store.py:110-128] — low. Fixed: activate() now calls validate_params(prior.kind, prior.params) before _insert_row.
- [x] [Review][Patch] ConfigVersion is mutable (no frozen=True) [src/domain/ports/config_store.py:22-36] — low. Fixed: added model_config = ConfigDict(frozen=True) to ConfigVersion.
- [x] [Review][Patch] AuditWriter from a different connection breaks atomicity [src/adapters/config_store/store.py:33-35] — low. Fixed: documented the same-connection constraint in the PostgresConfigStore docstring.
- [x] [Review][Patch] valid_from typed as Any in ConfigInsertPayload [src/adapters/config_store/models.py:26,38-44] — low. Fixed: changed valid_from to datetime type with a proper tz-awareness validator.
- [x] [Review][Patch] resolve_active / active() accept timezone-naive as_of and crash [src/adapters/config_store/resolution.py:19, src/adapters/config_store/store.py:78-87] — low. Fixed: added tz-awareness guard in resolve_active that raises ValueError for naive as_of.
- [x] [Review][Patch] TRUNCATE bypasses immutability trigger [migrations/0001_config_and_audit_schemas.sql:50-52,78-80] — low. Fixed: added BEFORE TRUNCATE FOR EACH STATEMENT triggers on both config.config_version and audit.event.
- [x] [Review][Patch] AuditEvent accepts empty/whitespace justification [src/adapters/audit/__init__.py:20-30] — low. Fixed: added _non_empty field_validator to AuditEvent.justification.
- [x] [Review][Patch] register_kind accepts empty/whitespace kind strings [src/adapters/config_store/models.py:59-65] — low. Fixed: added non-empty check and lowercase normalization in register_kind.
- [x] [Review][Patch] params=None to insert() raises TypeError before Pydantic validation [src/adapters/config_store/store.py:52] — low. Kept dict(params) conversion for mypy compatibility (Mapping→dict); params=None is a type-contract violation at the caller level.
- [x] [Review][Patch] activate() performs DB lookup before validating inputs [src/adapters/config_store/store.py:104-118] — low. Fixed: ConfigInsertPayload is now constructed before the get() call, so invalid inputs surface as validation errors.
- [x] [Review][Patch] main(argv) unused parameter [src/adapters/db/migrate.py:59] — low. Fixed: removed the unused argv parameter from main().
- [x] [Review][Defer] TOCTOU / no advisory lock in migration runner [src/adapters/db/migrate.py:36-56] — deferred, pre-existing. The `already` set is read outside the apply loop; concurrent runs can double-apply. Spec requires idempotency (re-runs safe) but not concurrent-run safety. Add pg_advisory_lock when concurrent starts become a real scenario.
- [x] [Review][Defer] schema_migrations DDL duplicated between runner and migration 0001 [src/adapters/db/migrate.py:37-44, migrations/0001_config_and_audit_schemas.sql:16-19] — deferred, pre-existing. Both create the same table with IF NOT EXISTS. Definitions are identical today; drift risk if either changes. Consolidate when schema_migrations evolves.
- [x] [Review][Defer] _strip_comments does not handle block comments (/* ... */) [tests/unit/test_schema_ownership.py:41-42] — deferred, pre-existing. Naive split on `--` breaks on string literals containing `--` and misses block comments. No current migration triggers this. Improve when future migrations need it.
- [x] [Review][Defer] Schema-ownership parser misses quoted identifiers [tests/unit/test_schema_ownership.py:30-38] — deferred, pre-existing. Regexes use \w+; quoted identifiers like "Config"."ConfigVersion" bypass the check. No current migration uses quoted identifiers. Improve when needed.
- [x] [Review][Defer] Schema-ownership parser does not detect DROP SCHEMA or ALTER SCHEMA [tests/unit/test_schema_ownership.py:36-38] — deferred, pre-existing. Only CREATE SCHEMA is detected. Spec says "additive only: no down-migrations." DROP/ALTER SCHEMA is out of scope. Add when non-additive migrations appear.
- [x] [Review][Defer] No max-length boundary on author, justification, kind, scope [src/adapters/config_store/models.py:24-29, src/adapters/audit/__init__.py:25-30] — deferred, pre-existing. _non_empty only checks emptiness, no max_length. Potential memory/DoS vector at the editing boundary. The boundary is human-driven (authorized config editors). Add max_length when the threat model requires it.
- [x] [Review][Defer] _ON_TARGET_RE false positives on JOIN ... ON schema.column [tests/unit/test_schema_ownership.py:35] — deferred, pre-existing. The regex matches any ON schema.identifier, not just CREATE TRIGGER/INDEX contexts. No current migration has JOIN clauses. Tighten the regex when JOIN migrations appear.
- [x] [Review][Defer] Schema-ownership check does not enforce per-migration ownership [tests/unit/test_schema_ownership.py:61-71] — deferred, pre-existing. Only global schema declaration is checked, not per-migration authorization. Moot with one migration and one owner per schema. Add per-migration ownership when multiple migrations touch the same schema.
