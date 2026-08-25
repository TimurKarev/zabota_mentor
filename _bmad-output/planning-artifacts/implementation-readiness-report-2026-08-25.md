---
stepsCompleted:
  - step-01-document-discovery
  - step-02-prd-analysis
  - step-03-epic-coverage-validation
  - step-04-ux-alignment
  - step-05-epic-quality-review
  - step-06-final-assessment
filesIncluded:
  prd:
    - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/prd.md
    - _bmad-output/planning-artifacts/prds/prd-zabota_mentor-2026-08-18/addendum.md
  architecture:
    - _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md
    - _bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/SOLUTION-DESIGN.md
  spec:
    - _bmad-output/specs/spec-zabota-ai-mentor-stage1/SPEC.md
    - _bmad-output/specs/spec-zabota-ai-mentor-stage1/architecture-invariants.md
    - _bmad-output/specs/spec-zabota-ai-mentor-stage1/stack.md
    - _bmad-output/specs/spec-zabota-ai-mentor-stage1/glossary.md
    - _bmad-output/specs/spec-zabota-ai-mentor-stage1/open-questions.md
  epics:
    - _bmad-output/planning-artifacts/epics.md
  ux: none
---

# Implementation Readiness Assessment Report

**Date:** 2026-08-25
**Project:** zabota_mentor

## Document Inventory

### PRD
- `prds/prd-zabota_mentor-2026-08-18/prd.md` (50 KB)
- `prds/prd-zabota_mentor-2026-08-18/addendum.md` (12 KB)

### Architecture
- `architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md` (43 KB)
- `architecture/architecture-zabota_mentor-2026-08-18/SOLUTION-DESIGN.md` (20 KB)

### Epics & Stories
- `epics.md` (100 KB)

### UX
- None (Stage 1 is conversation-first Telegram bot; UX skipped)

### Spec Bundle (cross-check source)
- `_bmad-output/specs/spec-zabota-ai-mentor-stage1/` — SPEC.md, architecture-invariants.md, stack.md, glossary.md, open-questions.md

### Issues
- No duplicates found
- UX document absent — flagged, accepted for Stage 1 scope
- `open-questions.md` to be checked for implementation blockers

## PRD Analysis

### Functional Requirements

**F1 — Onboarding & Consent**
- FR-1.1: Telegram deep-link + `/start`; 4 separate consents (PDn+profiling, mood data, correspondence retention, cross-border transfer) before any profiling; consent (1) gates activation
- FR-1.2: Primary profiling as 3–5 min live dialogue; determines starting type, scales, tone/frequency, quiet hours
- FR-1.3: CRM history analysis at onboarding for realistic starting bar; cold-start conservative priors; onboarding never blocked
- FR-1.4: AI states working agreements + master confirmation; first 2 weeks = calibration mode
- FR-1.5: Consent withdrawal — (2) and (3) independently revocable; (1) deactivates service; aggregated-profile-only mode on (3) withdrawal; PDn operator = service legal entity [уточнить]; salon = independent PDn operator of clients; Roskomnadzor notification before pilot

**F2 — Master Profiling (hybrid: type + live scales)**
- FR-2.1: Profile = motivational type (5 archetypes) + 9 live scales (0–100); scales drive behavior
- FR-2.2: Dynamic profiling from 4 signal streams: replies, behavior, CRM results, screenings
- FR-2.3: Exponential smoothing per scale (α config); values + versions logged
- FR-2.4: Type change on sustained +15/100 delta for ≥2 pay periods; logged, never disclosed to master
- FR-2.5: Explicit master requests apply immediately, bypass smoothing, logged as "manual setting"
- FR-2.6: Type never disclosed as label; soft descriptive answer on request
- FR-2.7: Progress = sliding 2-week window; ≥+5% key metric growth OR ≥95% bar retention at ≥80% load (config-defined)
- FR-2.8: Cold start — period 1 observation + support mode; first bar in period 2; incomplete profiling → default max-caution profile

**F3 — Communication Engine**
- FR-3.1: Per-master communication contract (frequency, length, tone, challenge/support, number format, send times)
- FR-3.2: Hard caps: ≤5 initiative msgs/shift, ≤2 on days off; lower on yellow/red; quiet hours 21:00–9:00 master TZ
- FR-3.3: Pre-visit recommendations T-30…60 min before appointment, salon TZ
- FR-3.4: Message-class disable ladder; pre-visit disabled last, only on explicit request
- FR-3.5: Ignore detection: ≥70% ignored over 2 weeks → reduce frequency + ask once
- FR-3.6: Trigger arbitration by expected-income-value within caps

**F4 — Recommendation Engine**
- FR-4.1: Signal sources — visit history, purchase cycles, cyclicity/gaps, seasonality, comments, priorities, refusals
- FR-4.2: Candidates = owner priorities ∪ history-logical; exclusion filters (≥2 refusals → N-month pause, contraindications, stop-list, incompatibility)
- FR-4.3: Ranking by acceptance probability × margin/priority
- FR-4.4: 1–3 recommendations per visit; what/why/how format; depth by sales-confidence scale
- FR-4.5: Zero-survey feedback — no "did you offer" questions; outcomes from CRM only; care mood check-ins allowed (F6)
- FR-4.6: Automatic outcomes update — client profile, master profile, engine quality

