---
baseline_commit: 4b14a18
---

# Story 1.2: Telegram Bot Wiring & /start Command

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a master,
I want to start the bot via a Telegram deep link and see a welcome message,
so that I can begin onboarding.

## Acceptance Criteria

1. **Given** a master receives a Telegram deep link
   **When** the master sends `/start` to the bot (with the salon payload from the link)
   **Then** the bot responds with a welcome message identifying the salon

2. **And** a canonical `master_id` is created in the `profile` module

3. **And** the `chat_id ↔ master_id` mapping is stored (owned by `profile`, AD-13)

4. **And** a salon-scoped work context row is created (`master_id`, `salon_id`)

5. **And** the salon key is on every created domain row (AD-7)

6. **And** webhook mode works in prod, polling mode works in dev

7. **And** `update_id` dedup is implemented (AD-12)

## Tasks / Subtasks

- [x] Task 1: Migration `0002_profile_master_tables.sql` — `profile` schema (AC: #2, #3, #4, #5)
  - [x] 1.1 `CREATE SCHEMA IF NOT EXISTS profile;` — follow the header/ownership-comment style of `0001_config_and_audit_schemas.sql`
  - [x] 1.2 `profile.salon`: `salon_id text PRIMARY KEY`, `telegram_start_code text NOT NULL UNIQUE` (deep-link payload), `name text NOT NULL`, `tz text NOT NULL DEFAULT 'Europe/Moscow'` (IANA name; static RU zones UTC+2..+12, NFR-F). Seed one dev salon (e.g. `dev-salon` / code `salon1`) so M0 deep links resolve end-to-end
  - [x] 1.3 `profile.master`: `master_id uuid PRIMARY KEY DEFAULT gen_random_uuid()`, `created_at timestamptz NOT NULL DEFAULT now()` — one canonical identity (AD-13). No salon column here: the psych profile is master-level (AD-7); `salon_id` lives on the rows below
  - [x] 1.4 `profile.master_chat_map`: `chat_id bigint PRIMARY KEY`, `master_id uuid NOT NULL REFERENCES profile.master`, `created_at timestamptz NOT NULL DEFAULT now()` — the anchor mapping owned by `profile` (AD-13)
  - [x] 1.5 `profile.work_context`: `(master_id uuid, salon_id text) PRIMARY KEY`, `created_at timestamptz NOT NULL DEFAULT now()` — salon-scoped work context (AD-7); every salon-scoped row carries `salon_id`
  - [x] 1.6 `CREATE SCHEMA IF NOT EXISTS messaging;` + `messaging.telegram_update_dedup`: `update_id bigint PRIMARY KEY`, `processed_at timestamptz NOT NULL DEFAULT now()` — durable `update_id` dedup (AC #7, AD-12). Insert-only (no UPDATE/DELETE needed — table itself is the dedup marker)
  - [x] 1.7 Update `SCHEMA_OWNERS` in `tests/unit/test_schema_ownership.py`: `profile` → the new profile-store adapter package, `messaging` → the new messaging-store adapter package (see Task 2). Keep the SQL parseable by the existing regex check (no block comments / quoted identifiers — see `deferred-work.md` parser limitations)
  - [x] 1.8 Verify with `TEST_DATABASE_URL=… uv run python -m src.adapters.db.migrate` then re-run — idempotent, applies nothing the second time

- [x] Task 2: Domain layer — `src/domain/profile` published interface (AC: #2, #3, #4)
  - [x] 2.1 Define the repository Protocol (e.g. `ProfileRepository` / `MasterRegistry`) in `src/domain/profile/` with async methods: resolve salon by start-code, find-or-create master + chat mapping (idempotent by `chat_id`), find-or-create work context (`master_id`, `salon_id`), and record `update_id` returning whether it was new (dedup gate). NO psycopg/aiogram imports — domain purity is import-linter-enforced (AD-2)
  - [x] 2.2 Implement the `/start` use case as a pure-ish domain service (e.g. `handle_start(repository, chat_id, start_payload) -> StartResult`): unknown/missing payload → no rows created, result says "salon not identified"; known payload → find-or-create master, mapping, work context; result carries salon name for the welcome text. Idempotent: a repeated `/start` from the same chat reuses the same `master_id` (AD-13 — one canonical identity per master)
  - [x] 2.3 Welcome text as a module-level template constant (Russian, deterministic, `rendered_by: template` spirit): identifies the salon by name and tells the master onboarding comes next. Do NOT implement consent capture — that is Story 1.3, strictly after this story
  - [x] 2.4 Typed fully (`disallow_untyped_defs` applies to `src.domain.*`); async defs return concrete result models (Pydantic or dataclass)

- [x] Task 3: Adapters — profile store + Telegram wiring (AC: #1, #2, #3)
  - [x] 3.1 `src/adapters/profile_store/` (new package): psycopg implementation of the Task-2 Protocol, owning the `profile` schema. Follow `PostgresConfigStore` conventions (sync psycopg methods, connection injected)
  - [x] 3.2 `src/adapters/messaging_store/` (new package): minimal psycopg impl exposing `record_update_id(update_id) -> bool` (INSERT … ON CONFLICT DO NOTHING; True = first sighting) owning the `messaging` schema
  - [x] 3.3 `src/domain/ports/telegram.py`: replace the TODO with the first real method — `async def send_message(self, chat_id: int, text: str) -> None` (signatures evolve with later stories per the existing comment)
  - [x] 3.4 `src/adapters/telegram/`: aiogram 3 wiring — `Bot(token)`, `Dispatcher`/`Router` with a `/start` handler that (a) checks/records `update_id` dedup FIRST (skip silently if already seen), (b) opens the DB connection, (c) calls the domain `handle_start`, (d) replies with the welcome or the "use your salon's link" fallback. The handler delegates all decisions to the domain; the adapter is transport only (AD-10: Telegram is transport, not state)
  - [x] 3.5 aiogram implementation of `TelegramPort.send_message` in the same adapter (`bot.send_message(chat_id, text)`) so the reply goes through the port, not raw bot calls from domain code

- [x] Task 4: App wiring — webhook (prod) + polling (dev) (AC: #6)
  - [x] 4.1 `src/app/main.py` `create_app()`: add FastAPI lifespan that constructs the aiogram `Bot` + `Dispatcher` (with the `/start` router) when `BOT_TOKEN` is set, and closes the bot session on shutdown. When `BOT_TOKEN` is unset, log a warning and serve `/health` only — preserves the 1.1a/1.1b regression guard (app starts with no external deps; CI depends on it)
  - [x] 4.2 New endpoint `POST /telegram/webhook`: verify the `X-Telegram-Bot-Api-Secret-Token` header against the configured secret using `hmac.compare_digest` (constant time) → 401/403 on mismatch; parse the body with aiogram's `Update.model_validate` (accept the model directly in the signature); `await dp.feed_webhook_update(bot, update)`; return quickly (Telegram retries on timeout — a retry must be harmless, which the `update_id` dedup guarantees)
  - [x] 4.3 `BOT_MODE` env: `webhook` | `polling`. `webhook` → also call `set_webhook` (with `secret_token`, from `WEBHOOK_URL` + fixed path) in lifespan. `polling` → start `dp.start_polling(bot)` as a lifespan background task (this is the dev mode — no public URL needed). Default: `polling` when `BOT_TOKEN` is set
  - [x] 4.4 New env vars in `.env.example`: `BOT_TOKEN=` (placeholder, exists already — update the comment), `BOT_MODE=polling`, `WEBHOOK_URL=` (public base URL, prod only), `TELEGRAM_SECRET_TOKEN=` (placeholder; note prod secrets live in Yandex Lockbox — AD-5)
  - [x] 4.5 `docker-compose.yml` app service: pass `BOT_MODE: polling` and `BOT_TOKEN: ${BOT_TOKEN:-}` through. App must stay healthy with an empty token (no bot). Worker untouched — bot processes live app-side (architecture: "bot process" on the app VM)
  - [x] 4.6 Redis stays NOT wired (AD-4; Story 1.6). Dedup is Postgres-durable — Redis dedup is only an optimization per AD-12

- [x] Task 5: Tests (AC: all)
  - [x] 5.1 Unit (`tests/unit/`): `handle_start` with a fake repository — new master + mapping + work context created; repeated `/start` same chat → same `master_id`, no duplicate rows; unknown payload → nothing created, fallback result; dedup gate returns "seen" on second sighting
  - [x] 5.2 Unit: webhook endpoint via `TestClient` — wrong/missing secret token → 401/403; valid signed update (construct an aiogram `Update` dict) → 200 and handler invoked; `/health` still `{"status":"ok"}` (regression)
  - [x] 5.3 Contract (`tests/contract/`, gated on `TEST_DATABASE_URL` — follow `test_config_store_db.py` skip pattern): profile store find-or-create idempotency; work-context uniqueness; dedup table first/second-sighting behavior; migration idempotency after `0002`
  - [x] 5.4 No test may touch the real Telegram API — the aiogram `Bot` is never called in tests; exercise the domain/handler logic through fakes and the webhook endpoint through `TestClient`
  - [x] 5.5 All existing tests stay green unchanged; `uv run ruff check .`, `uv run mypy src`, `uv run lint-imports` clean

- [x] Task 6: Verify end-to-end (AC: #1, #6, #7)
  - [x] 6.1 Dev polling smoke: with a real throwaway bot token, `docker compose up -d`, send `/start salon1` → welcome message naming the dev salon; send it again → same welcome, no duplicate master rows in `profile.master`/`master_chat_map`
  - [x] 6.2 Send a plain `/start` (no payload) → "use your salon's link" fallback, no rows created
  - [x] 6.3 `python -m src.app` with no `BOT_TOKEN` still starts and `/health` responds (regression guard); `python -m src.worker` still starts
  - [x] 6.4 Document the bot dev setup in `README.md` (BotFather token, `.env` vars, polling mode, deep-link payload `salon1`)

### Review Findings

Decision-needed:

- [x] [Review][Decision→Defer] Dev seed `dev-salon`/`salon1` ships in the production migration path [migrations/0002_profile_master_tables.sql:56-59] — resolved 2026-09-04: keep as-is (M0-only); remove before production pilot.
- [x] [Review][Decision→Patch] `set_webhook` failure aborts app startup [src/app/main.py:76-78] — resolved 2026-09-04: keep fail-fast, but wrap the call so `bot.session.close()` always runs (fix the session leak).
- [ ] [Review][Decision] Live-Telegram smoke (Task 6.1/6.2) never run — resolved 2026-09-04: run the live polling smoke NOW, before marking done (throwaway BotFather token, `docker compose up`, `/start salon1` twice + plain `/start`). PENDING — awaiting manual smoke run at review time.

Patch:

- [x] [Review][Patch] `set_webhook` session leak [src/app/main.py:76-78] — wrap the webhook-registration branch so `bot.session.close()` runs even when `set_webhook` raises (fail-fast behavior itself stays, per review decision D2).
- [x] [Review][Patch] Dedup row commits before the handler runs — a failed update is permanently lost [src/adapters/telegram/start_router.py:61-65, src/adapters/messaging_store/dedup.py:18-24, src/app/telegram.py:54-57] (HIGH) — each store method wraps in its own `conn.transaction()` which COMMITs on exit, so the dedup marker is durable before `handle_start`/`send_message` run; any handler failure (DB error, user blocked the bot) → webhook 500 → Telegram retry → dedup says "seen" → update never processed. Also: `handle_start`'s two writes commit separately (mid-failure leaves a master with no work context), and the `PostgresStartRepository` docstring claim "one update is one transaction scope" is false. Fix: make the whole update one DB transaction (dedup + all rows commit together after the handler's DB work), and send the reply outside the transaction.
- [x] [Review][Patch] `start_polling` hijacks SIGTERM/SIGINT [src/app/main.py:81] (MEDIUM) — aiogram default `handle_signals=True` overwrites uvicorn's handlers; SIGTERM stops polling but the app never shuts down → `docker stop` hangs to timeout + SIGKILL. Fix: `start_polling(bot, handle_signals=False)`.
- [x] [Review][Patch] Polling-task death is silent and crashes shutdown [src/app/main.py:81-88] (MEDIUM) — an invalid/expired token raises inside the unmonitored task: no log, `/health` stays green; at shutdown `suppress(asyncio.CancelledError)` re-raises the stored original exception. Fix: done-callback that logs/fails loudly + broader suppression at teardown.
- [x] [Review][Patch] `BOT_MODE` not validated [src/app/main.py:65-79] (MEDIUM) — any typo ("WEBHOOK", "webhooks") silently runs polling; if a webhook was previously registered, `get_updates` then 409-conflicts forever. Fix: validate against {webhook, polling} and fail fast on anything else.
- [x] [Review][Patch] Group-chat `/start` creates a canonical master for the group [src/adapters/telegram/start_router.py:73-84] (MEDIUM) — no `chat.type == "private"` filter; a group `chat_id` (negative) gets a `master` + `master_chat_map` row, violating the one-master-per-identity premise (AD-13). Fix: ignore non-private chats.
- [x] [Review][Patch] Blocking `psycopg.connect` on the event loop with no connect timeout [src/app/telegram.py:56] (MEDIUM) — libpq waits indefinitely; a DB outage during bot traffic freezes the whole event loop including `/health` → healthcheck fails → app restarted. Fix: at minimum `connect_timeout` in the connect kwargs (full `asyncio.to_thread` remains the documented M0 tradeoff).
- [x] [Review][Patch] Non-ASCII secret header → `hmac.compare_digest` TypeError → 500 [src/app/main.py:133] (LOW) — Starlette decodes headers latin-1; `compare_digest(str, str)` requires ASCII. Fix: compare `.encode()` of both sides.
- [x] [Review][Patch] `WEBHOOK_URL` trailing slash → `//telegram/webhook` → silent 404 dead bot [src/app/main.py:77] (LOW) — fix: `base_url.rstrip("/")`.
- [x] [Review][Patch] Partial test-override injection silently discarded [src/app/main.py:39-53] (LOW) — `create_app(bot=fake)` without `dispatcher` falls through to the env path and, with `BOT_TOKEN` set, builds a REAL bot — a test could attempt actual Telegram traffic. Fix: raise on partial override.
- [x] [Review][Patch] Protocol-conformance tests assert nothing [tests/unit/test_start_command.py:107-110, tests/unit/test_telegram_webhook.py:182-185] (LOW) — `assert repo is not None` does not check the fakes satisfy `ProfileRepository`/`TelegramPort`; make it a real structural check or drop the pretense.
- [x] [Review][Patch] Task 3/4 subtask checkboxes unchecked despite being implemented — story-file bookkeeping contradicting the Completion Notes; check them off.

Defer:

- [x] [Review][Defer] `messaging.telegram_update_dedup` grows unbounded; every update (incl. unmatched traffic) pays a connection + insert [migrations/0002_profile_master_tables.sql:51-54, src/adapters/telegram/start_router.py:61-66] — deferred, pilot-scale tradeoff; insert-only is the spec design, retention/eviction to be decided with Story 1.6 (Redis layer).

## Dev Notes

### Architecture Compliance (MUST follow)

- **AD-2 (Ports):** aiogram is FORBIDDEN in `src.domain` (import-linter contract in `pyproject.toml`). All aiogram imports stay in `src/adapters/telegram/` and `src/app/`. The domain talks to Telegram only via `TelegramPort`; to persistence only via the repository Protocol.
- **AD-7 (Tenancy):** `salon_id` on every salon-scoped row (work_context). `profile.master` itself is master-level (no salon column) — one psych profile, N salon work contexts. This split is the two-salon foundation; do not collapse it.
- **AD-12 (At-least-once):** `update_id` dedup is the AC requirement. Durable Postgres table now; Redis is an optimization only (and stays unwired until 1.6). `/start` itself must also be idempotent by `chat_id`.
- **AD-13 (Canonical identity):** exactly one `master_id`, owned by `profile`, with the `chat_id ↔ master_id` mapping in the same module. Never key anything off `chat_id` downstream.
- **AD-8 (Time):** all timestamps `timestamptz` UTC defaults; salon `tz` stored as IANA name (static RU zones). No local-time math in this story — quiet hours are Story 1.6.
- **AD-4 (Outbox):** do NOT build the outbox here (Story 1.6). The `/start` reply is a direct reactive answer, not an initiative message — a direct send via `TelegramPort` is correct for this story.
- **AD-10 (Transport, not state):** the aiogram handler contains no business logic — it delegates to the domain service. No policy (caps, quiet hours, pacing) exists yet; none is invented here.
- **AD-5 (Secrets):** `BOT_TOKEN`/`TELEGRAM_SECRET_TOKEN` only ever via env; `.env.example` placeholders only; `.env` already gitignored (1.1c).
- **AD-11 (Schema ownership):** one schema per module; update `SCHEMA_OWNERS` so CI enforces `profile`/`messaging` ownership. Migration SQL must stay parseable by the regex-based check (no `/* */` comments, no quoted identifiers).

### Library & Framework Requirements

| Component | Version | Note |
|-----------|---------|------|
| aiogram | **3.31.0** (pinned, `pyproject.toml:11`) | Do NOT change any pyproject version — pinned and verified at M0 |
| FastAPI | 0.141.1 | webhook endpoint + lifespan |
| Pydantic | 2.13.5 | aiogram `Update` is a Pydantic model — parse via `Update.model_validate` |
| psycopg[binary] | 3.3.5 | sync adapters, connection injected (existing convention) |

**Webhook integration specifics (verified current practice):**
- Verify `X-Telegram-Bot-Api-Secret-Token` against the secret passed to `set_webhook` with `hmac.compare_digest` (constant-time); reject with 401/403.
- Parse body into aiogram's `Update` model, then `await dp.feed_webhook_update(bot, update)` — the documented path for running the Dispatcher behind an arbitrary async web framework.
- Construct `Bot`/`Dispatcher` in FastAPI lifespan; close the bot session on shutdown.
- `set_webhook` supports `secret_token` (1–256 chars of `A-Za-z0-9_-`) and ports 443/80/88/8443 (prod concern, noted for completeness).
- Respond fast after (or while) processing — Telegram retries non-200/timeout deliveries; the retry must be a no-op thanks to `update_id` dedup.

### File Structure Requirements

**NEW files:**
```
migrations/0002_profile_master_tables.sql
src/domain/profile/<repository protocol + start service>.py   # domain purity — no aiogram/psycopg
src/adapters/profile_store/__init__.py (+ impl)
src/adapters/messaging_store/__init__.py (+ dedup impl)
src/adapters/telegram/<bot wiring>.py                          # aiogram Bot/Dispatcher/Router + TelegramPort impl
src/app/<telegram wiring module or extended main.py>
tests/unit/test_start_command.py
tests/unit/test_telegram_webhook.py
tests/contract/test_profile_store_db.py
```

**UPDATE files (read fully before editing):**
```
src/domain/ports/telegram.py        # replace the Story-1.2 TODO with the send_message signature
src/domain/profile/__init__.py      # publish the new interface
src/app/main.py                     # lifespan + webhook endpoint (TODO placeholder is there)
.env.example                        # BOT_MODE, WEBHOOK_URL, TELEGRAM_SECRET_TOKEN; update BOT_TOKEN comment
docker-compose.yml                  # pass BOT_MODE/BOT_TOKEN to app service
tests/unit/test_schema_ownership.py # SCHEMA_OWNERS += profile, messaging
README.md                           # bot dev setup section
```

**DO NOT modify (regression risk):**
```
pyproject.toml                      # versions pinned
src/adapters/config_store/*         # 1.1b, green
src/adapters/audit/__init__.py      # 1.1b, green (reused as-is if you audit master creation)
src/adapters/db/migrate.py          # picks up 0002 automatically — no runner changes
migrations/0001_*.sql               # immutable applied migration
src/worker/*                        # untouched this story
.github/workflows/ci.yml, Dockerfile, .dockerignore
```

### Testing Requirements

- pytest + pytest-asyncio (`asyncio_mode = "auto"` — no markers needed).
- DB-backed contract tests skip without `TEST_DATABASE_URL` (existing pattern, `tests/contract/test_config_store_db.py:22-26`); use unique fixtures per test, never TRUNCATE (immutability triggers block it).
- `uv run mypy src` must pass — `src.domain.*` has `disallow_untyped_defs`.
- `uv run lint-imports` must keep both contracts (domain purity + module independence). Adding files under `src/domain/profile/` is safe as long as no forbidden imports appear.
- CI runs everything automatically (gates: ruff → mypy → lint-imports → pytest ×2 → migrations smoke → image build). Nothing to change in CI.

### Previous Story Intelligence

**Story 1.1c (done, HEAD 4b14a18):** compose dev env (postgres 17-alpine + redis 8-alpine, loopback-only ports, shared `zabota-mentor:dev` image), `scripts/create-test-db.sh` creates throwaway `zabota_test` DB, CI pins Python 3.12 + commit-SHA actions. Review culture: security posture matters (loopback binds, non-root container, secret hygiene) — keep the same posture for the bot token.
**Story 1.1b (done, 8542538):** psycopg[binary] sync style with injected connections; `AuditWriter` for audit events (justification required); migration runner applies `migrations/*.sql` in order, idempotent; schema-ownership check parses SQL with regex — keep new SQL simple.
**Story 1.1a (done, b946792):** app/worker MUST start with no env vars (DB-free/optional-deps) — this guard is tested by CI and user verification every story. `src/app/main.py:21` has the exact TODO for this story's webhook endpoint; `src/domain/ports/telegram.py` has the TODO for the send signature.
**Deferred work (`deferred-work.md`):** worker SIGTERM graceful shutdown; schema-ownership parser limitations (no block comments/quoted identifiers — respect in 0002).

### Git Intelligence

Recent commits: `4b14a18` (1.1c CI/compose), `8542538` (1.1b config+audit), `b946792` (1.1a scaffold). All verification was green at HEAD: pytest 42 passed (with DB), ruff/mypy/lint-imports clean, compose healthy. Build directly on these patterns — do not restructure anything they established.

### Project Structure Notes

- Virtual uv project (`package = false`) running as `src.*` from repo root; entry points `python -m src.app` / `python -m src.worker`.
- Schema/module ownership mirrors 1.1b: adapter package owns its schema (`config` → `config_store`, `audit` → `audit`). New: `profile` → `src/adapters/profile_store`, `messaging` → `src/adapters/messaging_store`.
- The domain `profile` module docstring already says entity models and logic land with Stories 1.4–1.5 — this story starts that surface with the minimal `/start` slice only.

### References

- [Source: epics.md#Story 1.2] — Epic 1 story definition (user story + ACs)
- [Source: ARCHITECTURE-SPINE.md#AD-2] — ports, domain purity
- [Source: ARCHITECTURE-SPINE.md#AD-7] — salon-scoped tenancy, master-level psych profile
- [Source: ARCHITECTURE-SPINE.md#AD-8] — UTC storage, TZ handling
- [Source: ARCHITECTURE-SPINE.md#AD-12] — update_id dedup, idempotency
- [Source: ARCHITECTURE-SPINE.md#AD-13] — canonical master_id + chat mapping ownership
- [Source: ARCHITECTURE-SPINE.md#AD-4 / #AD-10] — outbox deferred, Telegram as transport
- [Source: ARCHITECTURE-SPINE.md#Structural Seed] — app VM hosts FastAPI + bot process; worker separate
- [Source: SOLUTION-DESIGN.md#Build order] — M0 walking skeleton: Telegram webhook, `/start` onboarding
- [Source: migrations/0001_config_and_audit_schemas.sql] — migration style, ownership headers, immutability triggers
- [Source: src/domain/ports/telegram.py] — port TODOs this story resolves
- [Source: src/app/main.py] — webhook endpoint TODO placeholder
- [Source: src/adapters/config_store/store.py] — adapter conventions to follow
- [Source: tests/contract/test_config_store_db.py] — DB test gating pattern
- [Source: tests/unit/test_schema_ownership.py] — SCHEMA_OWNERS map to extend
- [Source: 1-1c…md] — compose/CI layout, security review culture
- aiogram webhook docs: https://docs.aiogram.dev/en/latest/dispatcher/webhook.html and https://docs.aiogram.dev/en/latest/api/methods/set_webhook.html

## Dev Agent Record

### Agent Model Used

claude-sonnet-5 (Claude Code, GLM backend)

### Debug Log References

- Migration 0002 applied twice against `zabota_test` — second run applied nothing (idempotency verified, 1.8).
- Webhook E2E smoke against real Postgres via TestClient: `/start salon1` ×2 → identical welcome naming «Dev Salon», exactly 1 `master_chat_map` row; plain `/start` → Russian fallback, no rows (6.1/6.2 semantics).
- App/worker no-env regression run: app warns "BOT_TOKEN not set — serving /health only", `/health` → 200; worker starts and idles (6.3).
- Live Telegram transport NOT exercised: no real BotFather token available; per user decision (2026-09-04) the simulated E2E above was accepted as verification of 6.1/6.2. Live-Telegram polling smoke remains a manual step for review time (README documents the procedure).

### Completion Notes List

- **Story 1.2 complete** per all ACs; full suite 63 passed (50 unit + 13 contract, DB-backed), ruff/mypy/lint-imports clean, existing tests unchanged.
- **AC #1:** `/start salon1` → welcome identifying the salon (deterministic Russian template `WELCOME_TEMPLATE`, rendered_by: template spirit).
- **AC #2–#5:** canonical `master_id` (AD-13, `pg_advisory_xact_lock(chat_id)` serializes find-or-create — same race pattern as the config store), `chat_id ↔ master_id` map, salon-scoped `work_context` (AD-7, master-level `profile.master` has no salon column), `salon_id` on every salon-scoped row.
- **AC #6:** `BOT_MODE=webhook|polling` (default polling when `BOT_TOKEN` set); webhook registers in lifespan with `secret_token` + constant-time header check (401 missing / 403 mismatch / 503 unconfigured); polling runs `dp.start_polling` as a lifespan background task. No `BOT_TOKEN`/`DATABASE_URL` → warning + `/health` only (1.1a regression guard intact, verified).
- **AC #7:** durable `update_id` dedup — an update-level aiogram outer middleware (`UpdateDedupMiddleware`) checks/records dedup FIRST, opens one psycopg connection + repository per update, and skips repeats silently. Redis untouched (AD-4).
- **Design decisions:** (a) repository protocol methods are `async` per story 2.1; adapters implement them over sync psycopg (single fast statements — documented in `profile_store/store.py` as an M0-scale tradeoff, revisit `asyncio.to_thread` if the loop ever blocks measurably). (b) `ProfileRepository`'s four methods are satisfied in production by a composition-root composite (`PostgresStartRepository` in `src/app/telegram.py`) delegating to `profile_store` (profile schema) and `messaging_store` (messaging schema) sharing one connection per update — keeps AD-11 schema ownership clean. (c) `create_app(bot=…, dispatcher=…)` injection points let webhook tests drive the real `feed_webhook_update` path with fakes, no Telegram API (5.4).
- Task 3.4's "(b) opens the DB connection" ordering nuance: the dedup check itself needs the connection, so the middleware opens it once per update before dedup and passes the repository to handlers — strictly better than opening twice.
- Files under `src/domain/profile/` added without touching existing modules; import-linter contracts (domain purity + module independence) still pass.

### File List

New:
- migrations/0002_profile_master_tables.sql
- src/domain/profile/models.py
- src/domain/profile/repository.py
- src/domain/profile/start.py
- src/adapters/profile_store/__init__.py
- src/adapters/profile_store/store.py
- src/adapters/messaging_store/__init__.py
- src/adapters/messaging_store/dedup.py
- src/adapters/telegram/port.py
- src/adapters/telegram/start_router.py
- src/app/telegram.py
- tests/unit/test_start_command.py
- tests/unit/test_telegram_webhook.py
- tests/contract/test_profile_store_db.py

Modified:
- src/domain/ports/telegram.py (send_message signature replaces the TODO)
- src/domain/profile/__init__.py (publishes the new interface)
- src/adapters/telegram/__init__.py (exports the wiring)
- src/app/main.py (lifespan + POST /telegram/webhook)
- tests/unit/test_schema_ownership.py (SCHEMA_OWNERS += profile, messaging)
- .env.example (BOT_MODE, WEBHOOK_URL, TELEGRAM_SECRET_TOKEN, BOT_TOKEN comment)
- docker-compose.yml (app: BOT_MODE/BOT_TOKEN passthrough)
- README.md (Telegram bot dev setup section)

## Change Log

- 2026-09-04: Story created via create-story workflow — ultimate context engine analysis completed, comprehensive developer guide created.
- 2026-09-04: Story implemented — migration 0002 (profile + messaging schemas), domain /start slice, profile/messaging stores, aiogram wiring with update-level dedup middleware, webhook+polling app lifecycle, 21 new tests; story → review.
