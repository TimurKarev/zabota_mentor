# Epic 1 Context: Onboarding, Consent & Foundation (M0)

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Epic 1 delivers the M0 foundation: a master can start the Telegram bot, grant 4 separate consents, complete primary profiling, and receive first calibration-mode template messages — entirely on a fixture CRM with zero external dependencies. It establishes the repo scaffold, hexagonal ports, insert-only versioned config store, append-only audit log, CI, and the communication-contract machinery (caps, quiet hours, floor/pause/opt-out) that every later epic builds on.

## Stories

- Story 1.1a: Repo scaffold, ports & module boundaries
- Story 1.1b: Versioned config store & audit log
- Story 1.1c: CI pipeline & Docker Compose dev environment
- Story 1.2: Telegram bot wiring & /start command
- Story 1.3: 4-consent capture at onboarding
- Story 1.4: Primary profiling dialogue
- Story 1.5: Master profile state & dynamic profiling
- Story 1.6: Communication contract, caps & quiet hours
- Story 1.7: Template messages (shift-start & minimal shift totals)
- Story 1.8: Communication floor, pause & opt-out
- Story 1.9: Cold start & incomplete profiling handling
- Story 1.10: Fixture CRM & contract tests

## Requirements & Constraints

- **4 separate consents** (PDn processing + profiling; emotional-state data; correspondence history retention; cross-border transfer of depersonalized data to LLM) are collected BEFORE any profiling question. Without consent (1) the service is not activated; no cold messaging by design. Consents (2) and (3) are independently revocable via bot command: (2) off → screenings/tone disabled; (3) off → aggregated-profile-only mode; (1) off → service deactivated; (4) off → LLM egress blocked, template-only narration. Every profiling/egress decision links to an active consent record; grants/withdrawals audited with fact + date.
- **Profile model:** motivational type (1 of 5 archetypes) + 9 live scales 0–100 (ambitiousness, pressure sensitivity, need for support, sales confidence, sale framing, preferred frequency, preferred tone, execution discipline, failure reaction). Scales, not the type, drive behavior. Scale updates use exponential smoothing with per-scale alpha (fast 0.3–0.5, slow 0.1–0.2), config-managed, logged with versions. Type changes only when an alternative scores +15 points higher for ≥ 2 consecutive pay periods, logged with justification, never disclosed to the master as a label. Explicit master requests ("пиши короче", quiet-hour overrides) apply immediately, bypass smoothing, logged as "manual setting".
- **Profiling dialogue:** one question at a time with reactions to answers; mandatory questions cover SDT source, promotion/prevention, format preference, attitude to offering extras (key question), bad-day reaction, frequency, quiet hours/address. Ends with stated working agreements + confirmation; first 2 weeks = calibration mode with elevated format-feedback requests. Scoring algorithm for mapping answers to archetype scores is an open question (OQ-12) — use a config-defined mapping until resolved.
- **Communication contract:** per-master touch frequency, message length, tone, challenge/support ratio, number format, send times — starting values set by archetype (touches per shift range 1–4; challenge/support ratio from 70/30 down to 15/85). Hard caps: ≤ 5 initiative messages per shift, ≤ 2 on days off, lower on yellow/red. Quiet hours default 21:00–9:00 master TZ, guaranteed on the send side (never send inside the interval), configurable by owner and master.
- **Floor / pause / opt-out:** minimum floor while consent is active = 1 period-summary message + reactive answers; reactive mode always available. Automatic pause when no shifts ≥ 5 days (config N) + manual pause; during pause silence except reactive answers. Full opt-out degrades to legally required notices only; owner sees only the fact "master disabled the assistant", no reasons. Communication never stops on the AI's initiative.
- **Cold start:** no CRM history → first pay period = observation + support mode (no bar, no income forecast; the bar itself belongs to Epic 3, first set in period 2 from actuals). Incomplete profiling → default max-caution profile ("Cautious" settings); missing answers gathered one at a time over 1–2 weeks. Onboarding never blocked on data sparsity.
- **Determinism in M0:** all figures in template messages computed deterministically (no LLM); messages reproducible from (facts, config_version, prompt_version); every significant decision (consent, config change, profile change, egress) in the append-only audit log with justification and inputs.

## Technical Decisions

