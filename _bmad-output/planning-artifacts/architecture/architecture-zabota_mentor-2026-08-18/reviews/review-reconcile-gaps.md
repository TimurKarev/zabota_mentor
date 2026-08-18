# Reconcile Review — Gap Report vs Architecture Spine

**Reviewer:** reconcile reviewer (architecture spine) · **Date:** 2026-08-18
**Inputs:**
- Gap/contradiction report: `_bmad-output/planning-artifacts/zabot-ai-gap-contradiction-report.md` (Mary, 2026-08-10, against BRD v2.0)
- Spine: `_bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md` (2026-08-18, cites BRD **v2.1** with owner decisions 13.08.2026)

**Method:** For each gap-report finding (B1–B5, I1–I10, N1–N6), classify the spine's treatment as:

- **RESOLVED** — the spine settles it architecturally, at spine altitude.
- **CARRIED** — the spine explicitly holds it as an open question (Q1–Q4), deferred item, or hedged assumption — and does **not** claim resolution.
- **PARTIAL** — the architectural mechanism exists but a named sub-issue is untouched.
- **SILENT** — the finding (or a load-bearing part of it) is neither resolved, carried, nor deferred.

A special check the task demands: the spine must not claim resolution of still-open items (consent model, salon isolation) and must address the named blocking items (money/LLM boundary, CRM contract, 152-ФЗ).

**Caveat:** the gap report analyzed BRD v2.0; the spine cites BRD v2.1 plus owner decisions of 13.08.2026 (which postdate the report). Some gaps may have been closed upstream in the BRD (e.g., §5.2.1 freshness `[ADOPTED]`, §13.1 residency decision). This review can only verify what the spine itself shows; where a gap is "SILENT," the fix may be either an owner decision recorded in the BRD or an explicit open question in the spine — but one of those must exist.

---

## Verdict

**CONDITIONAL PASS.** The spine is honest and largely disciplined: it resolves exactly the right blocking items (money/LLM boundary via AD-1, CRM contract architecture via AD-3/AD-9/Q1, 152-ФЗ via AD-5), and it explicitly carries consent (Q3) and salon isolation/roles (Q2) as open questions with hedging assumptions (`[ASSUMPTION]` consent state, AD-7 schema hedge). **No false-resolution claims were found.** However, one BLOCKING-tier gap sub-item (bi-directional goals sync) and one BLOCKING-tier gap (B5, scheme taxonomy) are silently dropped rather than resolved or carried, plus a handful of IMPORTANT items (cold-start, retention schedule, consent-revocation semantics, GROW gate on proactive triggers) receive no architectural home. Conditions for pass are in the findings below.

---

## Reconciliation matrix

