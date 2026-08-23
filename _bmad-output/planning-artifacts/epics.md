---
stepsCompleted: ["step-01-validate-prerequisites"]
inputDocuments:
  - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/prd.md
  - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/addendum.md
  - _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md
---

# Zabot AI Mentor (Stage 1) - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Zabot AI Mentor Stage 1, decomposing the requirements from the PRD and Architecture spine into implementable stories.

**Input documents:** PRD (2026-08-18) + Addendum; Architecture Spine (final, 2026-08-18). No UX design contract (Stage 1 is a Telegram bot; interaction behavior is specified in the PRD itself).

## Requirements Inventory

### Functional Requirements

**F1 — Onboarding & Consent**

- FR-1.1: Onboarding via Telegram deep link + `/start`; consent capture is a first-class step (152-ФЗ: profiling, mood data, correspondence retention); no cold messaging possible by design.
- FR-1.2: Primary profiling as a live 3–5 min dialogue (one question at a time, reactions to answers) determining starting motivational type, scale values, tone/frequency, personal quiet hours; mandatory questions — Addendum A.4.
- FR-1.3: CRM history analysis at onboarding (avg check, complexity, dynamics) for a realistic starting bar; cold start uses config-defined conservative priors; onboarding never blocked.
- FR-1.4: AI states working agreements at end of onboarding and obtains confirmation; first 2 weeks = calibration mode with elevated format-feedback requests.
- FR-1.5: Consent withdrawal degrades service to non-profiling generic mode automatically; every profiling decision links to an active consent record.

**F2 — Master Profiling (hybrid: type + live scales)**

- FR-2.1: Profile = motivational type (1 of 5 archetypes, Addendum A.2) + 9 live scales 0–100 (Addendum A.3); scales, not the type, drive real behavior over time.
- FR-2.2: Dynamic profiling from four signal streams: master replies, behavior (answered/ignored by message class), CRM results, state screenings (F6).
- FR-2.3: Scales move via exponential smoothing; α per-scale config parameter (fast 0.3–0.5, slow 0.1–0.2), changeable without release; values and versions logged.
- FR-2.4: Type change only after ≥ 2 pay periods of sustained divergence; every significant profile change logged with justification.
- FR-2.5: Explicit master request ("пиши короче", "без эмодзи", "не пиши до 10:00") applies immediately and overrides model inferences.
- FR-2.6: Type never disclosed to the master as a label; soft descriptive answer on request.

**F3 — Communication Engine (communication contract)**

- FR-3.1: Per-master communication contract: touch frequency, message length, tone, challenge/support ratio, number format, send times; starting values by type.
- FR-3.2: Hard caps: ≤ 5 initiative messages per shift, ≤ 2 on days off; lower on yellow/red; quiet hours default 21:00–9:00 master-local, configurable by owner and master.
- FR-3.3: Pre-visit recommendations sent T-30…60 min before the appointment.
- FR-3.4: Message-class disable ladder: money/period-total and pre-visit recommendation classes disabled last.
- FR-3.5: Ignore detection: ≥ 70% messages ignored over 2 weeks → reduce frequency to minimum and ask once, directly; never escalate pressure.
- FR-3.6: Trigger arbitration: highest expected-income-value message sent; others deferred or merged — always inside caps.

**F4 — Recommendation Engine (next best offer)**

- FR-4.1: Signal sources: full client visit history, product purchase cycles, service cyclicity/gaps, seasonality, visit comments, owner priorities, past refusals.
- FR-4.2: Candidates = owner priorities ∪ history-logical positions; exclusion filters: ≥ 2 consecutive refusals → N-month pause, contraindications/allergies, stop-list, incompatibility with booked service.
- FR-4.3: Ranking by expected value: acceptance probability × margin/priority.
- FR-4.4: 1–3 recommendations per visit (fewer is better); format what/why/how; depth by sales-confidence scale (full script for novices, thesis for veterans).
- FR-4.5: Zero-survey feedback loop: never asks the master whether they offered; outcomes reconciled from check contents only; no interrogation.
- FR-4.6: Automatic outcomes update client profile, master profile (conversion by type), and engine quality.

**F5 — Coaching Cycles (shift / week / pay period)**