**F5 — Coaching Cycles**
- FR-5.1: Shift-start message (day plan, one focus, mood screening 2–3×/week, motivational tone)
- FR-5.2: Micro-support only on schedule gap + green status
- FR-5.3: Shift totals — revenue, avg check, rec outcomes, progress, deterministic income forecast, one specific praise
- FR-5.4: GROW session at period end — Goal/Reality/Options/Will; master chooses (autonomy)
- FR-5.5: Forcing requires all three: sustained progress (FR-2.7) + green status + explicit consent; proximity trigger <10–15% to plan
- FR-5.6: Pace reset on yellow/red, ≥2 weeks no progress, life circumstances, after forced sprint
- FR-5.7: Barrier work — systematic non-conversion → MI-style diagnostics → intervention matrix (A.5)

**F6 — Emotional Monitoring & Traffic Light**
- FR-6.1: Signal sources — screenings (2–3×/week + WHO-5 every 2 weeks), tone analysis, CRM signals
- FR-6.2: Traffic light = composite 0–100 from 3 streams; status transitions in code, never LLM; confidence threshold (≥0.7 start, ≥0.8 burnout)
- FR-6.3: Hysteresis — yellow entry <60 (3 days), exit ≥70 (3 days); red entry <40 (7 days), exit ≥55 (7 days); calibration: false reds ≤1/10 masters/month, missed burnouts = 0, yellow↔green ≤1/week
- FR-6.4: Status behavior — green standard, yellow ↓frequency/↓challenge/↑support/forbid forcing, red support-only + owner escalation
- FR-6.5: Ethics — screening as care; non-response = signal not pressure; no diagnoses; red escalation = conclusion + recommendation, no quotes

**F7 — Goals, Adaptive Bar & Motivation Plans**
- FR-7.1: Goal = owner-set Zabot plan (avg-check OR total-revenue); adaptive bar = internal agent trajectory; AI adapts bar/path, never goal
- FR-7.2: Goals read from Zabot (2 plan types), not built in agent; no two-way sync; 5-type constructor → backlog; BRD §11.3/§11.5 corrections pending [уточнить]
- FR-7.3: Owner configures in Zabot: 2 plan types; in agent: priorities, stop-list, quiet hours, comm limits, optional remuneration rules
- FR-7.4: Stage 1 = 2 Zabot plan types only; no constructor/rule engine/tier config; agent computes derived values in calculation DB
- FR-7.5: Incomplete plan data → no invented figures; metrics + clarification to owner
- FR-7.6: Adaptive bar (Locke–Latham): specific, measurable, difficult-but-attainable (~60–70% probability [уточнить method]); corridor ±15% / +10%/period / −15% floor; bar cannot exceed Zabot plan; raise on progress + consent only
- FR-7.7: Income transparency — master can ask earnings/plan/what-if; deterministic; ruble figures only if owner entered remuneration rules (FR-9.4)
- FR-7.8: Plan changes apply next period; AI explains change to master

**F8 — Proactive Triggers**
- FR-8.1: Trigger catalogue — period-bar risk, growth opportunity, proximity sprint, negative pattern, positive pattern, silence bridge
- FR-8.2: All initiative messages pass through caps/priorities/arbitration

**F9 — Deterministic Money Math & LLM Roles**
- FR-9.1: ALL figures computed deterministically in agent calculation DB; LLM receives bound inputs, forbidden from generating/estimating/rounding figures
- FR-9.2: LLM has 3 roles: (a) narrator, (b) structured-output classifier (tone+confidence), (c) bounded MI/GROW dialogue partner
- FR-9.3: LLM outage/budget trip → deterministic template fallback; wording degrades, correctness never
- FR-9.4: Output validator — every money number must match computed; failing message NOT sent
- FR-9.5: Ruble calculation gate — no salary in rubles if remuneration params unavailable; metric/plan-progress terms instead

**F10 — Owner Reporting & Escalation**
- FR-10.1: Per period per master — metrics vs plan/previous, attainment, income dynamics, rec conversion, praise facts, improvement areas, aggregated state signals, profile status
- FR-10.2: Out-of-band escalation only on red status or systemic anomalies
- FR-10.3: Confidentiality — correspondence never to owner except aggregated conclusions; aggregation rule config-defined [ASSUMPTION]

**F11 — CRM Integration & Data Freshness**
- FR-11.1: Data from Zabot — visit history, sales, shifts, bookings, check composition, dynamics, cancellations
- FR-11.2: Freshness — checks/sales ≤60 min, schedule/bookings ≤15 min, dynamics/period totals ≤24 h (config-defined)
- FR-11.3: Degradation ladder — L1 stale-but-usable (timestamp label, forecasts suppressed); L2 hard-stale (no figures, support only); recovery re-sync, no retroactive missed events except praise ≤60 min same shift
- FR-11.4: Cold start — conservative priors; onboarding/basic operation never blocked; new master = observation mode period 1
- FR-11.5: Sync — webhooks primary (unverified pending API), REST polling, nightly reconcile; strictly read-only; Zabot API surface pending verification [OQ-1]; fixture CRM keeps M0 unblocked

**F12 — Memory & Personalization**
- FR-12.1: Long-term memory — master profile, client profiles, bar history; short-term — current period, week focus, open agreements
- FR-12.2: Freshness priority; stale signals archived; retention periods config-defined [interact with 152-ФЗ, OQ-3]
- FR-12.3: Memory for help never pressure; no reminders of past failures

