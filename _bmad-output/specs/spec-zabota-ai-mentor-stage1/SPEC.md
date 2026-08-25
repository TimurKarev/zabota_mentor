---
id: SPEC-zabota-ai-mentor-stage1
companions:
  - architecture-invariants.md
  - open-questions.md
  - stack.md
  - glossary.md
  - ../planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/SOLUTION-DESIGN.md
sources:
  - ../planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md
  - ../planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/.memlog.md
  - ../planning-artifacts/prds/prd-zabota_mentor-2026-08-18/prd.md
  - ../../docs/Вопросы_команды_и_ответы_по_БТ_v2_1.md
---

> **Canonical contract.** This SPEC and the files in `companions:` are the complete, preservation-validated contract for what to build, test, and validate. The 17 architecture decisions (AD-1…AD-17) are the canonical invariants — IDs verbatim, never renumbered, reused, or retired; every downstream epic/story/cite references them. Source documents in frontmatter are for traceability only.

# Zabot AI Mentor — Stage 1

## Why

A pain to solve and an opportunity to capture, under a hard legal mandate. Beauty-salon masters directly determine salon revenue through average check and service complexity, yet their ability to sell is blocked by three personal barriers — **knowledge** (doesn't know what to offer), **skill** (can't phrase the offer), and **psychology** (is afraid to seem pushy). Owners set motivation plans in Zabot but have no scalable way to coach each master daily. The opportunity: a proactive Telegram AI coach that adapts the *format, tone, frequency, and content* of every interaction to the master's psychological profile and current emotional state, grounded in CRM history, with **honesty in numbers as the trust core**. The mandate: Russian personal-data law (152-ФЗ) physically zones the system (RU-zone residency, depersonalized-only egress, 4 separate consents, Roskomnadzor notification). Affected: salon masters (primary user), salon owners, and the service's own launch.

## Capabilities

- **CAP-1 — Onboarding & 4-consent capture**
  - **intent:** A master starts via a Telegram deep-link `/start` and grants 4 separate consents (PDn+profiling, emotional-state data, correspondence retention, cross-border transfer) before any profiling question; without consent (1) the service is not activated.
  - **success:** A master who completes `/start` has 4 consent records persisted in `profile` with grant timestamps; a master who declines consent (1) cannot be messaged. *Governed by AD-17, AD-5, AD-10, AD-12.*

- **CAP-2 — Master profiling (hybrid type + live scales)**
  - **intent:** The system assigns one of 5 motivational types at onboarding and maintains 9 continuous 0–100 scales refined from 4 signal streams with per-scale exponential smoothing; an explicit master request applies immediately, bypassing smoothing.
  - **success:** Every scale value carries a version + justification in audit; a type change requires +15pts/100 sustained over ≥2 pay periods and is logged; the type is never disclosed to the master as a label. *Governed by AD-1, AD-6, AD-14.*

- **CAP-3 — Communication contract engine**
  - **intent:** Maintain a per-master contract (frequency, length, tone, challenge/support ratio, send times) with hard caps (≤5 initiative/shift, ≤2 on days off, lower on yellow/red), send-side-guaranteed quiet hours (default 21:00–9:00 master TZ), and trigger arbitration by expected-income priority.
  - **success:** No initiative message is sent inside a master's quiet-hours window; competing triggers resolve to the highest expected-income candidate inside the caps. *Governed by AD-8, AD-10, AD-17.*

- **CAP-4 — Recommendation engine (next best offer)**
  - **intent:** Build 1–3 per-visit candidates from owner priorities + client history, exclude by refusal history (≥2 consecutive → N-month pause), contraindications from visit comments, and stop-list; rank by expected value; reconcile the outcome from check contents only (never ask the master).
  - **success:** A recommendation's outcome is derived from the check without any master survey; late praise for a successful recommendation may be sent within 60 min / end of same shift. *Governed by AD-1, AD-3, AD-9, AD-12.*

- **CAP-5 — Coaching cycles (shift/week/period GROW)**
  - **intent:** Run shift-start day plan + day focus, pre-visit recommendations, micro-support on green gaps, shift totals, weekly mini-retro, and a period GROW session; forcing (raise bar) requires sustained progress + green status + the master's explicit consent via the GROW gate.
  - **success:** An automated sprint trigger is never sent without passing the GROW consent gate; a bad-day reaction follows the type matrix (no hot debrief for sensitive types). *Governed by AD-4, AD-8, AD-10, AD-14.*