- FR-5.1: Shift-start message: day plan, one day focus, mood screening 2–3×/week, motivational message in psychotype tone.
- FR-5.2: Micro-support between visits only on schedule gap + green status.
- FR-5.3: Shift totals: revenue, avg check, recommendation outcomes, progress + deterministic income forecast, one specific praise; bad-day reaction per type matrix (no hot debrief for sensitive types).
- FR-5.4: GROW session at period end: Goal (bar + nearest money lever), Reality (honest totals, self-comparison), Options (master chooses), Will (agreements fixed).
- FR-5.5: Forcing requires all three: sustained progress ≥ 2 weeks, green status, master's explicit consent via GROW gate; proximity trigger < 10–15% to next level → sprint offer.
- FR-5.6: Pace reset on: yellow/red status; ≥ 2 weeks without progress; life circumstances; post-sprint recovery window.
- FR-5.7: Barrier work: systematic non-conversion → soft MI-style diagnostics (knowledge/skill/psychology) → matching intervention matrix (Addendum A.5).

**F6 — Emotional Monitoring & Traffic Light**

- FR-6.1: Signal sources: screenings 2–3×/week + WHO-5-derived check-in every 2 weeks; correspondence tone analysis; indirect CRM signals.
- FR-6.2: Traffic light = composite score (0–100) from three streams, config-weighted; transitions decided in code, never by LLM; tone below confidence threshold cannot change status.
- FR-6.3: Hysteresis: differing entry/exit thresholds with minimum stay (yellow entry < 60 for 3 days, exit ≥ 70 held 3 days; red entry < 40 for 7 days, exit ≥ 55 held 7 days; min stay 3/7 days — pilot-calibrated).
- FR-6.4: Status behavior: green — standard; yellow — frequency ↓, support ↑, forcing forbidden; red — support only, no goals, no sales, delicate owner escalation.
- FR-6.5: Ethics: screening framed as care; non-response never a pressure reason; no diagnoses; red escalation carries conclusion + recommendation only, no correspondence quotes.

**F7 — Goals, Adaptive Bar & Motivation Schemes**

- FR-7.1: Goal (owner-set, immutable by AI) vs adaptive bar (individual, AI-adjustable within owner rules); the AI adapts bar and path, never the goal.
- FR-7.2: Goals module lives inside the Mentor service at Stage 1; two-way Zabot sync deferred.
- FR-7.3: Owner configures: target metrics, motivation scheme, pay period, priorities, stop-list, quiet hours, communication limits.
- FR-7.4: Fixed set of 5 scheme types (progressive percent; fixed + percent; category rates; period-goal bonuses; combinations), each with parameter schema (Addendum A.6); all income math follows the salon's formula.
- FR-7.5: Incomplete scheme config → no invented income figures; metrics only + owner clarification request.
- FR-7.6: Adaptive bar: specific, measurable, difficult-but-attainable (~60–70%), accepted in GROW; movement rules (raise on progress + consent; stagnation — hold + diagnose; decline — never raised, may be tactically lowered); bounds config-defined, pilot-calibrated; never framed as punishment.
- FR-7.7: Income transparency: master can ask income/next-percent/what-if questions — answered by deterministic calculation on CRM data.
- FR-7.8: Scheme changes apply from next pay period; AI explains what changed in the master's money.

**F8 — Proactive Triggers**

- FR-8.1: Trigger catalogue: period-bar risk, growth opportunity, proximity to next level, negative pattern, positive pattern, master silence beyond norm.
- FR-8.2: All initiative messages pass through caps, priorities, arbitration; proactivity ≠ frequency.

**F9 — Deterministic Money Math & LLM Roles**

- FR-9.1: All figures computed deterministically; LLM receives computed values as bound inputs and is forbidden from generating/estimating/rounding any figure.
- FR-9.2: LLM has exactly three roles: narrator, structured-output classifier, bounded coaching-dialogue partner.
- FR-9.3: On LLM outage or budget trip, narration degrades to deterministic templates — wording degrades, correctness never does; zero figure-accuracy incidents is hard.

**F10 — Owner Reporting & Escalation**

- FR-10.1: Per pay period, per master: metrics vs goals/previous period; scheme position and income dynamics; recommendation conversion; praise facts; improvement areas; aggregated state signals; profile status.
- FR-10.2: Out-of-band escalation only on red status or systemic anomalies.
- FR-10.3: Confidentiality: correspondence never transmitted to owner except aggregated conclusions; aggregation boundary enforceable (no verbatim, no quote-length fragments).