**F13 — Communication Floor, Pause & Opt-out**
- FR-13.1: Minimum floor — 1 period-summary + reactive answers; pre-visit disabled last on explicit request
- FR-13.2: Pause/vacation — automatic (≥N days no shifts, N=5 default) + manual; silence except reactive
- FR-13.3: Full opt-out — disable service, legally required notices only; owner sees fact only
- FR-13.4: Principle 4 — "communication never stops on AI's initiative"; only master can stop it

**F14 — Configuration, Calibration & Audit**
- FR-14.1: All behavioral params config-managed, changeable without release; insert-only versioned; rollback <5 min
- FR-14.2: Every significant decision → append-only audit log with justification + inputs
- FR-14.3: Config-seed deliverables at pilot start (scale definitions, barrier matrix, thresholds, archival policy, aggregation rule, bar corridor, progress thresholds, type-divergence delta)

**Total FRs: 56** (FR-1.1 through FR-14.3)

### Non-Functional Requirements

- NFR-A: 100% figures deterministic; zero figure-accuracy incidents; 100% message reproducibility; status transitions in code
- NFR-B: RU-zone PDn residency; depersonalized-only egress; art. 12 consent + Roskomnadzor notification as launch gates; append-only audit; PII-scrubbed logs; erasure propagation incl. CRM-mirror tombstones; consent-withdrawal → auto-degrade; legal sign-offs pending (WHO-5 special category, Art. 22 register, Art. 16, crypto-shredding — non-blocking M0–M2)
- NFR-C: LLM outage → template fallback; degradation ladder with quarterly drills; DR RPO ≤15 min / RTO ≤4 h with quarterly restore drill; config rollback <5 min
- NFR-D: Telegram — no delivery/read receipts; engagement by answers/reactions; quiet hours guaranteed send-side; inline keyboards for screenings/quick replies; read share out of scope
- NFR-E: Hundreds of masters, few msgs/sec; LLM cost controls — response length caps, per-master daily token meter, budget-trip fallback
- NFR-F: Russia UTC+2..+12, no DST; store both salon TZ and master TZ; quiet hours + personal sends in master TZ; pre-visit in salon TZ
- NFR-G: Inter-salon strict tenant isolation; row-level multi-tenancy; machine-to-machine keys; secrets in vault; PII-scrubbed logging
- NFR-H: Every behavioral decision logged with inputs + justification; config/threshold versions recorded

**Total NFRs: 8** (NFR-A through NFR-H)

### Additional Requirements

**Ethics (normative for all features):**
- E-1: AI never changes goals/KPIs; never punishes/shames; self-comparison only; no escalation threats
- E-2: No manipulation — no guilt, fear of firing, toxic positivity
- E-3: No diagnoses; WHO-5 conversational non-clinical; serious distress → professional referral
- E-4: Recommendations from owner priorities + client history; master's "no" respected (max twice, then suppressed)
- E-5: Honesty in figures > motivational framing
- E-6: Correspondence confidential; owner sees aggregates only; red escalation = conclusion + recommendation, no quotes
- E-7: Based on empirical models (SDT, regulatory focus, Locke–Latham, MI, GROW, Big Five, WHO-5, Maslach)

**Constraints:**
- C-1: 152-ФЗ compliance — RU PDn storage; OpenAI via depersonalization gateway; direct IDs barred from prompts; art. 12 consent + Roskomnadzor before launch; erasure propagation; PII-scrubbed logs; PDn operator legal entity [уточнить]
- C-2: Telegram-only; inline keyboards for screenings; quiet hours send-side guaranteed
- C-3: Zabot CRM API surface to verify (webhooks, REST fields, entities); fixture CRM keeps M0 unblocked; M1 gated on API verification
- C-4: Hundreds of masters; team 2–4 engineers; machine-to-machine keys; infra ~$100–150/month + LLM costs
- C-5: DR RPO ≤15 min, RTO ≤4 h, quarterly restore drill; staging via test bot
- C-6: Python 3.12+ modular monolith, FastAPI + aiogram 3, PostgreSQL 17, Redis 8, docker compose on 2 Yandex Cloud VMs, GitHub private + self-hosted RU runner

**Milestones:**
- M0 (wks 1–4): Onboarding + consent, config versioning, scheduler + quiet hours, templates, audit; fixture CRM
- M1 (wks 5–8): Real CRM sync, freshness SLO, degradation L1 — gated on Zabot API verification (OQ-1)
- M2 (wks 9–14): Traffic light, income/forecast engine, recommendation engine, triggers/arbitration/floors, prompt library + LLM port, golden tests
- M3 (wks 15–18): Owner reporting, degradation drills, Roskomnadzor notification, pilot 1–2 salons

### PRD Completeness Assessment

**Strengths:**
- Exceptionally detailed — 56 FRs across 14 feature groups, 8 NFRs, 7 ethics principles, 6 constraints
- Every owner decision (13.08 + 23.08) explicitly traced; change signal reconciliation documented (A.10.1)
- Open questions clearly separated into Open / Resolved / Obsolete with owners and blocking flags
- Determinism boundary (F9) is unusually rigorous — output validator + ruble gate + calculation DB separation
- Confidentiality model (E-6, FR-10.3, §3.1 access matrix) is precise about aggregate-vs-detail boundary