- **CAP-6 — Emotional monitoring & traffic light**
  - **intent:** Compute a composite 0–100 score from 3 streams (screenings, LLM tone classification with confidence threshold, CRM signals) with hysteresis entry/exit thresholds + min stay decided in code, never by the LLM; calibration guidance: false reds ≤1/10 masters/month, missed burnouts = 0.
  - **success:** A tone classification below the confidence threshold cannot change the traffic-light state; the committed color is read from `profile` at decision time. *Governed by AD-1, AD-6, AD-14, AD-17.*

- **CAP-7 — Goals, adaptive bar & motivation plans**
  - **intent:** Read the 2 Zabot plan types (avg-check, total-revenue) read-only and compute the adaptive bar in the agent calc DB within the corridor (±15% deviation, +10%/period raise, −15% tactical floor not below 2-period actual, bar cannot exceed the Zabot plan); ruble forecasts only if the owner entered remuneration rules.
  - **success:** The bar never exceeds the Zabot plan; on incomplete plan data no ruble figure is invented (metrics + owner clarification). Bar probability method pending OQ-10. *Governed by AD-1, AD-3, AD-6.*

- **CAP-8 — Proactive triggers**
  - **intent:** Fire a trigger catalogue (period-bar risk, growth opportunity, proximity-to-plan sprint via the GROW gate, negative pattern → barrier diagnostics, positive pattern → reinforcement, master silence → one gentle bridge) with all initiative messages passing caps/priorities/arbitration.
  - **success:** Proactivity never bypasses the caps of CAP-3; a silence bridge message carries no reproach. *Governed by AD-10.*

- **CAP-9 — Deterministic money math, bounded LLM roles & output validator**
  - **intent:** Compute all figures deterministically over the agent calc DB; the LLM has 3 roles (narrator, structured-output classifier, bounded dialogue partner) and may not author/round a figure; the output validator hard-fails any mismatched money-type number or leaked placeholder, queueing a template fallback.
  - **success:** Zero figure-accuracy incidents (CM-4); a message failing the validator is not sent and a template fallback is queued. *Governed by AD-1, AD-16.*

- **CAP-10 — Owner reporting & escalation**
  - **intent:** Deliver a per-period per-master Telegram report (metrics vs plan/previous, plan-attainment, rec conversion, praise facts, improvement areas, aggregated state signals) and out-of-band red-status escalation; master↔AI correspondence is never transmitted except aggregated conclusions.
  - **success:** No verbatim correspondence or quote-length fragment reaches the owner; only the red-escalation fact + "share of green weeks" aggregate are owner-visible psych data. *Governed by AD-5, AD-7, AD-10.*

- **CAP-11 — CRM integration & data freshness**
  - **intent:** Sync via Zabot webhooks (unverified, pending OQ-1) + REST polling + nightly full reconcile, strictly one-way read-only CRM/Zabot → agent; enforce per-entity freshness tiers (checks ≤60min, schedule ≤15min, dynamics ≤24h) and a 2-level degradation ladder; cold-start uses config-defined priors.
  - **success:** No writes ever go back to Zabot; a Level-2 stale state suspends money math/forecasts and tells the master honestly; missed event messages are never sent retroactively except late praise. *Governed by AD-3, AD-9.*

- **CAP-12 — Memory & personalization**
  - **intent:** Maintain long-term memory (master profile, client profiles in recommendation terms, bar history) + short-term focus where fresh signals outweigh old; negative episodes are retained only as support material, never as prompt pressure.
  - **success:** The AI never reminds a master of past failures; archival periods are config-driven (interact with 152-ФЗ retention, OQ-3). *Governed by AD-15.*

- **CAP-13 — Communication floor, pause & opt-out**
  - **intent:** Provide a floor (1 period-summary + reactive answers, reactive always available; pre-visit disabled last and only on explicit master request), pause/vacation mode (auto-pause when no shifts ≥ N days, start N=5; manual pause), and full opt-out degrading to legally required notices.
  - **success:** A master in opt-out cannot be messaged except legally required notices; pause silences initiative messages while reactive answers remain; the owner sees only the fact "master disabled the assistant." *Governed by AD-10, AD-17.*