| ID | Gap-report finding (tier) | Spine treatment | Evidence in spine | Classification |
|---|---|---|---|---|
| B1 | Actors/permission model absent (BLOCKING) | Salon-scoped rows from day one; identity = `chat_id`, machine-to-machine API keys; role model explicitly open | AD-7, Conventions (Identity), Q2 | **CARRIED** (correct) |
| B2 | CRM integration contract undefined (BLOCKING) | Canonical model + anti-corruption layer, watermark polling, deletes by snapshot, fixture CRM as contract tests, freshness SLOs, degradation ladder; CRM surface open | AD-3, AD-9, Q1 | **PARTIAL** — bi-directional goals sync sub-item is SILENT (see H-1) |
| B3 | Money/LLM separation (BLOCKING) | Deterministic engines compute every figure; LLM gets bound variables, may not emit figures; enforced structurally + promptfoo golden tests | AD-1, Capability map (§11 → engines + config) | **RESOLVED** |
| B4 | 152-ФЗ provider/localization/consent (BLOCKING) | Two-zone residency, RU zone holds all PDn, depersonalization gateway before egress, art. 12 consent + Roskomnadzor notification as launch gates; consent triad open; egress mechanism open | AD-5 `[ADOPTED]`, Q3, Q4 | **PARTIAL** — retention/deletion schedule absent (M-3) |
| B5 | Motivation-scheme taxonomy empty (BLOCKING) | Scheme *coefficients* are versioned config rows; but no taxonomy, no fixed-set-vs-rule-engine decision, not an open question | AD-6 ("motivation-scheme coefficients") | **SILENT** (H-2) |
| I1 | Four empty control tables (IMPORTANT) | Traffic light = deterministic scoring entity with config-driven hysteresis entry/exit; third rhythm identified (shift/week/period); scales' α and composite weights config-owned; barrier→intervention matrix absent | AD-6, Capability map (§9 cycles, §10 traffic light) | **PARTIAL** (M-4) |
| I2 | Motivational types list + type→defaults (IMPORTANT) | Types live in `profile`; no type→default-settings mapping anywhere | Capability map (§6) | **SILENT**, content-level (L-1) |
| I3 | Proactivity trigger catalogue (IMPORTANT) | Dispatcher arbitration, priority, caps, throttle; trigger offsets in config; catalogue itself not authored or carried | AD-10, AD-6 | **PARTIAL**, content-level (L-2) |
| I4 | "Zero surveys" vs mood screenings (IMPORTANT) | Not addressed — BRD wording contradiction, not architectural | — | Acceptable SILENT (L-3) |
| I5 | "Never stops" vs no opt-out (IMPORTANT) | Frequency caps **and floors** in config; disable ladder (period totals/pre-visit last); "write less often" immediate; ignore-rate → minimum; revocation mechanism open via Q3 | AD-6, AD-10, Q3 | **PARTIAL** — pause/opt-out operational semantics undefined (M-2) |
| I6 | Goal vs adaptive bar contradiction (IMPORTANT) | Bar logic owned by engines; owner-set parameters in versioned config; terminology not adjudicated (BRD-level) | Capability map (§11) | Acceptable SILENT (L-4) |
| I7 | Profiling math undefined (IMPORTANT) | Smoothing α, weights, tone-confidence thresholds, hysteresis all versioned-config with reproducibility (`config_version` on score rows); "progress" definition and normalization absent | AD-6 | **PARTIAL**, engine-level detail (L-5) |
| I8 | Type↔scale mapping (IMPORTANT) | Not addressed; `profile` owns both but no mapping/recomputation rule | Module table | **SILENT**, engine-level (L-6) |
| I9 | Multi-timezone model (IMPORTANT) | UTC storage, local evaluation at send-decision time, injectable `Clock`, 11 static zones named | AD-8, AD-2, Conventions (Time) | **RESOLVED** |
| I10 | Cold-start/missing-data fallbacks (IMPORTANT) | AD-9 covers *staleness/outage* degradation, not *absence* (new master/salon/client, no history); no fallback states defined anywhere | AD-9 (staleness only) | **SILENT** (M-1) |
| N1 | Scientific-basis list (NICE) | Not addressed; not architectural | — | Acceptable SILENT |
| N2 | Glossary empty (NICE) | Not addressed; not architectural | — | Acceptable SILENT |
| N3 | Telegram channel constraints (NICE) | aiogram 3, per-chat token buckets, quiet-hours miss → defer to next window; delivery-receipt caveat not noted | Stack, AD-10, Conventions | **PARTIAL** (L-7) |
| N4 | GROW consent gate vs automated triggers (NICE) | Dispatcher owns trigger arbitration but no consent gate on force/sprint-class triggers | AD-10 | **SILENT** (M-5) |
| N5 | "Aggregate vs detail" boundary definition (NICE) | Carried as a rule label ("aggregate only, no quotes") but no enforceable definition (thresholds, no verbatim) | Capability map (§14) | **PARTIAL** (M-6) |
| N6 | KPIs reference undefined inputs (NICE) | Not addressed; downstream of I1/B5 | — | Acceptable SILENT |