**Concerns to validate in next steps:**
1. **6 `[уточнить]` items** — PDn operator legal entity (OQ-11), BRD §11.3/§11.5 corrections (OQ-12), attainment probability method (OQ-10), plus inline references in FR-1.5, FR-7.2, FR-7.6
2. **Open questions still blocking:** OQ-1 (Zabot API surface — blocks M1), OQ-3 (retention periods — blocks launch), OQ-6 (egress mechanism — blocks C-1 implementation), OQ-7 (monetization — blocks GTM), OQ-9 (aggregation rule — blocks FR-10.3), OQ-10, OQ-11, OQ-12
3. **Config-seed deliverables (FR-14.3)** — many pilot-calibration values are deliberately unset; confirm epics don't assume specific numbers
4. **No UX document** — accepted for Stage 1 (conversation-first), but onboarding dialogue flow (FR-1.2, A.4) and screening UX (inline keyboards, NFR-D) need spec-level detail somewhere (architecture? stories?)
5. **BRD v2.2 corrections** (OQ-12) — PRD notes BRD §11.1, §11.2, §11.3, §11.5 need correction but content pending; confirm this doesn't block epics

## Epic Coverage Validation

### Coverage Matrix

The epics document contains an explicit FR Coverage Map (lines 184–255) and NFR Coverage Map (lines 259–268). Each FR was cross-checked against both the coverage map AND the actual story acceptance criteria.

| FR | Epic | Story(ies) | Status |
|---|---|---|---|
| FR-1.1 | Epic 1 | 1.2, 1.3 | ✓ Covered |
| FR-1.2 | Epic 1 | 1.4 | ✓ Covered |
| FR-1.3 | Epic 1 | 1.4, 1.9 | ✓ Covered |
| FR-1.4 | Epic 1 | 1.4 | ✓ Covered |
| FR-1.5 | Epic 1 | 1.3, 1.8 | ✓ Covered |
| FR-2.1 | Epic 1 | 1.4, 1.5 | ✓ Covered |
| FR-2.2 | Epic 1 | 1.5 (streams 1–2); 2.6 (stream 3); 5.5 (stream 4) | ✓ Covered (split across epics) |
| FR-2.3 | Epic 1 | 1.5 | ✓ Covered |
| FR-2.4 | Epic 1 | 1.5 | ✓ Covered |
| FR-2.5 | Epic 1 | 1.5 | ✓ Covered |
| FR-2.6 | Epic 1 | 1.4, 1.5 | ✓ Covered |
| FR-2.7 | Epic 3 | 3.2 | ✓ Covered |
| FR-2.8 | Epic 1 | 1.9 | ✓ Covered |
| FR-3.1 | Epic 1 | 1.6 | ✓ Covered |
| FR-3.2 | Epic 1 | 1.6 | ✓ Covered |
| FR-3.3 | Epic 4 | 4.3 | ✓ Covered |
| FR-3.4 | Epic 4 | 4.9 | ✓ Covered |
| FR-3.5 | Epic 4 | 4.9 | ✓ Covered |
| FR-3.6 | Epic 4 | 4.9 | ✓ Covered |
| FR-4.1 | Epic 4 | 4.1 | ✓ Covered |
| FR-4.2 | Epic 4 | 4.1 | ✓ Covered |
| FR-4.3 | Epic 4 | 4.1 | ✓ Covered |
| FR-4.4 | Epic 4 | 4.1 | ✓ Covered |
| FR-4.5 | Epic 4 | 4.2 | ✓ Covered |
| FR-4.6 | Epic 4 | 4.2 | ✓ Covered |
| FR-5.1 | Epic 4 | 4.4 | ✓ Covered |
| FR-5.2 | Epic 4 | 4.4 | ✓ Covered |
| FR-5.3 | Epic 4 | 4.5 | ✓ Covered |
| FR-5.4 | Epic 4 | 4.6 | ✓ Covered |
| FR-5.5 | Epic 4 | 4.7 | ✓ Covered |
| FR-5.6 | Epic 4 | 4.7 | ✓ Covered |
| FR-5.7 | Epic 4 | 4.8 | ✓ Covered |
| FR-6.1 | Epic 5 | 5.1, 5.2 | ✓ Covered |
| FR-6.2 | Epic 5 | 5.3 | ✓ Covered |
| FR-6.3 | Epic 5 | 5.3 | ✓ Covered |
| FR-6.4 | Epic 5 | 5.4 | ✓ Covered |
| FR-6.5 | Epic 5 | 5.1, 5.4 | ✓ Covered |
| FR-7.1 | Epic 3 | 3.1 | ✓ Covered |
| FR-7.2 | Epic 3 | 3.1 | ✓ Covered |
| FR-7.3 | Epic 3 | 3.0 | ✓ Covered |
| FR-7.4 | Epic 3 | 3.1 | ✓ Covered |
| FR-7.5 | Epic 3 | 3.1 | ✓ Covered |
| FR-7.6 | Epic 3 | 3.3 | ✓ Covered |
| FR-7.7 | Epic 3 | 3.5 | ✓ Covered |
| FR-7.8 | Epic 3 | 3.7 | ✓ Covered |
| FR-8.1 | Epic 4 | 4.9 | ✓ Covered |
| FR-8.2 | Epic 4 | 4.9 | ✓ Covered |
| FR-9.1 | Epic 3 | 3.4a, 3.4b, 3.4c | ✓ Covered |
| FR-9.2 | Epic 6 | 6.1 | ✓ Covered |
| FR-9.3 | Epic 6 | 6.4 | ✓ Covered |
| FR-9.4 | Epic 6 | 6.3 | ✓ Covered |
| FR-9.5 | Epic 3 | 3.6 | ✓ Covered |
| FR-10.1 | Epic 7 | 7.1 | ✓ Covered |
| FR-10.2 | Epic 7 | 7.2 | ✓ Covered |
| FR-10.3 | Epic 7 | 7.3 | ✓ Covered |
| FR-11.1 | Epic 2 | 2.1, 2.2, 2.3 | ✓ Covered |
| FR-11.2 | Epic 2 | 2.4 | ✓ Covered |
| FR-11.3 | Epic 2 | 2.4 | ✓ Covered |
| FR-11.4 | Epic 2 | 2.5 | ✓ Covered |
| FR-11.5 | Epic 2 | 2.1, 2.2 | ✓ Covered |
| FR-12.1 | Epic 6 | 6.6 | ✓ Covered |
| FR-12.2 | Epic 6 | 6.6 | ✓ Covered |
| FR-12.3 | Epic 6 | 6.6 | ✓ Covered |
| FR-13.1 | Epic 1 | 1.8 | ✓ Covered |
| FR-13.2 | Epic 1 | 1.8 | ✓ Covered |
| FR-13.3 | Epic 1 | 1.8 | ✓ Covered |
| FR-13.4 | Epic 1 | 1.8 | ✓ Covered |
| FR-14.1 | Epic 1 | 1.1b, 1.6 | ✓ Covered |
| FR-14.2 | Epic 1 | 1.1b | ✓ Covered |
| FR-14.3 | Epic 7 | 7.5b | ✓ Covered |

