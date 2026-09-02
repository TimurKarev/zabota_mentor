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