### Special checks required by the review charter

- **No claimed resolution of open items.** PASS. Consent: Q3 open, `profile` consent state marked `[ASSUMPTION]`, AD-5 lists consent/notification as *launch gates*, not as done. Salon isolation: Q2 open, AD-7 explicitly hedges ("whatever role model lands"). No AD or table row asserts these are settled.
- **Money/LLM boundary addressed.** PASS — AD-1 is a direct, structural implementation of the gap report's recommended rule, down to bound variables and CI golden tests.
- **CRM contract addressed.** PASS at architecture altitude — AD-3 (transport, entities, idempotency-by-watermark, deletes, contract tests) + AD-9 (freshness SLA + degradation) + Q1 (surface unknowns). One sub-item missing: see H-1.
- **152-ФЗ addressed.** PASS — AD-5 `[ADOPTED]` covers localization, depersonalization boundary, cross-border legal basis; Q3/Q4 carry the remainder. Note the spine legitimately diverges from the report's "in-RF provider default" recommendation by choosing a foreign model behind a depersonalization gateway under art. 12 — this satisfies the report's own conditional ("if a foreign model is contemplated, define the depersonalization boundary and justify it"). Retention schedule remains open (M-3).

---

## Findings

### BLOCKING

None. The three items the charter names as must-address (money/LLM, CRM contract, 152-ФЗ) are all architecturally addressed, and no open item is falsely claimed resolved.

### HIGH

**H-1 — Bi-directional goals sync (B2 sub-item) is silently dropped.**
The gap report's B2 explicitly calls out §11.1's "двусторонняя синхронизация с Zabot" and asks for a sync-master decision per field, "especially for the goals module." The spine's entire CRM integration story is one-directional: watermark polling upserting a read-only `crm_mirror`, with a canonical entity set (`Master`, `Client`, `Appointment`, `Visit`, `CheckLine`) that contains no goal/bar entity and no write path in `CrmPort`. Either (a) BRD v2.1 / an owner decision eliminated write-back — then the spine should say so, citing it, so implementers don't re-infer §11.1; or (b) write-back is still required — then it needs an AD or open question covering the write path, sync-master, and conflict resolution, because retrofitting a CRM write direction into an anti-corruption read mirror is a real rework. As written it is a silent scope decision embedded in a diagram.

**H-2 — B5 (motivation-scheme taxonomy) is BLOCKING in the gap report and has no home in the spine.**
AD-1's deterministic income engine is unbuilt without the scheme taxonomy and per-scheme parameter contract; AD-6 accommodates "motivation-scheme coefficients" as config rows but neither enumerates a v1 taxonomy (3–5 canonical schemes), nor decides fixed-set vs rule-engine (a scope-changing decision the report flags), nor lists it in Open Questions or Deferred. It is not purely content: the shape of the config schema, the engines module, and the editing boundary all depend on it. Add an open question (owner/content decision with a deadline before engines design) or a config-seed deliverable.

### MEDIUM

**M-1 — Cold-start fallbacks (I10) have no architectural home.**
AD-9 is a *staleness* ladder, not an *absence* ladder. New master / new salon / no-CRM-history is the first experience of every onboarding and the projection/bar engines (AD-1) have nothing to compute on; the capability map's onboarding row covers only `/start`, consent, primary profiling. Add fallback states to the engines/profile design (conservative default bar, category priors, degraded-mode messaging) or an explicit deferred item.

**M-2 — Consent revocation has no operational semantics (I5 + Q3 edge).**
Q3 carries *which* consents exist, but the spine never says what revocation *does*: message-stop vs data deletion vs degrade-to-minimum, and how it reaches the dispatcher (AD-10 knows floors and "write less often," not "withdraw consent"). The audit schema logs "export/delete requests," which implies subject-rights flows exist but nothing routes them. Define the revocation → dispatcher/profile effect before M1.