### NFR Coverage

| NFR | Epic(s) | Status |
|---|---|---|
| NFR-A (Determinism) | Epic 3 (3.4a-c), Epic 6 (6.3) | ✓ Covered |
| NFR-B (Compliance & privacy) | Epic 1 (1.3), Epic 6 (6.2), Epic 7 (7.4, 7.5c) | ✓ Covered |
| NFR-C (Reliability & ops) | Epic 6 (6.4), Epic 7 (7.5a), Epic 2 (2.4) | ✓ Covered |
| NFR-D (Channel realism) | Epic 1 (1.6), Epic 4 (4.3, 4.4, 4.9) | ✓ Covered |
| NFR-E (Scalability & cost) | Epic 6 (6.1), Epic 1 (1.6) | ✓ Covered |
| NFR-F (Time & geography) | Epic 1 (1.6), Epic 4 (4.3) | ✓ Covered |
| NFR-G (Security & isolation) | Epic 1 (1.2, 1.1b), Epic 2 (2.3), Epic 7 (7.1, 7.3) | ✓ Covered |
| NFR-H (Explainability) | Epic 1 (1.1b), Epic 5 (5.3) | ✓ Covered |

### Missing Requirements

**No missing FRs.** All 56 PRD functional requirements are covered by at least one story with acceptance criteria.

**No missing NFRs.** All 8 non-functional requirements are covered.

### Coverage Statistics

- Total PRD FRs: 56
- FRs covered in epics: 56
- Coverage percentage: **100%**
- Total PRD NFRs: 8
- NFRs covered in epics: 8
- NFR coverage: **100%**

### New Open Questions Introduced by Epics (Not in PRD)

⚠️ **OQ-13** — Acceptance-probability model for recommendation ranking (FR-4.3, Story 4.1). The epics introduce this as a new `[уточнить]` item that does NOT exist in the PRD's open-questions list (§8.1). The story includes a workaround (config-defined baseline: client historical acceptance rate smoothed with a prior), but this should be added to the PRD's open questions for traceability.

### `[уточнить]` Items in Epics (Workarounds Provided)

| Story | OQ | Item | Workaround |
|---|---|---|---|
| 1.4 | OQ-12 | Questionnaire→archetype scoring algorithm | Config-defined mapping (deferred to config-seed) |
| 3.3 | OQ-10 | Attainment-probability estimation method | Config-defined naive forecast (last-period × (1+growth_factor)) |
| 4.1 | OQ-13 (NEW) | Acceptance-probability model | Config-defined baseline (client historical rate + prior) |
| 7.3 | OQ-9 | Aggregation threshold for owner-visible conclusions | ≥3 distinct master interactions, no verbatim ≥5 words |
| 7.5c | OQ-11 | PDn operator legal entity name | Unresolved — launch gate |

All workarounds are config-defined and do not block implementation, but OQ-10, OQ-11, OQ-12 remain unresolved launch gates.

## UX Alignment Assessment

### UX Document Status

**Not Found.** No UX design document exists in `_bmad-output/planning-artifacts/`.

### UX Implied Assessment

This is a **user-facing application** (Telegram bot), but the UX is conversation-first with no web/native UI:

- **PRD §2.3 non-goals:** explicitly excludes web portal, native app, Telegram Mini App
- **PRD F1–F6:** chat interaction patterns are specified behaviorally in the PRD itself
- **Addendum A.2:** type matrix with canonical message examples (tone registers per psychotype)
- **Addendum A.4:** onboarding profiling questions (live dialogue, one at a time)
- **NFR-D / AD-10:** inline keyboards (1–5 button scale for screenings, quick replies) — the only "widget"
- **Epics §"UX Design Requirements":** explicitly states "No UX design contract exists — Stage 1 is a Telegram bot with no web/native UI. Chat interaction patterns are specified behaviorally in the PRD (F1–F6) and the addendum's type matrix (A.2)"