- **CAP-14 — Configuration, calibration & audit**
  - **intent:** Hold all behavioral parameters in insert-only versioned rows (quiet hours, caps/floors, trigger offsets, 2 plan types, bar corridor, thresholds, hysteresis, smoothing α); every message stores (config_version, prompt_version); rollback < 5 min; append-only audit with justification.
  - **success:** Every message is reconstructible from (facts, config_version, prompt_version) — 100% coverage (GM-11); activating a prior config version is a new row. *Governed by AD-6.*

## Constraints

The 17 architecture decisions are the canonical invariants. Each is carried here as its load-bearing one-liner with its stable AD ID; the full rule, what it binds, and the divergence it kills live in `architecture-invariants.md`. Do not renumber, reuse, or retire AD IDs.

- **AD-1** Pipeline, not agent: the LLM has exactly 3 bounded roles (narrator, structured-output classifier, bounded dialogue partner); no LLM-authored money/score/ranking figure; `RenderFacts` bound-variables contract owned by `messaging`.
- **AD-2** All externals behind ports (`CrmPort`, `LlmPort` single-port for provider swap, `TelegramPort`, `Clock`, `ConfigStore`); domain layer framework-agnostic; injectable `Clock`.
- **AD-3** CRM anti-corruption layer + agent calculation DB + webhook+poll+nightly-reconcile, strictly one-way read-only CRM/Zabot → agent; CRM is master of operational data + the 2 Zabot plan types, agent is master of all derived data; 2 plan types only (avg-check, total-revenue), 5-type constructor deferred.
- **AD-4** Postgres is the durability backbone: every outbound side effect through the transactional outbox (natural key = originating decision row ID); Redis holds only dedup/pacing/hot cache, never durable state.
- **AD-5** Two-zone residency + placeholder-name egress + reverse substitution: all PDn in RU zone; strip replaces direct identifiers with internal IDs + placeholder names; final assembly re-binds real names inside RU zone after the LLM returns; every egress call audited.
- **AD-6** Insert-only versioned config and prompts; every message stores (config_version, prompt_version); engines read config by version at decision time; rollback = activating a prior version (new row).
- **AD-7** Salon-scoped tenancy + psych-layer isolation + master-in-two-salons: salon key on every row; psych layer inaccessible to owner; one psych profile (master-level) + two independent work contexts (salon-scoped); admin-role extensibility reserved.
- **AD-8** UTC in DB, dual local time at the decision point: store both salon TZ and master TZ; quiet hours + personal sends in master TZ; pre-visit in salon TZ; the two compose (a pre-visit whose salon-TZ window falls in master quiet hours is deferred).
- **AD-9** Freshness tiers, two clocks (`source_event_at` vs `synced_at`), 2-level degradation ladder; missed event messages never retroactive except late praise (within 60 min / end of shift); cold-start priors ≠ staleness.
- **AD-10** Dispatcher owns arbitration, pacing, floors, consent gates, send-side quiet hours; `TriggerCandidate` is the only ranking input; send-side-GUARANTEED quiet hours; inline keyboards for screenings/quick replies; GROW consent gate for force/sprint; insistence max twice; floor/pause/opt-out.
- **AD-11** Modular monolith boundaries: one deployable, 6 modules; cross-module calls only via published interfaces (`RenderFacts`/`TriggerCandidate`); zero shared-table access; one Postgres schema per module + append-only `audit`; import-linter + schema-ownership CI.
- **AD-12** At-least-once everywhere, owned key namespaces; Telegram dedup on `update_id`; outbox/sync idempotent by natural key; `crm_sync` assigns surrogate IDs at ingestion, downstream references surrogates only.
- **AD-13** One canonical `master_id` owned by `profile`; `chat_id↔master_id` mapping owned by `profile` with merge/split rules; psych profile hangs off `master_id`, work context off (`master_id`, `salon_id`).
- **AD-14** Single-owner state mutation: engines publish score + recommended transition, `profile` applies hysteresis and owns the committed traffic-light color; consent revocation re-weights the composite score in `engines` (rule config-owned, consent state profile-owned).
- **AD-15** Erasure propagates everywhere: tombstones in `crm_mirror` survive snapshot reconciliation; consent #3 revocation triggers scoped erasure (raw correspondence deleted, aggregated profile retained); memory archival policy config-driven in `profile`.
- **AD-16** Output validator: hard enforcement of figure determinism at egress — figure check (money + non-money bound values byte-equal to `RenderFacts`) + placeholder check (no unreplaced token); on either failing the message is NOT sent, audited, and a template fallback is queued. Owned by `messaging`, runs in RU zone.
- **AD-17** Consent state model: 4 separate consents at onboarding before any profiling question; (2) and (3) independently revocable; withdraw (2) → CRM-signal-only score; withdraw (3) → aggregated-profile-only mode; withdraw (1) → full deactivation; withdraw (4) → template-only narration; every profiling/egress decision links to an active consent record.
- **C-1 Compliance launch gates (152-ФЗ):** RU-zone PDn residency; depersonalized-only egress; art. 12 cross-border consent + Roskomnadzor notification before pilot launch; PDn operator = service legal entity (OQ-11); salon is independent PDn operator of its clients, agent processes on commission (ч.3 ст.6 152-ФЗ); PII-scrubbed logs; legal sign-offs pending for WHO-5/mood as special category (Art. 10), Art. 22 register, Art. 16 threshold effects, crypto-shredding vs destruction.
- **C-4 Scale & shape:** hundreds of masters, a few msg/s peak — scalability is explicitly NOT a Stage-1 driver; team 2–4 engineers; machine-to-machine keys, no OAuth; no K8s, no broker-as-truth, no microservices.
- **C-5 DR:** RPO ≤ 15 min, RTO ≤ 4 h, quarterly restore drill; staging via dedicated test bot.
- **C-6 Tech stack (pinned, final):** Python 3.12+ hexagonal modular monolith, FastAPI + aiogram 3, PostgreSQL 17, Redis 8, docker compose on 2 Yandex Cloud VMs, GitHub private + self-hosted RU runner, pytest + promptfoo. Detail in `stack.md`.

