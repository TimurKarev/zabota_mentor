---
stepsCompleted: ["step-01-validate-prerequisites", "step-02-design-epics", "step-03-create-stories"]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/prd.md
  - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md
  - docs/Вопросы_команды_и_ответы_по_БТ_v2_1.md
---

# Zabot AI Mentor (Stage 1) - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Zabot AI Mentor Stage 1, decomposing the requirements from the updated PRD (2026-08-23) and Architecture Spine (final, 2026-08-23) into implementable stories.

**Input documents:** PRD (2026-08-23, reflects Team Q&A change signal v2.1) + Addendum; Architecture Spine (final, 2026-08-23); Team Q&A with owner answers (`docs/Вопросы_команды_и_ответы_по_БТ_v2_1.md`, 23.08.2026). No UX design contract (Stage 1 is a Telegram bot; interaction behavior is specified in the PRD itself).

**Key change from previous epics (2026-08-20):** §11.2 motivation scheme constructor (5 types) is REMOVED from Stage 1 → backlog. Stage 1 works only with the 2 Zabot plan types (plan by master's average check, plan by total revenue). All epics/stories related to the 5-type constructor, bonus tiers, or rule engine are removed. Replaced with stories for: reading Zabot plans, progress tracking, adaptive bar calculation, deterministic calculation engine, and output validator.

**Disambiguation — "5 types" naming collision:** Two unrelated "5" concepts appear in source docs. (a) **Psychotype archetypes** (Addendum A.2) — 5 motivational archetypes used for tone/register selection; **retained in Stage 1** (FR-2.1, FR-2.4, Stories 1.4/1.5). (b) **Motivation scheme constructor** (Addendum A.6, BRD §11.2) — 5 plan-type taxonomy with tiers/rates/bonus rules; **deferred to backlog**. Throughout this document, "5 archetypes" = (a); "5-type constructor" = (b).

## Requirements Inventory

### Functional Requirements

**F1 — Onboarding & Consent**

- FR-1.1: Onboarding via Telegram deep link + `/start`; 4 separate consents collected at onboarding BEFORE any profiling question (owner-confirmed 23.08): (1) PDn processing + profiling; (2) emotional-state data processing; (3) correspondence history retention; (4) cross-border transfer of depersonalized data to LLM provider. Without consent (1) the service is not activated. No cold messaging possible by design.
- FR-1.2: Primary profiling as a live 3–5 min dialogue (one question at a time, reactions to answers); determines starting motivational type, starting scale values, preferred tone/frequency, personal quiet hours. Mandatory questions — Addendum A.4.
- FR-1.3: CRM history analysis at onboarding (current avg check, complexity, dynamics) for a realistic starting bar. Cold start: config-defined conservative priors; onboarding never blocked.
- FR-1.4: AI states working agreements at end of onboarding and obtains confirmation; first 2 weeks = calibration mode with elevated format-feedback requests.
- FR-1.5: Consent withdrawal — consents (2) and (3) independently revocable via bot command, with fact + date recorded. Withdraw (2) → screenings/tone disabled (traffic light on CRM signals only). Withdraw (3) → aggregated-profile-only mode (raw correspondence deleted, aggregated profile retained). Withdraw (1) → service deactivated. Every profiling decision links to an active consent record. PDn operator = service legal entity [уточнить: OQ-11]; salon is independent PDn operator of clients. Roskomnadzor notification before pilot.

**F2 — Master Profiling (hybrid: type + live scales)**

- FR-2.1: Profile = motivational type (1 of 5 archetypes, Addendum A.2) + 9 live scales 0–100 (Addendum A.3); scales, not the type, drive real behavior over time.
- FR-2.2: Dynamic profiling from four signal streams: master replies, behavior (answered/ignored by message class), CRM results, state screenings (F6).
- FR-2.3: Scales move via exponential smoothing; α per-scale config parameter (fast 0.3–0.5, slow 0.1–0.2), changeable without release; values and versions logged.
- FR-2.4: Type change when alternative type scores higher by sustained delta (starting +15 points out of 100) for ≥ 2 consecutive pay periods; logged with justification; master never told "label changed."
- FR-2.5: Explicit master request ("пиши короче", "без эмодзи", "не пиши до 10:00") applies immediately, bypasses smoothing, logged as "manual setting."
- FR-2.6: Type never disclosed to master as a label; soft descriptive answer on request.
- FR-2.7: Progress definition (gates bar raises): sliding 2-week window; progress = key bar metric growth ≥ +5% vs previous window OR bar retention ≥ 95% throughout window — at load ≥ 80% of master's typical. Both thresholds config-defined.
- FR-2.8: Cold start (no CRM history): first pay period = observation + support mode (no bar, no income forecast); onboarding + pre-visit recommendations work from day one. Bar first set in period 2 from period-1 actuals ("introductory," deliberately attainable). Incomplete profiling → default max-caution profile ("Cautious" settings); missing answers gathered over 1–2 weeks.

**F3 — Communication Engine (communication contract)**

- FR-3.1: Per-master communication contract: touch frequency, message length, tone, challenge/support ratio, number format, send times; starting values by type.
- FR-3.2: Hard caps: ≤ 5 initiative messages per shift, ≤ 2 on days off; lower on yellow/red. Quiet hours default 21:00–9:00 master TZ, guaranteed on send side; configurable by owner and master.
- FR-3.3: Pre-visit recommendations sent T-30…60 min before appointment, evaluated in salon TZ.
- FR-3.4: Message-class disable ladder: period-total and pre-visit recommendation classes disabled last; pre-visit only on explicit master request.
- FR-3.5: Ignore detection: ≥ 70% messages ignored over 2 weeks → reduce frequency to minimum and ask once, directly; never escalate pressure.
- FR-3.6: Trigger arbitration: highest expected-income-value message sent; others deferred or merged — always inside caps.

**F4 — Recommendation Engine (next best offer)**

- FR-4.1: Signal sources: full client visit history, product purchase cycles, service cyclicity/gaps, seasonality, visit comments, owner priorities, past refusals.
- FR-4.2: Candidates = owner priorities ∪ history-logical positions; exclusion filters: ≥ 2 consecutive refusals → N-month pause, contraindications/allergies, stop-list, incompatibility with booked service.
- FR-4.3: Ranking by expected value: acceptance probability × margin/priority.
- FR-4.4: 1–3 recommendations per visit (fewer is better); what/why/how format; depth by sales-confidence scale (full script for novices, thesis for veterans).
- FR-4.5: Zero-survey feedback loop: never asks master whether they offered; outcomes reconciled from check contents only; no interrogation.
- FR-4.6: Automatic outcomes update client profile, master profile (conversion by type), and engine quality.

**F5 — Coaching Cycles (shift / week / pay period)**

- FR-5.1: Shift-start message: day plan, one day focus, mood screening 2–3×/week, motivational message in psychotype tone.
- FR-5.2: Micro-support between visits only on schedule gap + green status.
- FR-5.3: Shift totals: revenue, avg check, recommendation outcomes, progress + deterministic income forecast, one specific praise; bad-day reaction per type matrix (no hot debrief for sensitive types).
- FR-5.4: GROW session at period end: Goal (bar + nearest money lever), Reality (honest totals, self-comparison), Options (master chooses), Will (agreements fixed).
- FR-5.5: Forcing requires all three: sustained progress (FR-2.7), green status, master's explicit consent via GROW gate; proximity trigger < 10–15% to plan → sprint offer.
- FR-5.6: Pace reset on: yellow/red status; ≥ 2 weeks without progress; life circumstances; post-sprint recovery window.
- FR-5.7: Barrier work: systematic non-conversion → soft MI-style diagnostics (knowledge/skill/psychology) → matching intervention matrix (Addendum A.5).

**F6 — Emotional Monitoring & Traffic Light**

- FR-6.1: Signal sources: screenings 2–3×/week + WHO-5-derived check-in every 2 weeks; correspondence tone analysis; indirect CRM signals.
- FR-6.2: Traffic light = composite score (0–100) from three streams, config-weighted; status transitions decided in code, never by LLM; tone below confidence threshold cannot change status.
- FR-6.3: Hysteresis: differing entry/exit thresholds with minimum stay (yellow entry < 60 for 3 days, exit ≥ 70 held 3 days; red entry < 40 for 7 days, exit ≥ 55 held 7 days). Calibration guidance: false reds ≤ 1/10 masters/month; missed burnouts = 0; yellow↔green ≤ 1/week per master.
- FR-6.4: Status behavior: green — standard; yellow — frequency ↓, support ↑, forcing forbidden; red — support only, no goals, no sales, delicate owner escalation.
- FR-6.5: Ethics: screening framed as care; non-response never a pressure reason; no diagnoses; red escalation carries conclusion + recommendation only, no correspondence quotes.

**F7 — Goals, Adaptive Bar & Motivation Plans (UPDATED 23.08 — 2 Zabot plan types only)**

- FR-7.1: Goal (цель) = plan set by owner in Zabot — one of two types only: plan by master's average check OR plan by total revenue — read-only to the agent, AI never changes it. Adaptive bar (планка) = internal agent value (lives in agent calculation DB): individual trajectory of master toward the Zabot plan. AI adapts bar and path, never the goal.
- FR-7.2: Goals/motivation module is READ from Zabot (the 2 plan types), not built inside Mentor. No two-way sync — direction strictly Zabot → agent, read-only. 5-type scheme constructor (BRD §11.2) deferred to backlog.
- FR-7.3: Owner configures in Zabot: the 2 plan types (avg-check target, total-revenue target per pay period). In agent's own settings (stored in agent calculation DB): priority services & goods, stop-list, default quiet hours, communication limits, and optionally remuneration rules (rates, percentages) if ruble income calculations are wanted (FR-9.5). Pay period read from Zabot.
- FR-7.4: Stage 1 supports ONLY the 2 Zabot plan types. No scheme constructor, no tier/rate/bonus configuration, no percent-base question, no rule engine. Agent reads plans + actuals from Zabot/CRM and computes everything derived (progress to plan, pace, attainment forecast, adaptive bar within the plan, decomposition "how much per visit/shift") in its own calculation DB. 5-type taxonomy (Addendum A.6) retained as backlog reference only.
- FR-7.5: On incomplete plan data, the AI invents no income figures — metrics only + clarification request to owner (config-completeness degradation).
- FR-7.6: Adaptive bar (Locke–Latham): specific, measurable, difficult-but-attainable (~60–70% attainment probability [уточнить: OQ-10 method]), accepted in GROW. Corridor rules (config-defined): calculated bar = forecast from master's actual dynamics; allowable deviation ±15%; raise step ≤ +10% per period; tactical lowering on yellow/red not below −15% of calculated bar and not below master's 2-period actual average. Bar cannot exceed Zabot plan; if plan below master's actual level, agent holds at actual level and reports to owner. Movement rules: raise on progress + consent; stagnation — hold + diagnose; decline — never raised. Never framed as punishment.
- FR-7.7: Income transparency: master can ask income/plan/what-if questions — answered by deterministic calculation. Ruble income figures appear ONLY if owner entered remuneration rules in agent settings (FR-9.5); otherwise agent works in metric and plan-progress terms ("240 ₽/visit left to the avg-check plan" — plan-relative, not salary).
- FR-7.8: Plan changes (owner in Zabot) apply from next pay period; AI explains to master what changed in their plan/progress.

**F8 — Proactive Triggers**

- FR-8.1: Trigger catalogue: period-bar risk, growth opportunity, proximity to plan attainment, negative pattern, positive pattern, master silence beyond norm.
- FR-8.2: All initiative messages pass through caps, priorities, arbitration; proactivity ≠ frequency.

**F9 — Deterministic Money Math & LLM Roles (UPDATED 23.08 — agent calc DB + output validator + ruble gate)**

- FR-9.1: All figures — income, forecasts, bar values, plan progress, scores, rankings, cap counts — computed deterministically by the agent's calculation engine over its calculation DB (separate DB replicating needed CRM/Zabot entities + all derived values: metric dynamics, plan progress, adaptive bar, recommendation conversion, traffic-light score). CRM/Zabot is master of operational data + motivation plans; agent is master of all derived data — conflict excluded by construction. LLM receives computed values as bound inputs, forbidden from generating/estimating/rounding any figure.
- FR-9.2: LLM has exactly three roles: (a) narrator of pre-computed facts; (b) structured-output classifier (tone 0–1 + confidence; below threshold cannot change state); (c) bounded MI/GROW coaching-dialogue partner under versioned prompts.
- FR-9.3: On LLM outage or budget trip, narration degrades to deterministic templates — wording degrades, correctness never does. Zero figure-accuracy incidents is hard (CM-4).
- FR-9.4: Output validator — every money-type number in an outgoing message must match the corresponding computed number (rounding done only by engine, before passing to LLM). A message that fails validation is NOT sent. Hard enforcement layer on top of FR-9.1.
- FR-9.5: Ruble calculation gate — if remuneration parameters (rates, percentages) are not available via Zabot API, agent does NOT compute salary in rubles; works in metrics and plan-progress terms. Ruble income forecasts enabled ONLY if owner has entered remuneration rules in agent settings (stored in agent calc DB); then agent computes by those rules and labels result as service estimate, not Zabot data.

**F10 — Owner Reporting & Escalation**

- FR-10.1: Per pay period, per master: metrics vs plan and previous period; plan-attainment position and income dynamics; recommendation conversion (CRM-measured); praise facts; improvement areas + how owner can help; aggregated state signals; profile status.
- FR-10.2: Out-of-band escalation only on red status or systemic anomalies.
- FR-10.3: Confidentiality: correspondence never transmitted to owner except aggregated conclusions; aggregation boundary enforceable (no verbatim, no quote-length fragments).

**F11 — CRM Integration & Data Freshness**

- FR-11.1: Data via Zabot CRM: visit history incl. comments; sales by master by client; shift load/schedule; bookings; check composition; metric dynamics; cancellations.
- FR-11.2: Freshness: checks/sales ≤ 60 min; schedule/bookings ≤ 15 min; dynamics/period totals ≤ 24 h (config-defined, pilot-calibrated).
- FR-11.3: Degradation ladder: Level 1 (stale but usable) — timestamp label, forecasts suppressed; Level 2 (hard-stale/down) — no figures, money math/praise/forecasts suspended, honest notice. Recovery — resync, recompute, no retroactive event messages (exception: late praise within 60 min, no later than end of same shift).
- FR-11.4: Cold start: config-defined conservative priors per entity; onboarding never blocked on data sparsity.
- FR-11.5: Sync = Zabot webhooks (unverified, pending OQ-1) + REST API polling + nightly full reconcile; direction strictly one-way CRM/Zabot → agent, read-only. No writes to Zabot. Fixture CRM keeps M0 unblocked.

**F12 — Memory & Personalization**

- FR-12.1: Long-term memory (master profile, client recommendation profiles, bar history); short-term focus (current period, week focus, open agreements).
- FR-12.2: Fresh signals outweigh old; stale observations archived out of prompt set (periods config-defined).
- FR-12.3: Memory used for help, never pressure; no reminding of past failures.

**F13 — Communication Floor, Pause & Opt-out**

- FR-13.1: Minimum floor: 1 period-summary message + reactive answers to incoming (reactive mode always available). Pre-visit recommendations disabled last, only on explicit master request.
- FR-13.2: Pause/vacation mode: automatic pause when no shifts scheduled ≥ N days (starting N=5, config-defined); manual pause. During pause: silence except reactive answers. Goals/bar logic accounts for pause.
- FR-13.3: Full opt-out: degrade to legally required notices only; owner sees only fact "master disabled assistant," no reasons/details. Equals consent withdrawal (FR-1.5). Tracks CM-2.
- FR-13.4: Principle 4 restated: "communication never stops on the AI's initiative" — only the master can stop it. While consent is active, the floor applies.

**F14 — Configuration, Calibration & Audit**

- FR-14.1: All behavioral parameters config-managed, changeable without release; insert-only versioned; config version in message reproducibility; rollback < 5 min.
- FR-14.2: Every significant decision (profile change, status switch, config change, consent, egress, erasure) in append-only audit log with justification and inputs.
- FR-14.3: Config-seed deliverables at pilot start: scale definitions, barrier matrix, thresholds, archival policy, aggregation rule, bar corridor starting values, progress thresholds, type-divergence delta.

### NonFunctional Requirements

- NFR-A (Determinism): 100% figures deterministic; zero figure-accuracy incidents; every message reproducible from (facts, config_version, prompt_version); status transitions decided in code.
- NFR-B (Compliance & privacy): RU-zone PDn residency; depersonalized-only egress via audited gateway; direct identifiers must not enter prompts even in depersonalized circuit (placeholder names + reverse substitution); art. 12 consent + Roskomnadzor notification as launch gates; append-only audit; PII-scrubbed logs; erasure propagation incl. CRM-mirror tombstones; consent-withdrawal → auto-degrade.
- NFR-C (Reliability & ops): LLM outage → template fallback; degradation ladder with quarterly drills; DR RPO ≤ 15 min / RTO ≤ 4 h with quarterly restore drill; config rollback < 5 min.
- NFR-D (Channel realism): Telegram — no read receipts (engagement answer-based only); quiet hours guaranteed on send side; inline keyboards for screenings (1–5 buttons) and quick replies.
- NFR-E (Scalability & cost): hundreds of masters, few messages/second; LLM cost controls: response length caps, per-master daily token meter, budget-trip fallback.
- NFR-F (Time & geography): static UTC+2..+12 zones; store BOTH salon TZ and master TZ (master defaults to salon, overridable); quiet hours + personal sends in master TZ; pre-visit T-30…60 in salon TZ.
- NFR-G (Security & isolation): inter-salon isolation (row-level multi-tenancy baseline); master-in-two-salons = one psych profile, two work contexts; machine-to-machine keys; secrets in vault; PII-scrubbed logging.
- NFR-H (Explainability): every behavioral decision logged with inputs and justification; config/threshold versions recorded with every change.

### Additional Requirements

*From the architecture spine (ADs, conventions, stack, structural seed) — technical requirements that shape epic/story structure:*

- **Repo scaffold (greenfield starter):** Python 3.12+ modular monolith, source tree `src/domain` (pure: profile, engines, messaging) + `src/adapters` (crm_adapter + fixture, llm, telegram/aiogram, clock, config_store) + `src/app` (FastAPI wiring, webhook) + `src/worker` (scheduler, outbox dispatcher, sync jobs, output validator) + `tests` (unit/contract/golden). (Epic 1 Story 1 basis)
- **AD-1 Pipeline, not agent:** LLM has exactly three bounded roles (narrator, structured-output classifier, bounded dialogue partner); every figure computed by deterministic engine; `RenderFacts` Pydantic model is the bound-variables contract owned by `messaging`; hard enforcement structural via AD-16 output validator + promptfoo golden tests.
- **AD-2 Ports:** domain defines Protocol interfaces — `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore` — implemented by adapters; no external call from domain; import-linter enforced in CI. `LlmPort` is single port — provider swap without domain rework.
- **AD-3 CRM anti-corruption layer + agent calculation DB:** Mentor owns canonical model (Master, Client, Appointment, Visit, CheckLine, VisitComment); adapter translates CRM payloads at boundary; surrogate IDs assigned at ingestion. Sync contract: webhooks + REST polling + nightly reconcile, strictly read-only. Agent calculation DB = replica of needed CRM/Zabot entities + ALL derived values (metric dynamics, plan progress, adaptive bar, recommendation conversion, traffic-light score). CRM/Zabot master of operational data + 2 motivation plan types; agent master of all derived data. Stage 1 = 2 Zabot plan types only; 5-type constructor deferred to backlog.
- **AD-4 Transactional outbox:** every outbound side effect written as outbox row in same transaction as decision; dispatcher sweeps due rows (FOR UPDATE SKIP LOCKED) every 15–30 s; Redis never holds durable state.
- **AD-5 Two-zone residency + placeholder-name egress:** strip step in `llm` adapter with versioned egress allowlist; direct identifiers replaced with internal IDs + placeholder names (Master_A, Client_42); versioned placeholder map; reverse substitution re-binds real names in RU zone after LLM returns; every egress call an audit event; egress contract test; secrets in Yandex Lockbox.
- **AD-6 Insert-only versioned config + prompts:** immutable versioned rows, Pydantic-validated at editing boundary; every message stores (config_version, prompt_version); config-completeness degradation mode. Config includes: 2 Zabot plan types only, bar corridor (±15%/+10%/−15%), progress thresholds (+5%/≥95%), type-divergence delta (+15pts), pause threshold (N=5). Ruble calculation gate: ruble forecasts only if owner entered remuneration rules in agent calc DB.
- **AD-7 Salon-scoped tenancy + psych-layer isolation:** salon key on every domain row; salon-scoped queries; Redis keys salon-prefixed. Psychological layer (scales, tone, correspondence, traffic-light status) inaccessible to owner — enforced at query layer AND owner-facing render boundary. Master-in-two-salons: ONE psych profile (master-level) + TWO work contexts (salon-scoped). Role model extensible for future "salon administrator" role.
- **AD-8 UTC in DB, dual local time at decision point:** timestamptz everywhere; store both salon TZ and master TZ; quiet hours + personal sends in master TZ; pre-visit in salon TZ; both compose (pre-visit salon-TZ window still gated by master-TZ quiet hours).
- **AD-9 Freshness tiers, two clocks, degradation ladder:** every mirror row carries `source_event_at` + `synced_at`; freshness tiers read `synced_at`; `suppress_backdated_events` reads `source_event_at`; Level 1/Level 2 degradation; late-praise exception (within 60 min, no later than end of same shift); absence ≠ staleness (cold-start priors).
- **AD-10 Dispatcher arbitration:** engines publish `TriggerCandidate`; dispatcher enforces caps, disable ladder, pacing (~1 msg/s per chat via Redis token buckets), GROW consent gate, insistence counters, `rendered_by` recording. Quiet hours guaranteed on send side. Inline keyboards for screenings. Communication floor: 1 period-summary + reactive answers. Pause/opt-out owned by `profile`.
- **AD-11 Module boundaries:** one deployable; cross-module calls via published interfaces only; one Postgres schema per module + append-only `audit`; import-linter + schema-ownership CI checks; no microservices/broker/K8s.
- **AD-12 At-least-once idempotency:** `update_id` dedup; outbox and sync upserts idempotent by natural key; surrogate IDs assigned by `crm_sync` at ingestion.
- **AD-13 Canonical master identity:** one `master_id` owned by `profile`; `chat_id ↔ master_id` mapping owned by `profile`; psych profile hangs off `master_id`, work context off (`master_id`, `salon_id`).
- **AD-14 Single-owner state mutation:** traffic light — engines score, `profile` applies hysteresis and owns committed color; dispatcher reads committed color. Consent revocation re-weights traffic-light composite score in `engines` (config-owned rule, profile-owned consent state).
- **AD-15 Erasure propagation:** tombstones in `crm_mirror` surviving snapshot reconciliation; consent #3 revocation triggers scoped erasure (raw correspondence deleted, aggregated profile retained); audit event lists purged schemas/rows.
- **AD-16 Output validator (NEW 23.08):** named validator component on message egress path AFTER LLM re-personalization and BEFORE outbox send. Two checks: (a) figure check — every money-type number byte-equality (after engine rounding) against `RenderFacts` computed value; non-money figures (scores, rankings, cap counts) validated same way; (b) placeholder check — no unreplaced placeholder token remains. On either failing: message NOT sent (hard fail); event audited; deterministic template fallback queued. Owned by `messaging`; runs in RU zone; unit-tested + golden set coverage.
- **AD-17 Consent state model (NEW 23.08):** 4 separate consents owned by `profile` as first-class stateful entity; collected at onboarding BEFORE any profiling question; (2) and (3) independently revocable; withdraw (2) → screenings/tone disabled (traffic light on CRM signals only); withdraw (3) → aggregated-profile-only mode (raw correspondence deleted, aggregated profile retained); withdraw (1) → service deactivated; withdraw (4) → LLM egress blocked, template-only narration. Every profiling and egress decision links to active consent record.
- **Testing strategy:** pytest + pytest-asyncio; contract tests via CRM fixture replay; promptfoo golden set (facts present, no invented numbers, register per type, ethics cases, validator rejects injected wrong numbers).
- **CI/CD:** GitHub private repo + self-hosted RU runner; CI: ruff, mypy, unit/contract/golden, image build, import-linter, schema-ownership check. Deploy: docker compose, 2 VMs (app + worker), Yandex Container Registry.
- **Environments:** prod (webhook mode, RU cloud); dev (aiogram polling + fixture CRM); staging (dedicated test bot). DR: managed backups + PITR.
- **Stack seed:** Python 3.12+, FastAPI, aiogram 3, PostgreSQL 17 (managed Yandex), Redis 8, Sentry + Grafana/Yandex Cloud Monitoring; versions pinned at M0.
- **Observability:** structured JSON PII-scrubbed logs; alerting on user-visible SLOs (per-entity freshness, oldest pending outbox row, LLM-port error rate, quiet-hours defer rate, output-validator fail rate).
- **Milestone mapping (PRD §7):** M0 wks 1–4 (onboarding, consent, config versioning, scheduler + quiet hours, templates, audit, fixture CRM) → M1 wks 5–8 (real CRM sync, freshness SLO, degradation L1; gated OQ-1) → M2 wks 9–14 (traffic light, income/forecast, recommendations, triggers/arbitration/floors, prompt library + LLM port, golden tests, output validator) → M3 wks 15–18 (owner reporting, degradation drills, Roskomnadzor file, pilot).

### UX Design Requirements

No UX design contract exists — Stage 1 is a Telegram bot with no web/native UI (PRD §2.3 non-goals). Chat interaction patterns are specified behaviorally in the PRD (F1–F6) and the addendum's type matrix (A.2) with canonical message examples (BRD Прил. А, referenced as tone registers in A.2). Inline keyboards (1–5 button scale for screenings, quick replies) are the only "widget" — required by NFR-D/AD-10.

### FR Coverage Map

| FR | Epic | Description |
|---|---|---|
| FR-1.1 | Epic 1 | Onboarding + 4 separate consents |
| FR-1.2 | Epic 1 | Primary profiling dialogue |
| FR-1.3 | Epic 1 | CRM history analysis at onboarding (fixture CRM in M0) |
| FR-1.4 | Epic 1 | Working agreements + calibration mode |
| FR-1.5 | Epic 1 | Consent withdrawal (4 consents, revocation, aggregated-profile mode) |
| FR-2.1 | Epic 1 | Profile = motivational type + 9 live scales |
| FR-2.2 | Epic 1 | Dynamic profiling (replies + behavior streams; CRM stream in Epic 2; screening stream in Epic 5) |
| FR-2.3 | Epic 1 | Exponential smoothing (α per-scale config) |
| FR-2.4 | Epic 1 | Type change (+15pts, ≥2 pay periods) |
| FR-2.5 | Epic 1 | Explicit master request (immediate, bypasses smoothing) |
| FR-2.6 | Epic 1 | Type never disclosed as label |
| FR-2.7 | Epic 3 | Progress definition (sliding 2-week window, +5%/≥95% at ≥80% load) |
| FR-2.8 | Epic 1 | Cold start (observation + support mode, introductory bar in period 2) |
| FR-3.1 | Epic 1 | Communication contract (starting values by type) |
| FR-3.2 | Epic 1 | Hard caps + quiet hours (master TZ, guaranteed send-side) |
| FR-3.3 | Epic 4 | Pre-visit recommendations (T-30…60, salon TZ) |
| FR-3.4 | Epic 4 | Message-class disable ladder |
| FR-3.5 | Epic 4 | Ignore detection (≥70% over 2 weeks) |
| FR-3.6 | Epic 4 | Trigger arbitration (highest expected-income-value) |
| FR-4.1 | Epic 4 | Recommendation signal sources |
| FR-4.2 | Epic 4 | Candidates + exclusion filters |
| FR-4.3 | Epic 4 | Ranking by expected value |
| FR-4.4 | Epic 4 | 1–3 recommendations, what/why/how, depth by confidence |
| FR-4.5 | Epic 4 | Zero-survey feedback loop |
| FR-4.6 | Epic 4 | Automatic outcomes update |
| FR-5.1 | Epic 4 | Shift-start message |
| FR-5.2 | Epic 4 | Micro-support (gap + green status) |
| FR-5.3 | Epic 4 | Shift totals (revenue, avg check, progress, forecast, praise) |
| FR-5.4 | Epic 4 | GROW session at period end |
| FR-5.5 | Epic 4 | Forcing (progress + green + GROW consent; proximity sprint) |
| FR-5.6 | Epic 4 | Pace reset (yellow/red, stagnation, life circumstances, post-sprint) |
| FR-5.7 | Epic 4 | Barrier work (MI-style diagnostics, intervention matrix) |
| FR-6.1 | Epic 5 | Signal sources (screenings, tone analysis, CRM signals) |
| FR-6.2 | Epic 5 | Traffic light composite score (code-decided transitions) |
| FR-6.3 | Epic 5 | Hysteresis (entry/exit thresholds, min stay, calibration guidance) |
| FR-6.4 | Epic 5 | Status behavior (green/yellow/red) |
| FR-6.5 | Epic 5 | Ethics of monitoring |
| FR-7.1 | Epic 3 | Goal = Zabot plan (read-only); adaptive bar = internal agent value |
| FR-7.2 | Epic 3 | Goals read from Zabot (2 plan types); no two-way sync; constructor → backlog |
| FR-7.3 | Epic 3 (Story 3.0) | Owner configures agent settings (priorities, stop-list, quiet hours, comm limits, remuneration rules) as versioned config; 2 plan types configured in Zabot |
| FR-7.4 | Epic 3 | Stage 1 = 2 Zabot plan types only; agent computes derived values in calc DB |
| FR-7.5 | Epic 3 | Incomplete plan data → no invented figures |
| FR-7.6 | Epic 3 | Adaptive bar (corridor ±15%/+10%/−15%, movement rules) |
| FR-7.7 | Epic 3 | Income transparency (deterministic calculation; ruble only if remuneration rules) |
| FR-7.8 | Epic 3 | Plan changes apply from next period |
| FR-8.1 | Epic 4 | Trigger catalogue |
| FR-8.2 | Epic 4 | All initiative through caps/arbitration |
| FR-9.1 | Epic 3 | All figures computed deterministically in calc DB; LLM receives bound inputs |
| FR-9.2 | Epic 6 | LLM three roles (narrator, classifier, dialogue partner) |
| FR-9.3 | Epic 6 | LLM outage → template fallback |
| FR-9.4 | Epic 6 | Output validator (figure check + placeholder check, hard fail) |
| FR-9.5 | Epic 3 | Ruble calculation gate |
| FR-10.1 | Epic 7 | Period reports (metrics, plan-attainment, conversion, praise, improvements, aggregates) |
| FR-10.2 | Epic 7 | Out-of-band escalation (red status, systemic anomalies) |
| FR-10.3 | Epic 7 | Confidentiality (aggregate-only, no quotes, enforceable boundary) |
| FR-11.1 | Epic 2 | Data via Zabot CRM (visit history, sales, schedule, bookings, checks, dynamics, cancellations) |
| FR-11.2 | Epic 2 | Freshness thresholds (checks ≤60min, schedule ≤15min, dynamics ≤24h) |
| FR-11.3 | Epic 2 | Degradation ladder (Level 1, Level 2, recovery, late-praise exception) |
| FR-11.4 | Epic 2 | Cold start priors |
| FR-11.5 | Epic 2 | Sync mechanism (webhooks + polling + nightly reconcile, read-only) |
| FR-12.1 | Epic 6 | Long-term + short-term memory |
| FR-12.2 | Epic 6 | Fresh signals outweigh old; archival |
| FR-12.3 | Epic 6 | Memory for help, never pressure |
| FR-13.1 | Epic 1 | Communication floor (1 period-summary + reactive) |
| FR-13.2 | Epic 1 | Pause/vacation mode (automatic + manual) |
| FR-13.3 | Epic 1 | Full opt-out (degrade to legally required notices) |
| FR-13.4 | Epic 1 | Principle 4 restated (communication never stops on AI's initiative) |
| FR-14.1 | Epic 1 | Config versioning (insert-only, rollback <5min) |
| FR-14.2 | Epic 1 | Audit log (append-only) |
| FR-14.3 | Epic 7 | Config-seed deliverables (full set at pilot) |

### NFR Coverage Map

| NFR | Epic(s) | Description |
|---|---|---|
| NFR-A (Determinism) | Epic 3, Epic 6 | All figures computed by deterministic engine (3.4); output validator hard-enforces (6.3); status transitions in code (5.3); `(config_version, prompt_version)` reproducibility (1.6, 1.7, 6.1) |
| NFR-B (Compliance & privacy) | Epic 1, Epic 6, Epic 7 | 4-consent model + revocation (1.3); depersonalization strip + placeholder egress (6.2); erasure propagation + tombstones (7.4); Roskomnadzor file (7.5); PII-scrubbed logging (1.1 audit schema) |
| NFR-C (Reliability & ops) | Epic 6, Epic 7, Epic 2 | LLM outage → template fallback (6.4); degradation ladder L1/L2 (2.4); DR drills RPO/RTO (7.5); config rollback <5min (1.1, 7.5) |
| NFR-D (Channel realism) | Epic 1, Epic 4 | Quiet hours guaranteed send-side (1.6); inline keyboards for screenings (5.1); pre-visit T-30…60 salon TZ (4.3); no read receipts (engagement answer-based, 4.9 ignore detection) |
| NFR-E (Scalability & cost) | Epic 6, Epic 1 | LLM cost controls: length caps, per-master daily token meter, budget-trip fallback (6.1); per-chat Redis token buckets (1.6); hundreds of masters, few msg/s |
| NFR-F (Time & geography) | Epic 1, Epic 4 | Dual TZ storage salon+master (1.6); quiet hours + personal sends in master TZ (1.6); pre-visit in salon TZ composed with master quiet hours (4.3) |
| NFR-G (Security & isolation) | Epic 1, Epic 2, Epic 7 | Salon-scoped tenancy, salon key on every row (1.2, 2.3); psych-layer inaccessible to owner (7.1, 7.3); secrets in Yandex Lockbox (6.2); schema-ownership CI (1.1, 2.3) |
| NFR-H (Explainability) | Epic 1, Epic 5 | Append-only audit log with justification+inputs (1.1); config/threshold versions recorded (1.1); traffic-light score+transition logged (5.3) |

## Epic List

### Epic 1: Onboarding, Consent & Foundation (M0)
A master can start the bot, grant 4 separate consents, complete primary profiling, and receive their first calibration-mode template messages — all on a fixture CRM with zero external dependencies. Includes repo scaffold, ports, config versioning, audit, Telegram wiring, 4-consent model (AD-17), profiling, communication contract, scheduler + quiet hours (master TZ), template messages, fixture CRM, cold start, and communication floor/pause/opt-out.
**FRs covered:** FR-1.1–1.5, FR-2.1–2.6, FR-2.8, FR-3.1–3.2, FR-13.1–13.4, FR-14.1–14.2

### Epic 2: CRM Integration & Agent Calculation DB (M1)
The agent is grounded in real Zabot/CRM data — the agent calculation DB replicates needed CRM entities and all derived values are computed from actual data, with freshness tiers and degradation handling. Gated on OQ-1 (Zabot API verification).
**FRs covered:** FR-11.1–11.5

### Epic 3: Deterministic Calculation Engine & Plan Tracking (M2 — NEW, replaces constructor)
The agent reads the 2 Zabot plan types (avg-check, total-revenue), computes all derived values deterministically (progress, pace, forecast, adaptive bar, decomposition), and the master can ask income/plan/what-if questions and get deterministic answers — with the ruble calculation gate enforcing no salary math unless owner entered remuneration rules. No scheme constructor, no tiers, no rule engine.
**FRs covered:** FR-7.1–7.8, FR-9.1, FR-9.5, FR-2.7

> **Stories:** 3.0 (agent-settings config), 3.1 (read Zabot plans), 3.2 (progress tracking), 3.3 (adaptive bar), 3.4a/3.4b/3.4c (calc engine split), 3.5 (income transparency + intent router), 3.6 (ruble gate), 3.7 (plan change handling).

### Epic 4: Personalized Coaching & Recommendations (M2)
The master receives adaptive coaching across shift/week/period cycles — shift-start messages, pre-visit recommendations, micro-support, shift totals with deterministic forecasts, GROW sessions, barrier work — with proactive triggers arbitrated through caps and the GROW consent gate.
**FRs covered:** FR-4.1–4.6, FR-5.1–5.7, FR-3.3–3.6, FR-8.1–8.2

### Epic 5: Emotional Monitoring & Traffic Light (M2)
The system monitors the master's emotional state through screenings, tone analysis, and CRM signals, and adjusts behavior via the traffic light with hysteresis — reducing frequency and forbidding forcing on yellow, support-only on red.
**FRs covered:** FR-6.1–6.5

### Epic 6: LLM Narration, Depersonalization & Output Validation (M2)
The LLM narrates pre-computed facts in psychotype-calibrated prose through a depersonalization gateway with placeholder names, and the output validator hard-enforces that every money-type number matches the computed value — a message that fails validation is never sent.
**FRs covered:** FR-9.2–9.4, FR-12.1–12.3

### Epic 7: Owner Reporting & Pilot Readiness (M3)
The owner receives per-period reports per master with aggregate-only confidentiality (no correspondence quotes), red-status escalations, and the system is ready for pilot with degradation drills, erasure propagation, and the Roskomnadzor notification file.
**FRs covered:** FR-10.1–10.3, FR-14.3

---

## Epic 1: Onboarding, Consent & Foundation (M0)

A master can start the bot, grant 4 separate consents, complete primary profiling, and receive their first calibration-mode template messages — all on a fixture CRM with zero external dependencies. Includes repo scaffold, ports, config versioning, audit, Telegram wiring, 4-consent model (AD-17), profiling, communication contract, scheduler + quiet hours (master TZ), template messages, fixture CRM, cold start, and communication floor/pause/opt-out.

### Story 1.1a: Repo Scaffold, Ports & Module Boundaries

As a developer,
I want a running modular monolith scaffold with ports and import-linter enforcement,
So that subsequent stories build on a clean architecture-compliant foundation.

**Acceptance Criteria:**

**Given** a clean repository
**When** the scaffold is created
**Then** the source tree follows `src/domain` (profile, engines, messaging) + `src/adapters` (crm_adapter + fixture, llm, telegram, clock, config_store) + `src/app` (FastAPI) + `src/worker` + `tests` (unit/contract/golden)
**And** Protocol interfaces are defined: `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore`
**And** import-linter forbids framework/adapter imports from `domain/` and is enforced in CI
**And** Python 3.12+, FastAPI, aiogram 3, PostgreSQL 17, Redis 8 versions are pinned in dependency files

### Story 1.1b: Versioned Config Store & Audit Log

As a developer,
I want an insert-only versioned config store and an append-only audit log,
So that every behavioral parameter is reproducible and every decision is traceable.

**Acceptance Criteria:**

**Given** the scaffold from 1.1a exists
**When** the config and audit foundations are implemented
**Then** insert-only versioned config store is implemented (Pydantic-validated at editing boundary, AD-6)
**And** append-only audit log schema exists (`audit` schema, AD-11)
**And** config rows are immutable after insert; edits create new versioned rows
**And** audit rows carry justification + inputs (FR-14.2)
**And** schema-ownership CI check enforces no cross-module table access

### Story 1.1c: CI Pipeline & Docker Compose Dev Environment

As a developer,
I want CI and a runnable dev environment,
So that merges are gated and local development is reproducible.

**Acceptance Criteria:**

**Given** the scaffold from 1.1a and config/audit from 1.1b exist
**When** CI and dev environment are configured
**Then** CI runs ruff, mypy, unit tests, import-linter, schema-ownership check
**And** docker compose dev environment runs and health check endpoint responds
**And** CI blocks merges on any failure

### Story 1.2: Telegram Bot Wiring & /start Command

As a master,
I want to start the bot via a deep link and see a welcome message,
So that I can begin onboarding.

**Acceptance Criteria:**

**Given** a master receives a Telegram deep link
**When** the master sends `/start` to the bot
**Then** the bot responds with a welcome message identifying the salon
**And** a canonical `master_id` is created in the `profile` module
**And** the `chat_id ↔ master_id` mapping is stored (owned by `profile`, AD-13)
**And** a salon-scoped work context row is created (`master_id`, `salon_id`)
**And** the salon key is on every created domain row (AD-7)
**And** webhook mode works in prod, polling mode works in dev
**And** `update_id` dedup is implemented (AD-12)

### Story 1.3: 4-Consent Capture at Onboarding

As a master,
I want to grant 4 separate consents before any profiling,
So that I control what data the AI processes about me.

**Acceptance Criteria:**

**Given** a master has started the bot
**When** the onboarding flow begins
**Then** 4 separate consents are presented BEFORE any profiling question: (1) PDn processing + profiling; (2) emotional-state data processing; (3) correspondence history retention; (4) cross-border transfer of depersonalized data to LLM provider
**And** each consent is captured independently via inline keyboard buttons
**And** consent state is owned by `profile` as a first-class stateful entity (AD-17)
**And** without consent (1) the service is not activated
**And** consent grant events are recorded in the audit log with fact + date
**And** consents (2) and (3) are independently revocable via a bot command
**And** withdrawing (2) disables screenings and tone analysis
**And** withdrawing (3) switches memory to aggregated-profile-only mode (raw correspondence deleted, aggregated profile retained)
**And** withdrawing (1) deactivates the service entirely
**And** withdrawing (4) blocks LLM egress (template-only narration)
**And** every profiling and egress decision links to an active consent record

> **Erasure ownership:** Consent state is owned by `profile` (AD-17). The actual erasure execution on consent (3) withdrawal — raw correspondence purge, `crm_mirror` tombstones, audit event — is delegated to the cross-module erasure-propagation story (Story 7.4, AD-15), which `profile` orchestrates. Stories 1.3, 6.6 reference 7.4 as the single erasure entry point; they do not implement erasure themselves.

### Story 1.4: Primary Profiling Dialogue

As a master,
I want to complete a profiling dialogue,
So that the AI understands my motivational type and preferences.

**Acceptance Criteria:**

**Given** a master has granted all 4 consents
**When** the master begins primary profiling
**Then** a live dialogue runs one question at a time with reactions to answers (duration is not fixed; the dialogue completes when all mandatory questions are answered)
**And** the dialogue determines starting motivational type (1 of 5 archetypes, Addendum A.2) via a config-defined mapping from questionnaire answers to archetype scores [уточнить: OQ-12 — scoring algorithm]
**And** the dialogue determines starting scale values (9 scales 0-100, Addendum A.3)
**And** the dialogue determines preferred tone/frequency and personal quiet hours
**And** mandatory questions from Addendum A.4 are all asked
**And** CRM history analysis runs at onboarding (from fixture CRM in M0) producing a starting-scale prior and an observation-mode flag — NOT a starting bar (the bar is first set in Epic 3, Story 3.3 from period-1 actuals per FR-2.8)
**And** the AI states working agreements at the end and obtains the master's confirmation
**And** the first 2 weeks are set to calibration mode with elevated format-feedback requests
**And** the motivational type is never disclosed to the master as a label (FR-2.6)

### Story 1.5: Master Profile State & Dynamic Profiling

As the AI system,
I want to maintain and update the master's profile (type + 9 scales) from signal streams,
So that coaching adapts to the master's evolving state.

**Acceptance Criteria:**

**Given** a master has completed primary profiling
**When** the master interacts with the bot (replies, behavior signals)
**Then** the 9 live scales (0-100) are updated via exponential smoothing with per-scale α config (fast 0.3-0.5, slow 0.1-0.2)
**And** scale values and versions are logged
**And** the system continuously scores how well the master fits each of the 5 types
**And** a type change occurs only when an alternative type scores +15 points higher for ≥2 consecutive pay periods
**And** the type change is logged with justification and the master is never told "your label changed"
**And** an explicit master request ("пиши короче", "без эмодзи", "не пиши до 10:00") applies immediately, bypassing smoothing, and is logged as "manual setting"
**And** the master can ask how the system sees them and gets a soft descriptive answer (not a label)
**And** dynamic profiling processes master replies and behavior streams (answered/ignored by message class)
**And** CRM results and state screening streams are prepared for integration in later epics

### Story 1.6: Communication Contract, Caps & Quiet Hours

As a master,
I want the AI to respect my communication contract (frequency, tone, quiet hours),
So that messages are helpful, not intrusive.

**Acceptance Criteria:**

**Given** a master has completed profiling
**When** the communication contract is established
**Then** a per-master contract is stored: touch frequency, message length, tone, challenge/support ratio, number format, send times
**And** starting values are set by motivational type (Addendum A.2)
**And** hard caps are enforced: ≤5 initiative messages per shift, ≤2 on days off, lower on yellow/red
**And** quiet hours default 21:00-9:00 master TZ and are guaranteed on the send side (the service does not send in the interval)
**And** quiet hours are configurable by owner and master
**And** both salon TZ and master TZ are stored (master defaults to salon, overridable)
**And** the scheduler evaluates quiet hours at send-decision time (not baked into job fire time)
**And** the scheduler uses the outbox pattern (AD-4) with dispatcher sweeping due rows every 15-30 s
**And** Telegram pacing (~1 msg/s per chat) is enforced via per-chat_id Redis token buckets

### Story 1.7: Template Messages (Shift-Start & Minimal Shift Totals)

As a master,
I want to receive shift-start and a minimal end-of-shift message,
So that I know my day plan and basic results.

**Acceptance Criteria:**

**Given** a master has a shift scheduled (from fixture CRM)
**When** the shift starts
**Then** a shift-start message is sent with: short day plan (clients scheduled from fixture CRM), one day focus, motivational message in psychotype tone
**And** the message is rendered from a deterministic template (`rendered_by: template`)
**When** the shift ends
**Then** a minimal shift-totals message is sent with: revenue and avg check (fixture-derived only)
**And** one specific praise for one specific action (fixture-derived)
**And** all figures in the message are computed deterministically (no LLM)
**And** the outbox row stores `(config_version, prompt_version)` for reproducibility
**And** a basic figure assertion validates template numbers before send
**And** bad-day reactions follow the type matrix (no hot debrief for sensitive types)

> **Scope note (M0 boundary):** Recommendation outcomes, progress toward bar, and deterministic income forecast are deferred to Story 4.5 (M2) — they depend on the recommendation engine (Epic 4) and calculation engine (Epic 3), which do not exist in M0. Story 1.7 ships only fixture-derived revenue/avg-check + praise.

### Story 1.8: Communication Floor, Pause & Opt-out

As a master,
I want to pause communication or opt out entirely,
So that I control my engagement with the AI.

**Acceptance Criteria:**

**Given** a master wants to reduce or stop communication
**When** the master requests a pause
**Then** automatic pause activates when no shifts are scheduled for ≥5 days (config-defined N)
**And** manual pause is available ("I'm on vacation until...")
**And** during a pause: silence except reactive answers to incoming questions
**And** goals/bar logic accounts for the pause period
**When** the master requests full opt-out
**Then** the service degrades to legally required notices only
**And** the owner sees only the fact "master disabled the assistant" — no reasons, no details
**And** full opt-out equals consent (1) withdrawal (FR-1.5)
**And** the minimum floor is always available while consent is active: 1 period-summary message + reactive answers to incoming
**And** pre-visit recommendations are disabled last and only on explicit master request
**And** pause/opt-out state is owned by `profile` and audited
**And** the system tracks CM-2 (full opt-out / consent-withdrawal rate)

### Story 1.9: Cold Start & Incomplete Profiling Handling

As a new master with no CRM history,
I want the AI to start in observation mode,
So that I get support without unrealistic expectations.

**Acceptance Criteria:**

**Given** a master with no CRM history (new employee)
**When** onboarding completes
**Then** the first pay period runs in observation + support mode: no bar, no income forecast
**And** onboarding, introductions, and pre-visit recommendations work from day one (built on client history, not master history)
**And** the bar is first set in period 2 from period-1 actuals — an "introductory" bar, deliberately attainable
**Given** a master who did not complete primary profiling
**When** the profiling dialogue is incomplete
**Then** a default max-caution profile activates (low frequency, soft tone, no challenges — "Cautious" type settings)
**And** missing answers are gathered one question at a time during natural dialogue pauses over 1-2 weeks

### Story 1.10: Fixture CRM & Contract Tests

As a developer,
I want a fixture CRM with recorded payloads,
So that I can develop and test without the real Zabot API.

**Acceptance Criteria:**

**Given** the fixture CRM is configured
**When** the system reads CRM data through `CrmPort`
**Then** recorded payloads are served behind `CrmPort` (doubles as contract-test suite)
**And** the canonical model is implemented: `Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment`
**And** surrogate IDs are assigned at first ingestion and published as part of the `crm_sync` interface
**And** downstream modules reference only surrogate IDs
**And** the adapter translates CRM payloads (names, enums, timezones, money formats) at the boundary
**And** contract tests replay fixture payloads and assert correct canonical model projection
**And** M0 is fully unblocked with no real Zabot API dependency

---

## Epic 2: CRM Integration & Agent Calculation DB (M1)

The agent is grounded in real Zabot/CRM data — the agent calculation DB replicates needed CRM entities and all derived values are computed from actual data, with freshness tiers and degradation handling. Gated on OQ-1 (Zabot API verification).

### Story 2.1: CRM Sync — Webhook Ingest

As the system,
I want to receive Zabot webhooks for booking/check/cancellation events,
So that the agent calculation DB stays current with real CRM data.

**Acceptance Criteria:**

**Given** a Zabot webhook endpoint is configured (unverified — pending OQ-1)
**When** a webhook event arrives (booking created/changed, visit/check closed, cancellation)
**Then** the event is ingested into the `crm_mirror` schema
**And** CRM payloads are translated at the boundary (names, enums, timezones, money formats)
**And** surrogate IDs are assigned at first ingestion; re-keyed source rows map to the same surrogate
**And** the natural-key mapping is published as part of the `crm_sync` interface
**And** ingestion is idempotent by natural key (AD-12)
**And** the sync run is recorded as an audit event
**And** direction is strictly one-way: CRM/Zabot → agent, read-only (no writes to Zabot)

### Story 2.2: CRM Sync — REST Polling & Nightly Reconcile

As the system,
I want to poll Zabot REST API for entities without webhooks and run nightly full reconciliation,
So that no CRM events are missed.

**Acceptance Criteria:**

**Given** some CRM entities lack webhook support
**When** the REST polling job runs
**Then** entities without webhooks are polled via Zabot REST API
**And** polled data is upserted into `crm_mirror` idempotently by natural key
**When** the nightly full reconcile runs
**Then** all CRM entities are reconciled against the mirror
**And** missed events are healed
**And** the reconcile is idempotent by natural key
**And** reconcile runs are recorded as audit events
**And** the `CrmPort` interface abstracts the sync mechanism from the domain

### Story 2.3: Agent Calculation DB Schema

As the system,
I want a calculation DB that replicates needed CRM/Zabot entities and stores all derived values,
So that engines compute over a consistent, owned data set.

**Acceptance Criteria:**

**Given** the agent calculation DB is initialized
**When** the schema is created
**Then** the `crm_mirror` schema stores replicated CRM entities (Master, Client, Appointment, Visit, CheckLine, VisitComment)
**And** every mirror row carries two timestamps: `source_event_at` (CRM-side truth) and `synced_at` (mentor-side fetch)
**And** the `engines` schema stores derived values (metric dynamics, plan progress, adaptive bar, recommendation conversion, traffic-light score)
**And** the `profile` schema stores master identity, psych profile, consent state, scales, traffic-light committed state, pause/opt-out state
**And** the `messaging` schema stores outbox, message log
**And** the `config` schema stores versioned config + prompts
**And** the `audit` schema is append-only
**And** one Postgres schema per module + append-only `audit` (AD-11)
**And** schema-ownership CI check enforces no cross-module table access
**And** CRM/Zabot is master of operational data + 2 motivation plan types; agent is master of all derived data (AD-3)

### Story 2.4: Freshness Tiers & Two-Clock Degradation Ladder

As the system,
I want freshness tiers and a degradation ladder,
So that messages reflect data recency honestly and degrade gracefully when CRM is stale.

**Acceptance Criteria:**

**Given** CRM data is synced into the mirror
**When** an engine reads mirror data
**Then** freshness is evaluated by reading `synced_at` against tier thresholds: checks/sales ≤60min, schedule/bookings ≤15min, dynamics/period totals ≤24h
**And** `suppress_backdated_events` reads `source_event_at` to prevent retroactive event messages
**When** data is Level 1 stale (older than tier, younger than hard limit: checks 24h, schedule end-of-day)
**Then** data is used with a visible timestamp label ("по данным на 14:30") and monetary forecasts are suppressed
**When** data is Level 2 stale (older than hard limit or CRM down)
**Then** communication continues without figures: support, coaching, profile/history-based recommendations; money math, visit-specific praise, and forecasts are suspended; the AI tells the master honestly
**When** CRM recovers
**Then** data is resynced, totals recomputed on actuals; missed event messages are never sent retroactively
**And** the late-praise exception applies: praise for a successful recommendation may be sent late, within 60 min but no later than the end of the same shift
**And** absence ≠ staleness: cold-start priors are used for new entities, never blocking onboarding
**And** alerting fires on per-entity freshness SLO violations

### Story 2.5: Cold Start Priors for CRM Entities

As the system,
I want config-defined conservative priors for new masters/salons/clients,
So that onboarding and basic operation are never blocked by data sparsity.

**Acceptance Criteria:**

**Given** a new master, new salon, or new client with no CRM history
**When** the system encounters data sparsity
**Then** config-defined conservative priors are applied per entity type
**And** category/seasonality priors are applied for new clients
**And** onboarding and basic operation are never blocked
**And** for a new master specifically: observation + support mode in period 1, first bar in period 2 (integrates with FR-2.8)
**And** priors are config-versioned and logged

### Story 2.6: CRM-Results Signal Stream for Dynamic Profiling

As the system,
I want CRM-derived results to feed the master's dynamic profile,
So that profiling reflects actual performance, not just chat behavior.

**Acceptance Criteria:**

**Given** CRM data is synced into the mirror (Stories 2.1–2.2) and the master has a profile (Story 1.5)
**When** the dynamic profiling engine updates the master's scales
**Then** CRM-results signals feed the third signal stream for FR-2.2: recommendation conversion by type, output drop at same booking level, attainment vs plan, cancellation rate
**And** each CRM signal is normalized to a 0–100 scale contribution with a config-defined weight
**And** scales are updated via the same exponential-smoothing path as the other streams (Story 1.5, per-scale α config)
**And** CRM signals are computed deterministically by `engines` over the agent calc DB — no LLM in the signal path
**And** the stream is suppressed when CRM data is Level 2 stale (AD-9) — stale CRM does not move scales
**And** signal updates are logged with inputs and config version

---

## Epic 3: Deterministic Calculation Engine & Plan Tracking (M2 — NEW, replaces constructor)

The agent reads the 2 Zabot plan types (avg-check, total-revenue), computes all derived values deterministically (progress, pace, forecast, adaptive bar, decomposition), and the master can ask income/plan/what-if questions and get deterministic answers — with the ruble calculation gate enforcing no salary math unless owner entered remuneration rules. No scheme constructor, no tiers, no rule engine.

### Story 3.0: Owner Agent-Settings Configuration Surface

As an owner,
I want to configure agent-owned settings (priorities, stop-list, quiet hours defaults, communication limits, remuneration rules),
So that the agent's behavior reflects my salon's parameters without writing to Zabot.

**Acceptance Criteria:**

**Given** an owner wants to configure agent behavior
**When** the owner edits agent settings
**Then** the following are configurable and stored as **versioned config** (AD-6, insert-only, Pydantic-validated at editing boundary): priority services & goods, stop-list, default quiet hours, communication limits, and optionally remuneration rules (rates, percentages) for ruble income calculations (FR-9.5)
**And** remuneration rules are config — NOT calc-DB operational data — so they are versioned, rollback-able, and audited as config changes (FR-14.1)
**And** the 2 Zabot plan types themselves are NOT configured here — they are read from Zabot (Story 3.1); this surface is for agent-owned parameters only (FR-7.3)
**And** pay period is read from Zabot, not configured here
**And** every edit creates a new config version row; the active version is resolved at decision time
**And** config changes are audited with justification + inputs (FR-14.2)
**And** config rollback < 5 min is preserved (FR-14.1)
**And** the ruble calculation gate (Story 3.6) reads remuneration-rule presence from the active config version

### Story 3.1: Read Zabot Plans (2 Types)

As the system,
I want to read the 2 Zabot plan types (avg-check, total-revenue) from the CRM mirror,
So that the agent knows each master's goals without writing to Zabot.

**Acceptance Criteria:**

**Given** the CRM mirror contains Zabot plan data
**When** the agent reads plans for a master
**Then** two plan types are supported: plan by master's average check and plan by total revenue
**And** plans are read-only — the agent never writes to Zabot (AD-3)
**And** the pay period (week / two weeks / month) is read from Zabot
**And** plan data is replicated into the agent calculation DB (`crm_mirror` schema)
**And** CRM/Zabot is master of plan data; the agent is master of all derived data
**And** the 5-type scheme constructor is NOT implemented (deferred to backlog)
**When** plan data is incomplete
**Then** the AI invents no income figures — metrics only + clarification request to owner (config-completeness degradation, FR-7.5)
**And** the goal (Zabot plan) is never changed by the AI; the adaptive bar is an internal agent value (FR-7.1)

### Story 3.2: Progress Tracking (Sliding 2-Week Window)

As the system,
I want to compute the master's progress toward the plan using a sliding 2-week window,
So that bar raises and coaching decisions are grounded in actual performance.

**Acceptance Criteria:**

**Given** a master has CRM data for at least 2 weeks
**When** the progress engine computes progress
**Then** progress is defined as: key bar metric growth ≥ +5% vs the previous 2-week window OR bar retention ≥ 95% throughout the window
**And** progress is only counted at load ≥ 80% of the master's typical load — "typical" defined as the rolling 4-week median of scheduled-shift load for that master (config-defined window)
**And** both thresholds (+5% and ≥95%) and the load threshold (≥80%) are config-defined
**And** the sliding 2-week window is computed in salon TZ (shifts are salon-scheduled)
**And** progress values are stored in the `engines` schema and logged with inputs
**And** progress gates bar raises (FR-5.5) and is consumed by coaching cycles (Epic 4)

### Story 3.3: Adaptive Bar Calculation (Corridor Rules)

As the system,
I want to compute and adjust the adaptive bar within corridor rules,
So that the master has a difficult-but-attainable individual trajectory toward the Zabot plan.

**Acceptance Criteria:**

**Given** a master has actual performance dynamics in the calculation DB
**When** the adaptive bar engine computes the calculated bar
**Then** the calculated bar is a forecast from the master's actual dynamics in "difficult-but-attainable" logic (~60-70% attainment probability [уточнить: OQ-10 — attainment-probability estimation method is unresolved; until resolved, use a config-defined naive forecast (e.g., last-period actual × (1 + growth_factor)) with the corridor rules below])
**And** the allowable deviation of the adaptive bar from the calculated bar is ±15% (config-defined)
**And** the raise step is ≤ +10% per period (config-defined)
**And** tactical lowering on yellow/red status is not below −15% of the calculated bar and not below the master's actual average over the last 2 periods
**And** the bar cannot exceed the Zabot plan
**When** the Zabot plan is below the master's actual level
**Then** the agent holds the master at their actual level and reports to the owner in the period report that the plan needs revision
**And** movement rules: raise only on sustained progress (FR-2.7) + master's consent; stagnation — hold + diagnose; decline — never raised
**And** the bar is never framed as punishment; always in income/metric terms
**And** the bar is stored in the `engines` schema (agent calc DB master, AD-3)
**And** the bar is accepted by the master in GROW (Epic 4, Story 4.6)

### Story 3.4a: Metric Dynamics & Plan Progress Computation

As the system,
I want deterministic computation of metric dynamics and plan progress,
So that progress figures are never generated by the LLM.

**Acceptance Criteria:**

**Given** the agent calculation DB has CRM data and plan data
**When** the calculation engine computes metric dynamics and plan progress
**Then** metric dynamics (revenue, avg check, conversion by type) are computed deterministically by `engines` over the calc DB
**And** plan progress (vs the 2 Zabot plan types, sliding 2-week window per Story 3.2) is computed deterministically
**And** engines read config by version at decision time (compute and send never span versions)
**And** engines are pure compute — no side effects
**And** CRM/Zabot is master of operational data + plans; agent is master of all derived data — conflict excluded by construction (AD-3)

### Story 3.4b: Decomposition & Attainment Forecast

As the system,
I want deterministic decomposition and attainment forecast,
So that "how much per visit/shift to reach plan" and forecast figures are never generated by the LLM.

**Acceptance Criteria:**

**Given** metric dynamics and plan progress from 3.4a
**When** the calculation engine computes decomposition and forecast
**Then** decomposition ("how much per visit/shift to reach plan") is computed deterministically
**And** attainment forecast (projected plan attainment by period end) is computed deterministically
**And** forecasts are suppressed when data is Level 1 stale (AD-9)
**And** engines are pure compute — no side effects
**And** all values are stored in the `engines` schema with config version

### Story 3.4c: RenderFacts Binding Contract

As the system,
I want a Pydantic `RenderFacts` model that carries pre-computed bound values to the LLM,
So that the LLM receives computed values as bound inputs and is forbidden from generating figures.

**Acceptance Criteria:**

**Given** computed figures from 3.4a and 3.4b
**When** the `RenderFacts` Pydantic model is assembled
**Then** `RenderFacts` (owned by `messaging`) carries ALL pre-computed bound values: income, forecasts, bar values, plan progress, scores, rankings, cap counts
**And** the LLM receives `RenderFacts` as bound inputs and is forbidden from generating, estimating, or rounding any figure (FR-9.1)
**And** rounding is done ONLY by the engine before passing to `RenderFacts` (the output validator, Story 6.3, checks byte-equality against these rounded values)
**And** `RenderFacts` is the single bound-variables contract between `engines` and `messaging` (AD-1)
**And** hard enforcement is structural via the output validator (AD-16, implemented in Epic 6, Story 6.3)

### Story 3.5: Income Transparency (Master Questions)

As a master,
I want to ask "how much have I earned?", "how far to the plan?", "what would +2 goods/day give me?" and get deterministic answers,
So that I see the action→money link.

**Acceptance Criteria:**

**Given** a master asks an income/plan/what-if question in chat
**When** the system processes the question
**Then** a deterministic (non-LLM) intent router in `messaging` classifies the message as an income/plan/what-if question — this does NOT add a 4th LLM role (FR-9.2 remains exactly three roles: narrator, classifier, dialogue partner)
**And** the intent router is keyword/rule-based, config-defined, and versioned (AD-6)
**And** the answer is computed by the deterministic calculation engine (not the LLM)
**And** ruble income figures appear ONLY if the owner has entered remuneration rules in agent settings (FR-9.5, Story 3.6)
**When** remuneration rules are NOT configured
**Then** the agent works in metric and plan-progress terms ("240 ₽/visit left to the avg-check plan" — plan-relative, not salary)
**When** remuneration rules ARE configured
**Then** the agent computes ruble income by those rules and labels the result as a service estimate, not Zabot data
**And** the answer is rendered as `RenderFacts` (template or LLM narration from Epic 6)
**And** the visible action→money link is the system's primary motivational mechanism

### Story 3.6: Ruble Calculation Gate

As the system,
I want a gate that prevents ruble salary calculations unless the owner has entered remuneration rules,
So that the agent never invents income figures.

**Acceptance Criteria:**

**Given** the agent is asked to compute ruble income
**When** remuneration parameters (rates, percentages) are not present in the active config version (Story 3.0)
**Then** the agent does NOT compute salary in rubles
**And** the agent works in metrics and plan-progress terms only
**When** the owner has entered remuneration rules via the agent-settings surface (Story 3.0, stored as versioned config per AD-6)
**Then** ruble income forecasts are enabled
**And** the agent computes by those rules and explicitly labels the result as a service estimate, not Zabot data
**And** remuneration rules are config (insert-only versioned), NOT calc-DB operational data — so they are rollback-able and audited as config changes
**And** the gate reads remuneration-rule presence from the active config version at decision time (compute and send never span versions)
**And** the gate state is audited

### Story 3.7: Plan Change Handling

As a master,
I want the AI to explain what changed in my plan when the owner updates it,
So that I understand the impact on my progress.

**Acceptance Criteria:**

**Given** the owner changes a plan in Zabot
**When** the CRM sync detects the plan change in the mirror
**Then** the change applies from the next pay period (not retroactively to the current period)
**And** the AI explains to the master what changed in their plan/progress
**And** the explanation is rendered as `RenderFacts` (template or LLM narration from Epic 6)
**And** the plan change is audited
**And** the adaptive bar is recalculated for the next period based on the new plan

---

## Epic 4: Personalized Coaching & Recommendations (M2)

The master receives adaptive coaching across shift/week/period cycles — shift-start messages, pre-visit recommendations, micro-support, shift totals with deterministic forecasts, GROW sessions, barrier work — with proactive triggers arbitrated through caps and the GROW consent gate.

### Story 4.1: Recommendation Engine (Candidates, Filters, Ranking)

As a master,
I want to receive 1-3 personalized recommendations per client visit,
So that I know what to offer and how.

**Acceptance Criteria:**

**Given** a client visit is scheduled
**When** the recommendation engine generates recommendations
**Then** signal sources are used: full client visit history, product purchase cycles, service cyclicity/gaps, seasonality, visit comments, owner priorities, past refusals
**And** candidates = owner priority positions ∪ history-logical positions (repeat purchase, cross-sell, up-sell)
**And** exclusion filters apply: ≥2 consecutive client refusals → N-month pause; contraindications/allergies from comments; owner stop-list; incompatibility with booked service
**And** ranking is by expected value: acceptance probability (client history + master statistics) × margin/priority [уточнить: OQ-13 — acceptance-probability model is unspecified; until resolved, use a config-defined baseline (e.g., client historical acceptance rate for the recommendation type, smoothed with a prior)]
**And** 1-3 recommendations per visit are generated (fewer is better; one confident offer, not a menu)
**And** format is what/why/how: the item, history-based justification, ready phrase adapted to master's psychotype and client context
**And** depth depends on sales-confidence scale: full script for novices, thesis for veterans
**And** the recommendation is stored in the `engines` schema with provenance

### Story 4.2: Zero-Survey Feedback Loop & Outcome Reconciliation

As the system,
I want to reconcile recommendation outcomes from check contents without asking the master,
So that the engine learns without interrogation.

**Acceptance Criteria:**

**Given** a recommendation was issued for a client visit
**When** the visit check is closed in CRM
**Then** the outcome is reconciled from check contents only (never asking the master whether they offered)
**And** non-conversion does not distinguish "didn't offer" from "client refused" — the system does not interrogate
**And** automatic outcomes update: client profile (accepts / consistently declines), master profile (conversion by recommendation type), engine quality (which recommendations work for this master)
**And** reconciliation is idempotent per visit (AD-12)
**And** the BRD §8.4 ban applies only to reporting/control surveys; care-oriented mood check-ins are permitted (F6)

### Story 4.3: Pre-Visit Recommendations (T-30…60, Salon TZ)

As a master,
I want to receive recommendations 30-60 minutes before a client visit,
So that I have time to prepare.

**Acceptance Criteria:**

**Given** a client visit is scheduled
**When** the pre-visit window opens (T-30…60 min before appointment)
**Then** the recommendation message is scheduled via the outbox
**And** the pre-visit target window is evaluated in salon TZ (where the visit physically occurs)
**And** the send decision is gated by master-TZ quiet hours (AD-8 composition: a pre-visit whose salon-TZ window falls inside master quiet hours is deferred to the next master-TZ window)
**And** pre-visit recommendations are the last message class to be disabled (only on explicit master request, FR-13.1)
**And** the message is rendered from `RenderFacts` (template or LLM from Epic 6)

> **Send-time recompute (N6):** Pre-visit recommendations are time-sensitive (the client is arriving in 30-60 min). `RenderFacts` is recomputed at send-decision time (not at outbox-enqueue time) so the recommendation reflects the latest CRM state, not a stale snapshot from when it was queued.

### Story 4.4: Shift-Start Message & Micro-Support

As a master,
I want a shift-start message with my day plan and one focus,
So that I start my shift with clear direction.

**Acceptance Criteria:**

**Given** a master has a shift scheduled
**When** the shift starts
**Then** a shift-start message is sent with: short day plan (clients, who has recommendations), one day focus (not five), motivational message in psychotype tone
**And** mood screening is offered 2-3×/week (not daily — anti-fatigue), using inline keyboards (1-5 button scale)
**When** a schedule gap exists and status is green
**Then** micro-support is sent (e.g., praise when a recommendation is accepted)
**And** the late-praise exception applies: praise for a successful recommendation may be sent late, within 60 min but no later than the end of the same shift

### Story 4.5: Shift Totals with Deterministic Forecast

As a master,
I want shift totals with my results and progress,
So that I see how I did and where I stand.

**Acceptance Criteria:**

**Given** a master's shift has ended
**When** shift totals are computed
**Then** the message includes: revenue, avg check, recommendation outcomes, progress toward period bar, deterministic income forecast (from Epic 3 calc engine)
**And** one specific praise for one specific action is included
**And** bad-day reactions follow the type matrix (Addendum A.2): no hot debrief for sensitive types; for achievers, constructive redirect same evening
**And** all figures are from `RenderFacts` (deterministic, validated by output validator in Epic 6)
**And** the forecast is suppressed if data is Level 1 stale (AD-9)

> **Accepted staleness (N6):** Shift totals accept `RenderFacts` computed at render time — a daily summary tolerates seconds-level staleness between render and send. No recompute at send-decision time for this message class.

### Story 4.6: GROW Session at Period End

As a master,
I want a GROW session at the end of each pay period,
So that I review results and agree on next period's focus.

**Acceptance Criteria:**

**Given** a pay period is ending
**When** the GROW session is initiated
**Then** the session follows: Goal (bar + nearest money lever of the salon's motivation plan), Reality (honest totals, self-comparison only — no cross-master comparison), Options (2-3 focus options, master chooses — autonomy), Will (agreements fixed: bar, focus, what the AI will do)
**And** the adaptive bar (from Epic 3, Story 3.3) is presented and accepted by the master in the Will phase
**And** the session is a bounded LLM dialogue (from Epic 6, Story 6.1 — bounded coaching-dialogue partner role)
**And** all figures in the session are deterministic (from the calc engine)
**And** agreements are stored and audited

### Story 4.7: Forcing, Pace Reset & GROW Consent Gate

As a master,
I want the AI to push me only when I'm progressing, green, and have consented,
So that pressure is always earned and agreed.

**Acceptance Criteria:**

**Given** the system considers raising the bar or intensity
**When** forcing is evaluated
**Then** forcing requires ALL THREE: sustained progress per FR-2.7 (≥+5% or ≥95% retention over 2-week window at ≥80% load), green status (from Epic 5), and the master's explicit consent in dialogue
**And** automated sprint triggers always pass through the GROW consent gate — never auto-initiated
**When** plan attainment is < 10-15% away
**Then** a proximity trigger fires: the system shows how close the plan is and offers a sprint (promotion types: exciting framing; prevention types: "don't lose what's almost earned")
**When** pace reset conditions are met (yellow/red status; ≥2 weeks without progress at normal load; life circumstances; post-sprint recovery)
**Then** the bar is held or lowered, and the system switches to support mode
**And** after a forced sprint, a planned recovery window without ambitious goals is provided

### Story 4.8: Barrier Work (MI-Style Diagnostics)

As a master,
I want the AI to help me diagnose why I'm not converting recommendations,
So that I can overcome the barrier.

**Acceptance Criteria:**

**Given** recommendations of a type systematically miss checks (CRM-visible, no surveys)
**When** the system detects systematic non-conversion
**Then** the AI soft-raises the topic and diagnoses the barrier (knowledge / skill / psychology) via MI-style open questions
**And** the matching intervention matrix is applied (Addendum A.5)
**And** this is a coaching conversation initiated with care, not compliance control
**And** the conversation is a bounded LLM dialogue (from Epic 6)
**And** the barrier diagnosis and intervention are logged in the master profile

### Story 4.9: Proactive Triggers & Dispatcher Arbitration

As the system,
I want to publish trigger candidates and arbitrate competing messages,
So that the master receives the highest-value message within caps.

**Acceptance Criteria:**

**Given** multiple proactive triggers compete for the same decision window
**When** the dispatcher evaluates triggers
**Then** engines publish `TriggerCandidate` (message class, expected income, deadline, source-data timestamps) — the dispatcher's only ranking input
**And** the highest expected-income-value message is sent; others are deferred or merged
**And** hard caps are enforced: ≤5 initiative messages per shift, ≤2 on days off, lower on yellow/red
**And** the message-class disable ladder is enforced: period-total and pre-visit recommendation classes are disabled last
**And** Telegram pacing (~1 msg/s per chat) is enforced via per-chat_id Redis token buckets
**And** force/sprint triggers pass through the GROW consent gate
**And** the trigger catalogue is implemented: period-bar risk, growth opportunity, proximity to plan, negative pattern, positive pattern, master silence beyond norm
**When** ≥70% of messages are ignored over 2 weeks
**Then** frequency is reduced to minimum and the system asks once, directly, what format would be useful
**And** the AI never escalates pressure on a disengaged master
**And** insistence rule: per-topic offer counters live in `profile`; a persistent proposal is made at most twice, then fixed and dispatcher-suppressed
**And** message rows record `rendered_by: llm|template|validator-fallback`

---

## Epic 5: Emotional Monitoring & Traffic Light (M2)

The system monitors the master's emotional state through screenings, tone analysis, and CRM signals, and adjusts behavior via the traffic light with hysteresis — reducing frequency and forbidding forcing on yellow, support-only on red.

### Story 5.1: Mood Screenings & WHO-5 Check-Ins

As a master,
I want short mood check-ins 2-3 times a week,
So that the AI can notice when I'm struggling.

**Acceptance Criteria:**

**Given** a master is in calibration or active mode
**When** a screening is scheduled (2-3×/week)
**Then** a short scale question is sent using inline keyboards (1-5 button scale)
**And** a WHO-5-derived check-in is sent every 2 weeks (conversational, non-clinical)
**And** the master has the right not to answer without consequence
**And** screening is framed as care, not control
**And** non-response is a signal but never a reason for pressure
**And** no diagnoses or clinical terms are used
**When** serious distress is detected
**Then** the AI gently recommends seeing a professional
**And** screening results feed the traffic light composite score (Story 5.3) and the dynamic profiling screening stream (Story 5.5)

### Story 5.2: Tone Analysis (LLM Classifier)

As the system,
I want to analyze correspondence tone with confidence scoring,
So that emotional state is detected from how the master writes.

**Acceptance Criteria:**

**Given** the master sends messages to the bot
**When** the LLM tone classifier processes correspondence
**Then** a structured output is emitted: tone score 0-1 + confidence
**And** signals analyzed: length, speed, style change, emoji disappearance in an emoji-active master, ignoring
**And** the classification feeds deterministic engines and never reaches the master unvalidated
**When** the confidence threshold is not met (start ≥0.7; burnout markers ≥0.8)
**Then** the tone assessment cannot change the traffic light status
**When** consent (2) is withdrawn
**Then** tone analysis is disabled and the traffic light operates on CRM signals only (AD-14 re-weights the composite score with config-owned rule)

### Story 5.3: Traffic Light Composite Score & Hysteresis

As the system,
I want a composite traffic light score with hysteresis,
So that status transitions are stable and decided in code.

**Acceptance Criteria:**

**Given** three signal streams are available (screenings, tone, CRM signals)
**When** the traffic light engine computes the composite score
**Then** the score is 0-100 from three streams: screenings normalized 0-100, LLM tone 0-1 with confidence, CRM signals (output drop at same booking level, cancellations up, shifts shortened)
**And** weights are config-defined
**And** status transitions are decided in code, never by the LLM
**When** yellow entry conditions are met (score <60 for 3 days running, or tone <0.4 at ≥0.7 confidence)
**Then** the status transitions to yellow
**And** yellow exit requires score ≥70 held for 3 days
**When** red entry conditions are met (score <40 for 7 days, or burnout markers at ≥0.8 confidence + output drop >20% at same booking over 2 weeks)
**Then** the status transitions to red
**And** red exit requires score ≥55 held for 7 days
**And** minimum stay is 3 days (yellow) / 7 days (red)
**And** calibration guidance is config-defined: false reds ≤1/10 masters/month; missed burnouts = 0 (on doubt, lean yellow); yellow↔green ≤1/week per master
**And** engines publish score + recommended transition (pure compute); `profile` applies hysteresis and owns the committed color (AD-14)

### Story 5.4: Status Behavior (Green/Yellow/Red)

As the system,
I want status-appropriate behavior,
So that coaching adapts to the master's emotional state.

**Acceptance Criteria:**

**Given** the traffic light has a committed color
**When** the dispatcher reads the committed color at decision time
**Then** green status: standard behavior, forcing allowed
**And** yellow status: frequency ↓, challenge ↓, support ↑, forcing forbidden, soft open question
**And** red status: support only, no goals, no sales talk, offer to discuss workload, delicate owner escalation
**And** the dispatcher reads the committed color via `profile`'s interface — never a cached engine inference (AD-14)
**And** red-status escalation to owner carries conclusion + recommendation only — no correspondence quotes

### Story 5.5: Screening Signal Stream for Dynamic Profiling

As the system,
I want screening results to feed the master's dynamic profile,
So that profiling reflects emotional state over time.

**Acceptance Criteria:**

**Given** screening results are collected (Story 5.1)
**When** the dynamic profiling engine updates the master's scales
**Then** screening results feed the fourth signal stream (state screenings) for FR-2.2
**And** scales are updated via exponential smoothing (from Epic 1, Story 1.5)
**When** consent (2) is withdrawn
**Then** the screening stream drops out of the composite score
**And** CRM-signal-only weights apply (config-owned re-weighting rule, AD-14)
**And** the re-weighting is audited

---

## Epic 6: LLM Narration, Depersonalization & Output Validation (M2)

The LLM narrates pre-computed facts in psychotype-calibrated prose through a depersonalization gateway with placeholder names, and the output validator hard-enforces that every money-type number matches the computed value — a message that fails validation is never sent.

### Story 6.1: LLM Port & Prompt Library

As the system,
I want a single LLM port with versioned prompts,
So that narration is psychotype-calibrated and provider-swappable.

**Acceptance Criteria:**

**Given** the LLM port is configured
**When** the system needs LLM narration
**Then** the `LlmPort` interface is used (single port — provider swap happens behind it without domain rework, AD-2)
**And** the prompt library contains versioned prompt artifacts stored in the config store
**And** the LLM has exactly three roles: (a) narrator of pre-computed bound facts in psychotype-calibrated prose; (b) structured-output classifier (tone score + confidence); (c) bounded MI/GROW coaching-dialogue partner
**And** `RenderFacts` → prompt assembly is performed by the `llm` module
**And** LLM cost controls are implemented: response length caps, per-master daily token meter, budget-trip template fallback
**And** prompt versions are stored with every message for reproducibility

> **Sequencing constraint (H3):** Until Story 6.3 (output validator) lands, the LLM narration path stays DISABLED — only deterministic templates render (`rendered_by: template`). The first LLM-narrated message may ship only in the same iteration as, or after, 6.3. This prevents unvalidated LLM-authored figures from reaching masters during M2 ramp-up.

### Story 6.2: Depersonalization Strip & Placeholder-Name Egress

As the system,
I want to strip direct identifiers and replace them with placeholder names before LLM egress,
So that no raw identifiers enter prompts even in the depersonalized circuit.

**Acceptance Criteria:**

**Given** a message is being prepared for LLM narration
**When** the strip step runs in the `llm` adapter before the gateway
**Then** direct identifiers (names, contacts, client names) are replaced with internal IDs + placeholder names (e.g., `Master_A`, `Client_42`)
**And** a versioned egress allowlist defines egressible fields
**And** a versioned placeholder map carries the substitution
**And** the LLM generates against pseudonym/placeholder tokens
**When** the LLM returns
**Then** final message assembly re-binds real names inside the RU zone (reverse substitution, same bound-variable mechanism as numbers)
**And** every egress call is an audit event (payload hash + allowlist version + placeholder-map version)
**And** the placeholder-map version used at the strip step is recorded on the outbox row; the re-substitution step reads that same recorded version, NOT the current active version — preventing mid-roundtrip races when the map is edited between strip and re-substitution
**And** an egress contract test asserts no direct identifier and no raw name passes the strip point
**And** secrets live in Yandex Lockbox

### Story 6.3: Output Validator (Figure Check + Placeholder Check)

As the system,
I want an output validator on the egress path,
So that no LLM-authored or mismatched money number ever reaches the master.

**Acceptance Criteria:**

**Given** a message has been rendered by the LLM and re-personalized
**When** the output validator runs (AFTER re-personalization, BEFORE outbox send, AD-16)
**Then** the `RenderFacts` snapshot used to render the message is **persisted on the outbox row** (not held in memory) so it survives worker restarts between render and send, and is available to both the validator and the template fallback (no re-fetch, no recomputation)
**And** the figure check validates: every money-type number in the rendered message is normalized to a canonical form (strip thousands separators, unify decimal separator to `.`, strip currency tokens) and then compared for byte-equality (after engine-defined rounding) against the corresponding `RenderFacts` computed value, similarly normalized
**And** non-money figures (scores, rankings, cap counts) are validated the same way against their `RenderFacts` bound values
**And** the placeholder check validates: no unreplaced placeholder token (e.g., `Master_A`, `Client_42`) remains in the rendered text
**When** either check fails
**Then** the message is NOT sent (hard fail)
**And** the event is audited (message_id, failed check, expected vs actual / leaked token)
**And** a deterministic template fallback is queued for the same outbox row (`rendered_by: validator-fallback`)
**When** the validator itself raises an exception (not a check failure)
**Then** the message is NOT sent, the exception is audited, and template fallback is queued — identical handling to a check failure (crash-safe)
**And** the validator is owned by the `messaging` module and runs inside the RU zone
**And** the validator is unit-tested and covered by the golden set

### Story 6.4: Template Fallback on LLM Outage/Budget Trip

As the system,
I want deterministic template fallback when the LLM is unavailable,
So that wording degrades but correctness never does.

**Acceptance Criteria:**

**Given** the LLM is unavailable (outage or budget trip)
**When** narration is requested
**Then** narration degrades to deterministic templates (`rendered_by: template`)
**And** the output validator still gates template figures (AD-16)
**When** consent (4) is withdrawn
**Then** LLM egress is blocked and the service degrades to template-only narration
**And** zero figure-accuracy incidents is a hard requirement (CM-4)
**And** wording degrades, correctness never does
**When** the template fallback also fails validation (validator-double-fail)
**Then** a minimal figure-free notice is sent ("данные обновляются, итоги будут позже")
**And** the event is audited as `validator-double-fail`
**And** alerting fires on validator-double-fail rate

### Story 6.5: Golden Tests (Promptfoo)

As a developer,
I want golden tests that assert facts present, no invented numbers, correct register per type, and ethics cases,
So that the LLM pipeline is continuously validated.

**Acceptance Criteria:**

**Given** the golden test suite is configured
**When** CI runs the promptfoo golden set
**Then** tests assert: facts present in output, no invented numbers, correct register per motivational type
**And** ethics cases are covered: no cross-master comparison, no guilt/threat language
**And** the validator rejects injected wrong numbers (golden test for AD-16)
**And** tests cover all three LLM roles: narrator, classifier, dialogue partner
**And** tests are CI-enforced and block merges on failure

### Story 6.6: Memory & Personalization

As the system,
I want long-term and short-term memory with archival,
So that prompts are personalized without overwhelming context.

**Acceptance Criteria:**

**Given** the master has interaction history
**When** the system assembles prompt context
**Then** long-term memory includes: master profile (type, scales, agreements, barriers, what worked/didn't), client profiles (refusals, preferences), bar history and results
**And** short-term focus includes: current period, week focus, open agreements
**And** fresh signals outweigh old; stale observations are archived out of the prompt set (periods config-defined)
**And** memory is used for help, never pressure: the AI does not remind masters of past failures; negative episodes are stored only as support material
**When** consent (3) is withdrawn
**Then** aggregated-profile-only mode activates: raw correspondence and quotes are deleted; the aggregated profile (type, scales + values, traffic-light status + transition history) is retained (AD-15)
**And** memory recency/archival policy is owned by `profile` and config-driven

> **Erasure ownership:** The actual purge of raw correspondence on consent (3) withdrawal is delegated to the cross-module erasure-propagation story (Story 7.4), which `profile` orchestrates. Story 6.6 defines the memory policy and what is retained/deleted; 7.4 executes the cross-module purge (messaging rows, crm_mirror tombstones, audit event).

---

## Epic 7: Owner Reporting & Pilot Readiness (M3)

The owner receives per-period reports per master with aggregate-only confidentiality (no correspondence quotes), red-status escalations, and the system is ready for pilot with degradation drills, erasure propagation, and the Roskomnadzor notification file.

### Story 7.1: Owner Period Report

As an owner,
I want a per-period report per master,
So that I see results, conversion, and aggregated state without seeing private correspondence.

**Acceptance Criteria:**

**Given** a pay period has ended
**When** the owner report is generated
**Then** the report includes per master: metrics vs plan and previous period; plan-attainment position and income dynamics; recommendation conversion (CRM-measured); specific praise facts; improvement areas + how the owner can help (training, assortment, booking); aggregated state signals; profile status (how the master responds to communication, what changed)
**And** the report is delivered via Telegram
**And** the owner-facing render is aggregate-only and psych-layer-inaccessible (AD-7): no profile scales, no traffic-light status (except red-escalation fact + "share of green weeks" aggregate), no correspondence quotes
**And** all figures are deterministic (from the calc engine, Epic 3)
**And** the report is rendered from `RenderFacts` (template or LLM from Epic 6, with output validator)

### Story 7.2: Red-Status Escalation

As an owner,
I want out-of-band escalation on red status or systemic anomalies,
So that I can intervene when a master needs support.

**Acceptance Criteria:**

**Given** a master is in red status or a systemic anomaly is detected
**When** the escalation is triggered
**Then** an out-of-band escalation is sent to the owner
**And** the escalation carries conclusion + recommendation only — no correspondence quotes
**And** the owner sees: the red-escalation fact + the "share of green weeks" aggregate in the period report
**And** systemic anomalies (e.g., one priority position sagging across all masters → assortment/price problem) are escalated separately
**And** the psych layer (scales, tone, correspondence, full traffic-light history) is inaccessible to the owner (AD-7)

### Story 7.3: Confidentiality Aggregation Boundary

As the system,
I want an enforceable aggregation boundary,
So that no verbatim or quote-length fragments reach the owner.

**Acceptance Criteria:**

**Given** the owner-facing render boundary is active
**When** any owner-visible output is generated
**Then** master↔AI correspondence is never transmitted to the owner in any form except aggregated conclusions
**And** the aggregation boundary is enforceable: no verbatim, no quote-length fragments, threshold-defined aggregation
**And** the aggregation rule is config-defined [уточнить: OQ-9 — aggregation threshold (min N masters / min window) unresolved; until resolved, owner-visible conclusions require ≥ 3 distinct master interactions in the period, no verbatim fragments ≥ 5 words]
**And** the boundary is enforced at both the query layer AND the owner-facing render boundary (AD-7)
**And** the psych layer (scales, tone, correspondence, traffic-light status) is inaccessible by construction

### Story 7.4: Erasure Propagation (Cross-Module Owner)

As a master,
I want my data deleted when I withdraw consent or request erasure,
So that my PDn rights are enforced.

**Acceptance Criteria:**

**Given** an erasure or deletion request is received (or consent (3) withdrawal triggers scoped erasure)
**When** the erasure is executed
**Then** `profile` orchestrates the cross-module purge as the single erasure entry point (referenced by Stories 1.3 and 6.6)
**And** an audit event is created listing purged schemas/rows
**And** tombstones are created in `crm_mirror` keyed by canonical ID, surviving snapshot reconciliation and suppressing re-ingestion (AD-15)
**And** `profile` PDn is purged with the same event
**And** `messaging` raw correspondence and quotes are purged
**When** consent (3) is withdrawn (aggregated-profile-only mode)
**Then** scoped erasure activates: raw correspondence and quotes are deleted
**And** the aggregated profile (type, scales + values, traffic-light status + transition history) is retained
**And** erasure propagation includes CRM-mirror tombstones
**And** the erasure is idempotent — re-triggering for the same consent event does not double-purge

### Story 7.5a: Degradation & DR Drills

As the team,
I want degradation and DR drills executed,
So that reliability claims are validated before pilot.

**Acceptance Criteria:**

**Given** the system is approaching pilot (M3)
**When** degradation drills are executed
**Then** LLM outage → template fallback is validated (Story 6.4)
**And** CRM stale → degradation ladder (Level 1/Level 2) is validated (Story 2.4)
**And** DR restore is validated (RPO ≤15min, RTO ≤4h, NFR-C)
**And** config rollback < 5 min is validated (FR-14.1)
**And** drills are scheduled quarterly

### Story 7.5b: Config-Seed Deliverables

As the team,
I want the full config-seed set prepared at pilot start,
So that behavioral parameters are calibrated and versioned.

**Acceptance Criteria:**

**Given** pilot start is approaching
**When** config-seed deliverables are prepared
**Then** the full set is delivered: profile scale definitions, barrier→intervention matrix, starting thresholds, memory archival policy, aggregation rule for owner-visible conclusions, bar corridor starting values, progress thresholds, type-divergence delta
**And** each deliverable is a versioned config row (AD-6) with documented starting values and rationale
**And** the config-seed is reviewable and rollback-able

### Story 7.5c: Roskomnadzor File & Pilot Gate

As the team,
I want the Roskomnadzor notification file and pilot gate ready,
So that the legal launch gate and pilot scope are satisfied.

**Acceptance Criteria:**

**Given** the legal and pilot gates are approaching
**When** the Roskomnadzor file and pilot gate are prepared
**Then** the Roskomnadzor notification file is prepared (art. 12 consent + PDn operator declaration, NFR-B)
**And** the pilot gate is ready: 1-2 salons (M3)
**And** the PDn operator entity is confirmed [уточнить: OQ-11]