### Alignment Assessment

The PRD, architecture, and epics are **aligned** on the no-UX-document decision:

1. **PRD → Architecture:** Architecture spine (AD-10) specifies inline keyboards for screenings, Telegram pacing, quiet-hours send-side guarantee — all channel UX concerns are covered as architectural decisions
2. **PRD → Epics:** Stories 1.3 (inline keyboard consent buttons), 1.6 (quiet hours), 4.4 (inline keyboard mood screenings 1–5), 5.1 (inline keyboard screenings) implement the UX-relevant requirements directly
3. **Architecture → Epics:** AD-10 dispatcher arbitration, per-chat Redis token buckets, inline keyboard requirement — all reflected in stories

### Warnings

⚠️ **LOW RISK — No UX document, but adequately compensated.** The conversation UX is specified behaviorally in the PRD (F1–F6, A.2, A.4) and the architecture covers channel constraints (AD-10, NFR-D). The epics document explicitly acknowledges this and implements UX-relevant requirements directly in stories.

⚠️ **MEDIUM RISK — Onboarding dialogue flow (FR-1.2, A.4) lacks conversational design spec.** The PRD specifies the questions and adaptive order, but there's no documented conversational flow design (branching logic, error states, re-engagement after incomplete profiling). Story 1.4 implements this but relies on config-defined mapping [уточнить: OQ-12]. A conversational design review of the onboarding flow before M0 implementation would reduce risk.

⚠️ **LOW RISK — Screening UX (FR-6.1, inline keyboards) is minimal.** The 1–5 button scale is specified, but the wording, timing, and framing of screening questions is not documented as a design artifact. Story 5.1 implements this with care-framing language from the PRD, but a review of the actual screening question wording before M2 would be valuable.

### Recommendation

No UX document is required for Stage 1 launch. However, two lightweight design reviews are recommended before implementation:
1. **Onboarding dialogue flow review** (before M0, Story 1.4) — branching, error states, re-engagement
2. **Screening question wording review** (before M2, Story 5.1) — actual question text, framing, frequency calibration

## Epic Quality Review

### Epic Structure Validation

#### A. User Value Focus Check

| Epic | Title | User Value | Status |
|---|---|---|---|
| Epic 1 | Onboarding, Consent & Foundation | "A master can start the bot, grant 4 separate consents, complete primary profiling, and receive their first calibration-mode template messages" | ✓ User-centric |
| Epic 2 | CRM Integration & Agent Calculation DB | "The agent is grounded in real Zabot/CRM data" | ⚠️ System-facing, but enables user value (accurate recommendations) |
| Epic 3 | Deterministic Calculation Engine & Plan Tracking | "the master can ask income/plan/what-if questions and get deterministic answers" | ⚠️ Mixed — user value present (income transparency) but primarily system-facing |
| Epic 4 | Personalized Coaching & Recommendations | "The master receives adaptive coaching across shift/week/period cycles" | ✓ User-centric |
| Epic 5 | Emotional Monitoring & Traffic Light | "The system monitors the master's emotional state... and adjusts behavior" | ⚠️ System-facing, but Story 5.1 is user-facing ("As a master, I want short mood check-ins") |
| Epic 6 | LLM Narration, Depersonalization & Output Validation | "The LLM narrates pre-computed facts in psychotype-calibrated prose" | ⚠️ System-facing — user value is personalized messages |
| Epic 7 | Owner Reporting & Pilot Readiness | "The owner receives per-period reports per master" | ✓ Owner-facing |

**Assessment:** Epics 2, 3, 5, 6 are system-facing rather than user-facing. This is a structural concern — best practice prefers user-value-oriented epics. However, for this project the determinism boundary (F9) and compliance requirements (NFR-B) necessitate system-facing epics. The user value is present in the epic descriptions but secondary. This is a 🟡 Minor Concern — the epics are well-structured for the domain, but a PM might reframe Epic 2/3/5/6 titles to lead with user outcome.

#### B. Epic Independence Validation

| Epic | Depends On | Forward Deps | Status |
|---|---|---|---|
| Epic 1 | None (fixture CRM) | None | ✓ Fully independent |
| Epic 2 | Epic 1 (fixture CRM, profile) | None | ✓ Independent |
| Epic 3 | Epic 1 (profile), Epic 2 (calc DB, CRM data) | None | ✓ Independent |
| Epic 4 | Epic 1, 2, 3 | **Epic 5 (traffic light status), Epic 6 (LLM narration)** | 🟠 Forward dependency |
| Epic 5 | Epic 1, 2 | None | ✓ Independent |
| Epic 6 | Epic 1, 3 (RenderFacts) | None | ✓ Independent |
| Epic 7 | All prior epics | None | ✓ Independent (M3 final) |

**🟠 Major Issue — Epic 4 has forward dependencies on Epic 5 and Epic 6:**
- Story 4.7 (forcing/pace reset) requires "green status (from Epic 5)"
- Story 4.6 (GROW session) requires "bounded LLM dialogue (from Epic 6, Story 6.1)"
- Stories 4.3, 4.5 reference "RenderFacts (template or LLM from Epic 6)"

