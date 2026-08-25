# Stack & Module Ownership — Zabot AI Mentor, Stage 1

> Implementation substrate pinned by the architecture (final). Detail lives in the architecture docs; this companion is the downstream-readable summary. Versions verified current 2026-08-16/17 (research) and re-checked 2026-08-18 (gate); loose pins fixed in `pyproject`/compose at M0.

## Stack

| Name | Version |
| --- | --- |
| Python | 3.12+ |
| FastAPI (webhooks / internal API) | pinned at M0 (0.141.x current) |
| aiogram 3 (Telegram bot) | 3.x (3.30.x current) |
| PostgreSQL (managed, Yandex Cloud) | 17 (Yandex offers 14–18; single-major-upgrade policy — pin at M0) |
| Redis | pinned at M0 (8.x current) |
| Deploy | docker compose, 2 VMs (app node + worker node), Yandex Container Registry |
| CI/CD | GitHub private repo + self-hosted RU runner (GitLab CE fallback) |
| Testing | pytest + pytest-asyncio, promptfoo (LLM golden set) |
| LLM hop | ProxyAPI **or** own egress VM (open — OQ-6), OpenAI behind `LlmPort` |
| Observability | Sentry, Grafana / Yandex Cloud Monitoring |

## Module → schema → ownership

| Module | Owns | Postgres schema |
| --- | --- | --- |
| `crm_sync` | webhook ingest (unverified) + REST polling + nightly reconcile, CRM mirror projections, ingestion-assigned surrogate IDs, erasure tombstones | `crm_mirror` |
| `profile` | master identity + `chat_id↔master_id` mapping, **psychological profile (master-level, not salon-scoped)**, scales, traffic-light **committed** state, **consent state (4 consents, AD-17)**, preference state, memory recency/archival policy, insistence counters, pause/opt-out state | `profile` |
| `engines` | scoring, income/forecast, recommendation, **adaptive bar logic (agent-calc-DB master, AD-3)**, shift-window derivation, business-KPI aggregation — pure compute over the agent calculation DB | `engines` |
| `messaging` | scheduler, outbox, dispatcher, arbitration, dialogue state, `RenderFacts`/`TriggerCandidate` contracts, **output validator (AD-16)**, owner-facing render (aggregate-only, psych-layer-inaccessible) | `messaging` |
| `llm` | prompt assembly from `RenderFacts`, depersonalization strip + **placeholder-name substitution (AD-5)**, `LlmPort` calls, template fallback, reverse-substitution re-personalization | (stateless — no schema; consumes `messaging` via its published interface) |
| `config` | insert-only versioned config + versioned prompt artifacts, editing boundary | `config` |
| cross-cutting | append-only audit | `audit` |

## Consistency conventions

| Concern | Convention |
| --- | --- |
| Naming | Python `snake_case` modules/tables; ports named `XxxPort`; canonical entities `Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment` |
| Schema layer | Pydantic models are the single definition from transport (webhook/CRM/LLM structured output) to storage (JSONB typed via the same models) |
| Identity | Canonical internal `master_id` on every cross-module reference (AD-13); psych profile hangs off `master_id`, work context off (`master_id`, `salon_id`) (AD-7); `chat_id` is the Telegram transport anchor; machine-to-machine API keys only (no OAuth); salon key on every domain row |
| Time | UTC `timestamptz` everywhere in storage; `source_event_at` vs `synced_at` per mirror row (AD-9); **dual TZ stored — salon + master** (AD-8); quiet hours + personal sends in master TZ, pre-visit in salon TZ, both evaluated at send decision |
| Mutation | No side effect without a durable record first (outbox row / audit entry / config-version reference). `audit` is append-only: config changes, consent events (grant + each revocation), profile scale/type changes **with justification** (§6.5), LLM egress events (payload hash + allowlist + placeholder-map version), output-validator failures, erasure requests and what they purged, export/delete requests, sync runs, nightly reconcile runs |
| Errors & fallbacks | LLM failure → deterministic template fallback (`rendered_by: template`); **output-validator mismatch → message not sent, template fallback queued (`rendered_by: validator-fallback`)** (AD-16); quiet-hours miss → defer to next window; CRM stale → AD-9 ladder; incomplete plan/config → AD-6 completeness mode; consent #4 withdrawn → template-only narration (AD-17) |
| Logging & observability | Structured JSON, PII-scrubbed; alerting on user-visible SLOs (per-entity freshness, oldest pending outbox row, LLM-port error rate, quiet-hours defer rate, output-validator fail rate), not CPU |

## Minimal source tree

```text
src/
  domain/          # pure: entities, engines, ports (Protocols) — no framework imports
    profile/  engines/  messaging/
  adapters/        # crm_adapter (+ fixture), llm (strip + placeholder map → gateway), telegram (aiogram), clock, config_store
  app/             # FastAPI wiring, DI, webhook endpoint
  worker/          # scheduler entry, outbox dispatcher + arbitration + output validator, sync jobs (webhook ingest + poll + nightly reconcile)
tests/
  unit/            # engines, hysteresis, income math, bar corridor, quiet hours via injected Clock, output validator
  contract/        # CRM fixture replay, egress strip + placeholder assertions
  golden/          # promptfoo: facts present, no invented numbers, register + ethics cases, validator rejects injected wrong numbers
```