**M-3 — Retention periods / archive schedule absent (B4 sub-item).**
§13's "archived" stale observations still have no retention or deletion rule; AD-5 governs *where* PDn lives, not *how long*. This is a PD-operator registry prerequisite and a Q3 launch-gate input. One row in Conventions or Deferred would close it.

**M-4 — Barrier→intervention matrix and scale set (I1) lack a designated owner.**
Traffic light and rhythms received genuine architectural treatment (scoring entity, hysteresis in config, third rhythm = period); §9.5's barrier→intervention matrix and §6.3's canonical scale set appear nowhere — not in the capability map, config seed, or open questions. They are control-flow consumed by engines; assign them to config-seed content with the same versioned treatment as traffic-light thresholds.

**M-5 — N4: no consent gate on proactive force/sprint triggers.**
AD-10's arbitration resolves competing triggers by expected-income priority but never routes "force/sprint"-class triggers through the §9.4 GROW readiness confirmation. One clause in AD-10 ("trigger classes requiring master consent bypass arbitration into a consent-request message") closes it; without it, the dispatcher as specified can auto-initiate a sprint the BRD says requires consent.

**M-6 — N5: "aggregate only, no quotes" is a label, not an enforceable rule.**
The capability map asserts the §14 boundary but no mechanism defines aggregate (thresholds, min-cohort, no verbatim) or enforces it at the report-generation boundary. At minimum, mark it as a constraint on the owner-reporting message builder in `messaging`.

### LOW

- **L-1 (I2):** Motivational-type list and type→default-settings mapping absent; content-level, recoverable from Прил. А; belongs in config seed.
- **L-2 (I3):** Proactivity trigger catalogue not authored; the mechanism (dispatcher + config offsets) fully accommodates it. Ensure the catalogue lands as versioned config rows, not code.
- **L-3 (I4):** "Zero surveys" vs check-ins is BRD wording; not architectural; flag back to the BRD owner.
- **L-4 (I6):** Goal-vs-bar terminology not adjudicated; engines/config split implies the right structure (owner-set goal in config, AI-adjustable bar in engines); BRD-level fix.
- **L-5 (I7):** Smoothing/weights reproducibility is solved by AD-6 (`config_version` on score rows — a genuine improvement over the report's ask); operational definition of "progress" and per-signal normalization remain engine-design deliverables.
- **L-6 (I8):** Type↔scale mapping/recomputation rule unowned; assign to `profile` module design.
- **L-7 (N3):** Telegram pacing/quiet-hours handled; the no-delivery-receipts caveat (affects ignore-rate heuristics in AD-10, which assumes delivery visibility) deserves a one-line note.

---

## What the spine does notably well (for the record)

1. **AD-1** implements B3's recommendation verbatim and structurally (bound variables + payload-shape enforcement + CI golden tests) — stronger than prompt discipline.
2. **AD-9** exceeds B2's freshness-SLA ask with a two-level degradation ladder and a never-send-backdated rule that also protects the honesty contract.
3. **AD-8 + injectable Clock** fully resolves I9 including the no-DST simplification.
4. **AD-6's `config_version` on every message and score row** converts I7's explainability concern into an auditable mechanism.
5. **Open questions Q1–Q4 are exactly the right four**, and the `[ASSUMPTION]`/`[ADOPTED]` markers keep claimed-vs-decided status legible.

## Required actions before the spine is approved

1. (H-1) Resolve or explicitly carry bi-directional goals write-back.
2. (H-2) Give B5's scheme taxonomy a home: open question or config-seed deliverable with the fixed-set-vs-rule-engine decision.
3. (M-1, M-2, M-3) Add cold-start fallback states, consent-revocation operational semantics, and a retention schedule — each is a sentence-to-a-paragraph addition, not a redesign.
4. (M-4, M-5, M-6) Assign the barrier matrix/scale set to config seed; add the GROW consent gate clause to AD-10; state the aggregate-report enforcement point.