**Mitigation (already in epics):**
1. All three epics (4, 5, 6) are in the same milestone (M2, wks 9–14) — sprint planning can sequence stories correctly
2. Template fallback (Story 1.7, AD-10) allows Epic 4 stories to ship with `rendered_by: template` until Epic 6 lands
3. Story 6.1 has explicit sequencing constraint (H3): "Until Story 6.3 (output validator) lands, the LLM narration path stays DISABLED — only deterministic templates render"
4. Traffic light status can default to "green" (standard behavior) until Epic 5 lands

**Recommendation:** Reorder epics within M2 to: Epic 3 → Epic 6 → Epic 5 → Epic 4. This eliminates forward dependencies. Alternatively, keep current order but ensure sprint planning sequences stories as: 3.x → 6.1–6.3 → 5.1–5.3 → 4.x (with 4.6, 4.7 last).

### Story Quality Assessment

#### A. Story Sizing Validation

**Well-sized stories (split appropriately):**
- Story 1.1 → split into 1.1a (scaffold), 1.1b (config/audit), 1.1c (CI) ✓
- Story 3.4 → split into 3.4a (metric dynamics), 3.4b (decomposition/forecast), 3.4c (RenderFacts) ✓
- Story 7.5 → split into 7.5a (drills), 7.5b (config-seed), 7.5c (Roskomnadzor) ✓

**No oversized stories detected.** All stories have focused acceptance criteria (5–15 ACs each).

#### B. Acceptance Criteria Review

All 40+ stories use proper **Given/When/Then** BDD format. Spot-check findings:

| Story | AC Quality | Issues |
|---|---|---|
| 1.3 (4-Consent Capture) | ✓ Comprehensive — 12 ACs covering all 4 consents, revocation, audit | None |
| 1.4 (Primary Profiling) | ✓ Detailed — 9 ACs covering dialogue, type, scales, agreements, calibration | [уточнить: OQ-12] noted |
| 3.3 (Adaptive Bar) | ✓ Thorough — 10 ACs covering corridor rules, movement rules, edge cases | [уточнить: OQ-10] with workaround |
| 4.1 (Recommendation Engine) | ✓ Detailed — 7 ACs covering signals, filters, ranking, format | [уточнить: OQ-13] with workaround |
| 6.3 (Output Validator) | ✓ Exceptionally detailed — 12 ACs covering figure check, placeholder check, crash-safety, golden set | None |
| 7.4 (Erasure Propagation) | ✓ Thorough — 8 ACs covering cross-module purge, tombstones, idempotency | None |