- **Stack (pinned at M0):** Python 3.12+ modular monolith; FastAPI, aiogram 3, PostgreSQL 17, Redis 8. Source tree: `src/domain` (profile, engines, messaging — pure, no framework imports) + `src/adapters` (crm_adapter + fixture, llm, telegram, clock, config_store) + `src/app` (FastAPI wiring) + `src/worker` (scheduler, outbox dispatcher) + `tests` (unit/contract/golden). Import-linter enforced in CI.
- **Ports:** domain defines Protocol interfaces — `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore` — implemented by adapters; no external call from domain.
- **Config store:** insert-only versioned rows, Pydantic-validated at the editing boundary; edits create new versions; active version resolved at decision time (compute and send never span versions); rollback < 5 min.
- **Audit:** one append-only `audit` schema; one Postgres schema per module; schema-ownership CI check forbids cross-module table access.
- **Identity & tenancy:** one canonical `master_id` owned by `profile`; `chat_id ↔ master_id` mapping owned by `profile`; salon-scoped work context (`master_id`, `salon_id`); salon key on every domain row; master-in-two-salons = one psych profile, two work contexts.
- **Time:** UTC in DB (timestamptz); store BOTH salon TZ and master TZ (master defaults to salon, overridable); quiet hours + personal sends in master TZ; scheduler evaluates quiet hours at send-decision time, not baked into job fire time.
- **Transactional outbox:** every outbound side effect written as an outbox row in the same transaction as the decision; dispatcher sweeps due rows (FOR UPDATE SKIP LOCKED) every 15–30 s; Redis never holds durable state. Telegram pacing ~1 msg/s per chat via per-chat_id Redis token buckets.
- **Idempotency:** Telegram `update_id` dedup; sync/outbox upserts idempotent by natural key.
- **Telegram modes:** webhook in prod, aiogram polling in dev; inline keyboards (1–5 buttons) for consent capture and screenings; engagement is answer-based only (no read receipts).
- **Fixture CRM:** recorded payloads served behind `CrmPort`, doubling as the contract-test suite; canonical model `Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment`; surrogate IDs assigned at first ingestion; adapter translates CRM payloads (names, enums, timezones, money formats) at the boundary.
- **CI/CD:** GitHub private repo + self-hosted RU runner; CI runs ruff, mypy, unit/contract tests, import-linter, schema-ownership check; docker compose dev env (Postgres 17 + Redis 8) with health check. Secrets in Yandex Lockbox.
- **Consent as state:** consents are a first-class stateful entity owned by `profile` (not just flags); pause/opt-out state also owned by `profile` and audited.

## UX & Interaction Patterns

- No UX design contract exists — Stage 1 is a Telegram bot; interaction behavior is specified behaviorally in the requirements.
- Onboarding flow: deep link → `/start` → salon-identifying welcome → 4 consent screens (inline keyboards, independent capture) → one-question-at-a-time profiling dialogue with reactions to answers → stated working agreements + confirmation → 2-week calibration mode.
- Inline keyboards (1–5 button scale) are the only "widget", used for consents and later screenings.
- Tone registers per archetype (energetic/playful/respectful/warm/soft); bad-day reactions follow the type matrix — no hot debrief for sensitive types, support-only with next-day debrief for Cautious.
- The type is never disclosed as a label; on request the master gets a soft descriptive answer.

## Cross-Story Dependencies

- Stories 1.1a → 1.1b → 1.1c are a strict scaffold sequence; all other stories depend on 1.1a/1.1b foundations.
- Story 1.2 (/start) creates the master identity and work context that 1.3 (consents), 1.4 (profiling), 1.5 (profile state) build on; 1.4 requires all 4 consents granted.
- Story 1.7 template messages depend on 1.6 (scheduler/quiet hours/outbox) and 1.10 (fixture CRM data).
- Erasure on consent (3) withdrawal is NOT implemented here — it is delegated to the cross-module erasure-propagation story in Epic 7 (Story 7.4); `profile` orchestrates.
- Dynamic profiling (1.5) wires only reply + behavior signal streams now; CRM-results and screening streams arrive in Epics 2 and 5.
- Shift totals in 1.7 are fixture-derived only (revenue, avg check, one praise); recommendation outcomes, progress toward bar, and income forecasts are deferred to Epics 3–4.
- Traffic-light status consumed by caps (lower on yellow/red) is produced in Epic 5 — until then, only default caps apply.