**F11 — CRM Integration & Data Freshness**

- FR-11.1: Data via Zabot CRM: visit history incl. comments; sales by master by client; shift load/schedule; bookings; check composition; metric dynamics; cancellations.
- FR-11.2: Freshness: checks/sales ≤ 60 min; schedule/bookings ≤ 15 min; dynamics/period totals ≤ 24 h.
- FR-11.3: Degradation ladder: Level 1 (stale but usable) — timestamp label, forecasts suppressed; Level 2 (hard-stale/down) — no figures, money math/praise/forecasts suspended, honest notice; recovery — resync, recompute, no retroactive event messages.
- FR-11.4: Cold start: config-defined conservative priors per entity; onboarding never blocked on data sparsity.
- FR-11.5: Sync = watermark polling baseline; webhooks only accelerator; fixture CRM keeps M0 unblocked (pending OQ-1).

**F12 — Memory & Personalization**

- FR-12.1: Long-term memory (master profile, client recommendation profiles, bar history); short-term focus (current period, week focus, open agreements).
- FR-12.2: Fresh signals outweigh old; stale observations archived out of prompt set (periods config-defined).
- FR-12.3: Memory used for help, never pressure; no reminding of past failures.

**F13 — Communication Floor, Pause & Opt-out** `[ASSUMPTION — OQ-4]`

- FR-13.1: Minimum floor: period totals and pre-visit recommendations remain at minimum frequency (disabled last).
- FR-13.2: Pause/vacation mode: mute for N days with announced resumption; goals/bar logic accounts for pause.
- FR-13.3: Full opt-out: degrades to legally required notices only; equals consent withdrawal; tracks CM-2.
- FR-13.4: "No full silence while consent is active" — autonomy and legal withdrawal rights always win.

**F14 — Configuration, Calibration & Audit**

- FR-14.1: All behavioral parameters config-managed, changeable without release; insert-only versioned; config version in message reproducibility; rollback < 5 min.
- FR-14.2: Every significant decision (profile change, status switch, config change, consent, egress, erasure) in append-only audit log with justification and inputs.
- FR-14.3: Config-seed deliverables at pilot start: scale definitions, barrier matrix, thresholds, archival policy, scheme schemas, aggregation rule.

### NonFunctional Requirements

- NFR-A (Determinism): 100% figures deterministic; zero figure-accuracy incidents; every message reproducible from (facts, config_version, prompt_version); status transitions decided in code.
- NFR-B (Compliance & privacy): RU-zone PDn residency; depersonalized-only egress via audited gateway; art. 12 consent + Roskomnadzor notification as launch gates; append-only audit; PII-scrubbed logs; erasure propagation incl. CRM-mirror tombstones; consent-withdrawal → auto-degrade.
- NFR-C (Reliability & ops): LLM outage → template fallback; degradation ladder with quarterly drills; DR RPO ≤ 15 min / RTO ≤ 4 h with quarterly restore drill; config rollback < 5 min.
- NFR-D (Channel realism): Telegram — no read receipts (engagement answer-based only); quiet hours best-effort; scale widgets via inline keyboards.
- NFR-E (Scalability & cost): hundreds of masters, few messages/second; LLM cost controls: response length caps, per-master daily token meter, budget-trip fallback.
- NFR-F (Time & geography): static UTC+2..+12 zones; timezone per master/salon stored at onboarding; quiet hours and pre-visit timing in master-local time.
- NFR-G (Security & isolation): inter-salon isolation (row-level multi-tenancy baseline); machine-to-machine keys; secrets in vault; PII-scrubbed logging.
- NFR-H (Explainability): every behavioral decision logged with inputs and justification; config/threshold versions recorded with every change.

### Additional Requirements

*From the architecture spine (ADs, conventions, stack, structural seed) — technical requirements that shape epic/story structure:*

