# zabota_mentor

Telegram-based coaching assistant for beauty-industry masters.
Hexagonal modular monolith: one deployable, six modules (`crm_sync`, `profile`,
`engines`, `messaging`, `llm`, `config`) plus an append-only `audit` trail.

- **Python:** 3.12+
- **Runtime (pinned in `pyproject.toml`):** FastAPI 0.141.1, uvicorn 0.52.4, aiogram 3.31.0, Pydantic 2.13.5
- **Target services (connected in later stories):** PostgreSQL 17, Redis 8.x

## Source tree

```
src/
  domain/            # pure domain layer — no framework imports (enforced by import-linter)
    profile/         # profiles, consent, dynamic profiling state
    engines/         # deterministic calculation engine, plan tracking
    messaging/       # communication contract, templates, dispatcher rules
    ports/           # CrmPort, LlmPort, TelegramPort, Clock, ConfigStore Protocols
  adapters/          # port implementations: crm_adapter, llm, telegram, clock, config_store
  app/               # FastAPI wiring, DI, webhook endpoints
  worker/            # scheduler, outbox dispatcher, sync jobs
tests/
  unit/  contract/  golden/
```

## Setup

Requires [uv](https://docs.astral.sh/uv/) — the dev tooling (pytest, ruff, mypy,
import-linter) is installed via uv dependency groups, not `pip install .`:

```bash
uv sync                 # creates .venv and installs pinned runtime + dev deps
```

## Run

```bash
uv run python -m src.app     # FastAPI app: http://127.0.0.1:8000/health  (APP_HOST/APP_PORT env overrides)
uv run python -m src.worker  # worker: starts and idles (no DB/Redis/Telegram needed)
```

## Test & verify

```bash
uv run pytest         # unit/contract/golden test suite
uv run ruff check .   # lint
uv run mypy src       # static type check
uv run lint-imports   # architecture contracts: domain purity + module boundaries
```

`lint-imports` must stay green — it enforces AD-2 (domain imports nothing from
frameworks/adapters; Pydantic is allowed as the schema-layer convention) and
AD-11 (`profile`, `engines`, `messaging` are mutually independent). CI wiring
arrives with Story 1.1c; these commands are the exact commands CI will run.

### DB-backed tests (PostgreSQL 17)

Tests touching Postgres (config store, audit log — Story 1.1b) are gated on
`TEST_DATABASE_URL`; without it they skip with a visible reason and the unit
layer stays fully green. To run them against a throwaway Postgres 17:

```bash
docker run --rm -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:17
TEST_DATABASE_URL="postgres://postgres:postgres@localhost:5432/postgres" uv run pytest
```

(The compose file with a proper dev DB service arrives with Story 1.1c.)

### Migrations

Plain ordered SQL files in `migrations/` (`NNNN_description.sql`), applied by a
minimal idempotent runner — no Alembic, no down-migrations. Apply pending
migrations to the database named in `DATABASE_URL`:

```bash
DATABASE_URL="postgres://…" uv run python -m src.adapters.db.migrate
```

Schema ownership is governed: `tests/unit/test_schema_ownership.py` maps each
Postgres schema to its owning module adapter and fails on cross-module access
(AD-11).