## Non-goals

Stage 1 is explicitly out-of-scope for (from the spine Deferred list + PRD §2.3):

- **5-type motivation-scheme constructor (BRD §11.2)** — backlog; Stage 1 = the 2 Zabot plan types only (avg-check, total-revenue). No tier/rate/bonus config, no percent-base question, no rule engine.
- **Two-way Zabot goals sync (BRD §11.1)** — removed; direction is strictly CRM/Zabot → agent, read-only.
- **Task-queue library (Celery vs Taskiq)** — Postgres-first scheduling is the durability layer; decide only if sweep latency ever matters.
- **Egress mechanism details** (own VM vs ProxyAPI) — OQ-6; `LlmPort` hides the choice.
- **Owner/admin surface beyond a reviewed CLI script** + **"salon administrator" role** — architecture reserves extensibility (AD-7), implementation deferred.
- **Telegram Mini App / own mobile app** — named growth path, RU-hosted when built.
- **pgvector** client-history similarity + **pseudonymization tokens** for egress logs — later hardening (placeholder names are the stage-1 mechanism, AD-5).
- **Multi-provider LLM routing** per message class — `LlmPort` is single-port, swap-ready (AD-2).
- **Horizontal dispatcher / Managed K8s** — SKIP LOCKED already allows N workers; adopt only if load justifies.
- **Memory archival schedule details** — policy shape is AD-15; concrete periods config-driven at pilot calibration; interact with 152-ФЗ retention duties (OQ-3).
- **Adaptive bar attainment-probability method** — OQ-10; corridor shape is fixed, the ~60–70% probability calculation method is open.
- Web portal, marketing site, native iOS/Android app.
- Monetization/pricing/sales motion (OQ-7).
- Agentic LLM behavior, vector similarity search, multi-provider routing.
- New roles beyond master and owner (no salon administrator, platform operator, or support roles at Stage 1).

## Success signal

Stage 1 ends with a 1–2 salon pilot (M3) where:

- **Zero figure-accuracy incidents (CM-4)** — every number in every outgoing message is engine-computed and validator-confirmed (AD-16); a failing message is not sent and a template fallback is queued.
- **Every message is reconstructible from (facts, config_version, prompt_version) — 100% coverage (GM-11).**
- **The 4-consent model + RU-zone residency + Roskomnadzor notification are in place** (launch gates cleared; OQ-3 retention and OQ-11 PDn-operator entity resolved).
- **Recommendation-to-check conversion is measurable automatically from CRM** (GM-9), with no master survey.
- **The psych layer is provably inaccessible to the owner** — only the red-escalation fact + "share of green weeks" aggregate are owner-visible (AD-7).

Numeric GM/CM targets are a config-defined pilot-calibration deliverable, set with the owner at pilot start and reviewed at pilot end (the spec does not invent numbers).

## Assumptions

- **A1** `profile` is a sixth module (research listed five) — master profile, scales, traffic-light state, and consent state live in their own module+schema rather than inside `engines`, keeping coaching state out of pure compute.
- **A2** The depersonalization gateway runs as a component inside the RU zone forwarding to the egress point (own VM abroad OR ruble-billed intermediary); which of the two is open (OQ-6), the port hides it.
- **A3** The canonical CRM entity set (`Master`, `Client`, `Appointment`, `Visit`, `CheckLine`, `VisitComment`) is pending Zabot API field verification (OQ-1 narrowed to field-surface verification).
- **A4** The precise aggregation rule for owner-visible conclusions (aggregate-vs-detail boundary, threshold-defined aggregation) is a config-defined deliverable at pilot (OQ-9).
- **A5** Memory archival/retention periods interact with 152-ФЗ retention duties and are config-defined, pilot-calibrated (OQ-3 remaining).

## Open Questions

The 8 architecture-spine open questions plus 2 PRD-level ones. Full detail (markers, owners, gates) in `open-questions.md`.

- **OQ-1** [narrowed 23.08] Verify Zabot API field surface (plans, checks, bookings, webhooks). **Gates M1.** Owner: Zabot owner.
- **OQ-3** [partially resolved 23.08] PDn retention periods. **Launch gate (Roskomnadzor).** Owner: owner + counsel.
- **OQ-6** Egress mechanism: own foreign VM vs ruble-billed intermediary + model selection. Owner: owner + tech.
- **OQ-10** [уточнить] Adaptive bar ~60–70% attainment-probability method (corridor fixed). Gates bar-engine detail. Owner: owner + tech.
- **OQ-11** [уточнить] PDn operator legal entity name. **Launch gate (Roskomnadzor).** Owner: owner + counsel.
- **OQ-12** [уточнить] BRD §11.3/§11.5 corrections pending scheme-constructor removal. Gates BRD v2.2. Owner: owner + PM.
- **OQ-13** Telegram has no read receipts — engagement KPIs must be answered/ignored-based. Owner: BRD owner.
- **OQ-14** [уточнить] Two-salon master traffic-light CRM-signal aggregation method. Gates traffic-light engine detail (two-salon case only). Owner: tech.
- **OQ-7** (PRD-level) Monetization/pricing/sales motion — must be decided before launch. Owner: owner.
- **OQ-9** (PRD-level) Confidentiality aggregation rule specifics (FR-10.3). Owner: PM + counsel.

## PRD ↔ Spine conflict surface

The PRD (updated 2026-08-23) and the spine (updated 2026-08-23) were co-updated from the same Team Q&A v2.1 change signal, so they are consistent by construction. Verified alignment on: output validator (FR-9.4 = AD-16), sync mechanism (FR-11.5 = AD-3), 2 Zabot plan types (FR-7.4 = AD-3/AD-6), placeholder-name egress (C-1 = AD-5), psych-layer isolation (§3.1/§3.2 = AD-7), dual TZ (NFR-F = AD-8), 4-consent model (FR-1.5 = AD-17), send-side quiet hours + inline keyboards + floor/pause/opt-out (NFR-D/FR-13 = AD-10), single-owner state + consent re-weighting (AD-14), PostgreSQL 17 (C-6 = Stack). **No real disagreement found.** Per the SOLUTION-DESIGN header, the spine wins on any future conflict; a real disagreement means one of them needs updating (the live risk is the BRD v2.2 corrections, OQ-12, or a future change signal diverging them).