- **Repo scaffold (greenfield starter):** Python 3.12+ modular monolith, source tree `src/domain` (pure: profile, engines, messaging) + `src/adapters` (crm_adapter + fixture, llm, telegram/aiogram, clock, config_store) + `src/app` (FastAPI wiring, webhook) + `src/worker` (scheduler, outbox dispatcher, sync jobs); tests unit/contract/golden. (Epic 1 Story 1 basis)
- **AD-2 Ports:** domain defines Protocol interfaces — `CrmPort`, `LlmPort`, `TelegramPort`, `Clock`, `ConfigStore` — implemented by adapters; no external call from domain; import-linter enforced in CI.
- **AD-4 Transactional outbox:** every outbound side effect written as outbox row in the same transaction as the decision; dispatcher sweeps due rows (FOR UPDATE SKIP LOCKED) every 15–30 s; Redis never holds durable state.
- **AD-5 Two-zone residency + depersonalization:** strip step in `llm` adapter with versioned egress allowlist; every egress call an audit event; egress contract test; RU-side name re-binding after LLM returns; secrets in Yandex Lockbox.
- **AD-6 Insert-only versioned config + prompts:** immutable versioned rows, Pydantic-validated at editing boundary; every message stores (config_version, prompt_version); config-completeness degradation mode.
- **AD-7 Salon-scoped tenancy from day one:** salon key on every domain row; salon-scoped queries; Redis keys salon-prefixed.
- **AD-8 UTC in DB, local at decision point:** timestamptz everywhere; quiet hours/pre-visit offsets evaluated at send-decision time against master-local clock.
- **AD-9 Two timestamps per mirror row:** `source_event_at` + `synced_at`; freshness tiers read `synced_at`; suppress_backdated reads `source_event_at`; absence ≠ staleness (cold-start priors).
- **AD-10 Dispatcher arbitration:** engines publish `TriggerCandidate`; dispatcher enforces caps, disable ladder, pacing (~1 msg/s per chat via Redis token buckets), GROW consent gate, insistence counters, `rendered_by` recording.
- **AD-11 Module boundaries:** one deployable; cross-module calls via published interfaces only; one Postgres schema per module + append-only `audit`; import-linter + schema-ownership CI checks; no microservices/broker/K8s.
- **AD-12 At-least-once idempotency:** `update_id` dedup; outbox and sync upserts idempotent by natural key; surrogate IDs assigned by `crm_sync` at ingestion.
- **AD-13 Canonical master identity:** one `master_id` owned by `profile`; `chat_id ↔ master_id` mapping owned by `profile`; all references carry canonical ID.
- **AD-14 Single-owner state mutation:** traffic light — engines score, `profile` applies hysteresis and owns committed color; dispatcher reads committed color.
- **AD-15 Erasure propagation:** tombstones in `crm_mirror` surviving snapshot reconciliation; audit event lists purged schemas/rows.
- **Testing strategy:** pytest + pytest-asyncio; contract tests via CRM fixture replay; promptfoo golden set (facts present, no invented numbers, register per type, ethics cases: no cross-master comparison, no guilt/threat).
- **CI/CD:** GitHub private repo + self-hosted RU runner; CI: ruff, mypy, unit/contract/golden, image build, import-linter, schema-ownership check. Deploy: docker compose, 2 VMs (app + worker), Yandex Container Registry.
- **Environments:** prod (webhook mode, RU cloud); dev (aiogram polling + fixture CRM); staging (dedicated test bot). DR: managed backups + PITR.
- **Stack seed:** Python 3.12+, FastAPI, aiogram 3, PostgreSQL 17 (managed Yandex), Redis 8, Sentry + Grafana/Yandex Cloud Monitoring; versions pinned at M0.
- **Observability:** structured JSON PII-scrubbed logs; alerting on user-visible SLOs (per-entity freshness, oldest pending outbox row, LLM-port error rate, quiet-hours defer rate).
- **Milestone mapping (PRD §7):** M0 wks 1–4 (onboarding, consent, config versioning, scheduler + quiet hours, templates, audit, fixture CRM) → M1 wks 5–8 (real CRM, freshness SLO, degradation L1; gated OQ-1) → M2 wks 9–14 (traffic light, income/forecast, recommendations, triggers/arbitration/floors, prompt library + LLM port, golden tests) → M3 wks 15–18 (owner reporting, degradation drills, Roskomnadzor file, pilot).

### UX Design Requirements

No UX design contract exists — Stage 1 is a Telegram bot with no web/native UI (PRD §2.3 non-goals). Chat interaction patterns are specified behaviorally in the PRD (F1–F6) and the addendum's type matrix (A.2) with canonical message examples (BRD Прил. А, referenced as tone registers in A.2).

### FR Coverage Map

{{requirements_coverage_map}}

## Epic List

{{epics_list}}