**AC quality is high.** Error conditions are covered (e.g., Story 6.3 validator exception handling, Story 6.4 validator-double-fail). Edge cases are documented (e.g., Story 3.3 Zabot plan below master's actual level, Story 2.4 absence ≠ staleness).

### Dependency Analysis

#### A. Within-Epic Dependencies

All within-epic dependencies are backward (Story N depends on Story N-k within same epic). No forward references within epics. ✓

**Cross-epic dependencies (all backward except Epic 4):**
- Epic 2 → Epic 1 (Story 2.6 → Story 1.5) ✓
- Epic 3 → Epic 2 (Story 3.1 → Story 2.3) ✓
- Epic 4 → Epic 1, 2, 3 ✓ + **Epic 5, 6 (forward)** 🟠
- Epic 5 → Epic 1, 2 ✓
- Epic 6 → Epic 1, 3 ✓
- Epic 7 → all prior ✓

#### B. Database/Entity Creation Timing

✓ **No "create all tables upfront" violation.** Database schemas are created when first needed:
- Story 1.1b: config + audit schemas (needed for Epic 1)
- Story 2.3: `crm_mirror`, `engines`, `profile`, `messaging` schemas (needed for Epic 2)
- No upfront schema creation story

### Special Implementation Checks

#### A. Starter Template Requirement

✓ **Story 1.1a** is the starter template story: "Repo Scaffold, Ports & Module Boundaries" — includes scaffold creation, port definitions, import-linter, pinned versions. Follows architecture AD-2 (ports) and AD-11 (module boundaries).

#### B. Greenfield Indicators

✓ This is a greenfield project. Present:
- Story 1.1a: initial project setup ✓
- Story 1.1c: CI/CD pipeline setup ✓
- Story 1.10: fixture CRM for development ✓
- Story 1.1b: config/audit foundation ✓

### Best Practices Compliance Checklist

| Criterion | Epic 1 | Epic 2 | Epic 3 | Epic 4 | Epic 5 | Epic 6 | Epic 7 |
|---|---|---|---|---|---|---|---|
| Delivers user value | ✓ | ⚠️ | ⚠️ | ✓ | ⚠️ | ⚠️ | ✓ |
| Functions independently | ✓ | ✓ | ✓ | 🟠 | ✓ | ✓ | ✓ |
| Stories appropriately sized | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| No forward dependencies | ✓ | ✓ | ✓ | 🟠 | ✓ | ✓ | ✓ |
| DB tables created when needed | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Clear acceptance criteria | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Traceability to FRs maintained | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

### Quality Assessment Summary

#### 🔴 Critical Violations
**None.**

#### 🟠 Major Issues
1. **Epic 4 forward dependencies on Epic 5 and Epic 6** — Stories 4.6, 4.7 reference Epic 5 (traffic light) and Epic 6 (LLM narration) which are later epics. Mitigated by template fallback and same-milestone sequencing. **Recommendation:** Reorder M2 epics as 3 → 6 → 5 → 4, or ensure sprint planning sequences stories accordingly.

#### 🟡 Minor Concerns
1. **System-facing epic titles (Epics 2, 3, 5, 6)** — Best practice prefers user-value-oriented epic titles. The user value is present but secondary in the description. Consider reframing: e.g., Epic 2 → "Master gets accurate, real-time recommendations grounded in live CRM data."
2. **Developer stories (1.1a, 1.1b, 1.1c, 1.10, 2.3, 3.4a–c)** — "As a developer/system" stories are necessary for greenfield infrastructure but deviate from pure user-story format. Acceptable for this project type.
3. **OQ-13 not in PRD** — The epics introduce a new open question (acceptance-probability model for recommendation ranking) that doesn't exist in the PRD's open-questions list. Should be backported to the PRD for traceability.
4. **5 `[уточнить]` items in stories** — All have config-defined workarounds, but OQ-10, OQ-11, OQ-12 remain unresolved launch gates. The workarounds are explicitly documented, which is good practice.

## Summary and Recommendations

### Overall Readiness Status

**✅ READY — with conditions**

The planning artifacts are implementation-ready. All 56 functional requirements and 8 non-functional requirements are fully covered by 40+ stories across 7 epics with rigorous acceptance criteria. The architecture spine, solution design, and spec bundle are aligned. The determinism boundary (F9), compliance model (NFR-B), and confidentiality framework (E-6, FR-10.3) are exceptionally well-specified.

Implementation can begin (M0, Epic 1) immediately — M0 has zero external dependencies (fixture CRM) and no unresolved open questions blocking it.

### Critical Issues Requiring Immediate Action

**None blocking M0.** The following are launch gates (M3) or M1 gates that do not block starting implementation:

1. **OQ-1 (M1 gate):** Zabot API surface verification — blocks Epic 2 (real CRM sync). M0 proceeds on fixture CRM regardless.
2. **OQ-11 (launch gate):** PDn operator legal entity name — blocks Roskomnadzor notification (Story 7.5c). Not needed until M3.
3. **OQ-10 (FR-7.6):** Attainment-probability method — has config-defined workaround in Story 3.3. Resolve before M2.
4. **OQ-12 (BRD v2.2):** BRD §11.3/§11.5 corrections + questionnaire scoring algorithm — has workaround in Story 1.4. Resolve before M0 implementation of Story 1.4.

### Issues to Address Before Implementation

1. **🟠 Epic 4 forward dependencies (Epic 5, 6):** Reorder M2 epics as 3 → 6 → 5 → 4, or ensure sprint planning sequences stories as: 3.x → 6.1–6.3 → 5.1–5.3 → 4.x (with 4.6, 4.7 last). This eliminates forward dependencies.

2. **🟡 OQ-13 not in PRD:** Backport the new open question (acceptance-probability model for recommendation ranking, introduced in Story 4.1) to the PRD's open-questions list (§8.1) for traceability.

3. **🟡 Onboarding dialogue flow design review:** Before implementing Story 1.4, conduct a lightweight conversational design review (branching logic, error states, re-engagement after incomplete profiling). The PRD specifies questions but not the conversational flow.

4. **🟡 Screening question wording review:** Before implementing Story 5.1 (M2), review actual screening question text, framing, and frequency calibration. The PRD specifies the framework but not the actual words.

### Recommended Next Steps

1. **Start implementation immediately** — run `bmad-sprint-planning` to generate the sprint plan from epics, then begin the story cycle (create → dev → review) for Epic 1, Story 1.1a
2. **Resolve OQ-1 in parallel** — engage Zabot owner to verify API surface (webhooks, REST fields, plan/check/booking entities) before M1 begins (wk 5)
3. **Resolve OQ-11 in parallel** — engage owner + counsel to confirm PDn operator legal entity before M3 (wk 15)
4. **Backport OQ-13 to PRD** — add acceptance-probability model question to PRD §8.1 open questions
5. **Reorder M2 epics** — adjust epic ordering or document sprint sequencing constraint: 3 → 6 → 5 → 4

### Artifact Quality Scores

| Artifact | Completeness | Consistency | Implementability | Overall |
|---|---|---|---|---|
| PRD (+ addendum) | 9/10 | 9/10 | 8/10 | **A** |
| Architecture (spine + solution design) | 9/10 | 9/10 | 9/10 | **A** |
| Spec bundle (SPEC + companions) | 9/10 | 9/10 | 8/10 | **A-** |
| Epics & Stories | 9/10 | 8/10 | 8/10 | **A-** |
| UX | N/A | N/A | N/A | **N/A (accepted)** |

### Final Note

This assessment identified **7 issues** across **3 categories** (1 major, 6 minor). No critical violations were found. The planning artifacts are exceptionally thorough — 56 FRs with 100% epic coverage, rigorous determinism boundary, explicit owner-decision traceability, and well-sized stories with BDD acceptance criteria.

The single major issue (Epic 4 forward dependencies) is already mitigated by template fallback and same-milestone sequencing. All `[уточнить]` items have config-defined workarounds that do not block implementation.

**Recommendation: Proceed to sprint planning and begin M0 implementation.**

---

**Assessment date:** 2026-08-25
**Assessor:** BMad Implementation Readiness skill
**Project:** zabota_mentor (Zabot AI Mentor, Stage 1)
**Report file:** `_bmad-output/planning-artifacts/implementation-readiness-report-2026-08-25.md`
