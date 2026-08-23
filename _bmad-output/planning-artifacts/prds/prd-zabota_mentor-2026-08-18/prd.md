---
title: "Zabot AI Mentor PRD"
status: final
created: 2026-08-18
updated: 2026-08-23
---

# PRD — Zabot AI Mentor (Stage 1)

**Product:** ИИ-помощник мастера Zabot — proactive personal AI coach for beauty-salon masters
**Stakes:** Real launch (paying salons). This PRD drives full delivery.
**Primary sources:** Business Requirements v2.1 (`docs/zabot_ai.md`, owner decisions 13.08.2026), Stage-1 Reference Architecture research (16.08.2026), 152-ФЗ/LLM stack research (11.08.2026), Architecture run (18.08.2026, status: final), Gap & Contradiction report (10.08.2026), Owner clarification letter (rev. 4), **Team Q&A with owner answers v2.1 (`docs/Вопросы_команды_и_ответы_по_БТ_v2_1.md`, 23.08.2026 — change signal for this update)**.
**Stage-1 window:** M0–M3, ~18 weeks (per architecture plan; see Addendum A.7).

---

## 1. Purpose & Problem

Beauty-salon masters directly determine salon revenue through average check and service complexity, yet their ability to sell is limited by three personal barriers: **knowledge** (doesn't know what to offer), **skill** (can't phrase the offer), and **psychology** (is afraid to seem pushy). Owners set motivation plans in Zabot but have no scalable way to coach each master daily.

**Zabot AI Mentor** is a proactive personal coach delivered in Telegram that helps every master maximize their personal financial result — revenue, average check, personal income — through relevant, personalized per-client recommendations grounded in CRM history, and through coaching adapted to the master's psychological profile and current emotional state. Salon profit grows as a consequence of masters' results.

**Core differentiator:** the AI adapts the *format, tone, frequency, and content* of every interaction to the specific master's psychological profile and current state. The same meaning is delivered differently to two different masters. Where needed, the coach pushes goals; where needed, it slows down, supports, and helps the master reach the financial outcome.

The system respects owner-set goal frames, adapts the *bar and the path* — never the goal — and is designed so that sales follow from confidence and care, not fear (see Ethics, §9).

## 2. Goals & Success Metrics

### 2.1 Product goals

1. Masters earn more: growth in average revenue per client, average check, check complexity.
2. Masters grow within their salon's motivation plan (attain and exceed the Zabot avg-check / total-revenue plan).
3. Masters improve sales & service skills and overcome personal barriers.
4. Salon profit grows as a consequence; master turnover decreases (long-term indicator).

### 2.2 Success metrics

**Owner-facing:**
- GM-1: Growth in target metrics (avg revenue per client, avg check, complexity) vs. pre-launch baseline per salon.
- GM-2: Growth in master income.
- GM-3: Share of masters attaining their Zabot plan (avg-check / total-revenue).
- GM-4: Master turnover reduction (long-term).

**Master-facing:**
- GM-5: Personal income growth.
- GM-6: Result stability (fewer swings between pay periods).
- GM-7: Bar attainment / engagement.

**System-quality:**
- GM-8: Engagement — share of messages answered / conversational engagement rate, and inverse ignore-rate (see NFR-D, §10.4 — Telegram provides no read receipts; "share read" is **not** measurable in Stage 1).
- GM-9: Recommendation-to-check conversion (measured automatically from CRM).
- GM-10: Dynamics of emotional status (share of "green" weeks).
- GM-11: Message reproducibility — every message reconstructible from (facts, config_version, prompt_version); target 100% coverage.

**Counter-metrics (guard against success-by-harm):**
- CM-1: Share of masters who asked to reduce frequency or disable functions — must stay low (intrusiveness indicator).
- CM-2: Full opt-out / consent-withdrawal rate — must stay low (consent CM tied to §9.4).
- CM-3: Reaction-to-message negativity / tone deterioration after AI interactions — flat or improving.
- CM-4: Figure-accuracy incidents (any AI-authored or wrong number in a message) — target zero (see FR-9, Determinism).

**Pilot gate:** Stage 1 ends with a 1–2 salon pilot (M3). Numeric targets for GM/CM metrics are a **config-defined pilot-calibration deliverable** — set with the owner at pilot start, reviewed at pilot end. The PRD deliberately does not invent numbers; the same calibration approach already governs smoothing α and traffic-light thresholds (§8, FR-14).

### 2.3 Non-goals (Stage 1)

- No web portal, marketing site, native iOS/Android app, or Telegram Mini App (Mini App is the named growth path, RU-hosted when built).
- No bidirectional sync with Zabot — direction is strictly CRM/Zabot → agent, read-only (owner-confirmed 23.08; corrects BRD §11.1 "двусторонняя синхронизация"). Zabot is never written to. The 5-type motivation-scheme constructor (BRD §11.2) is deferred to backlog — Stage 1 works only with the 2 plan types that exist in Zabot (средний чек, общая выручка).
- No new roles beyond master and owner (no salon administrator, platform operator, or support roles). Architecture must allow adding a "salon administrator" role later without reworking access rights (owner-confirmed 23.08).
- No monetization/pricing model — out of scope for this PRD; Open Question OQ-7.
- No agentic LLM behavior, vector similarity search, pseudonymization tokens, or multi-provider routing (deferred; see Addendum A.7).

## 3. Actors & Roles (closed set, owner decisions 13.08 + 23.08.2026)

| Actor | Role |
|---|---|
| Master | Primary user; converses with AI, receives recommendations and coaching |
| Owner / manager | Sets goals, motivation plans, priorities, stop-list; receives reports and escalations |
| Zabot system | CRM + motivation-plan data source; message transport (Stage 1: Telegram) |
| AI Mentor service | Profiling, recommendations, coaching, monitoring, reporting — deterministic engines + bounded LLM roles (§10.1) |

### 3.1 Access matrix (owner-confirmed 23.08.2026)

| Data | Master | Owner |
|---|---|---|
| Own metrics, income, bar, plan-attainment position | read (via AI dialogue) | read, all masters |
| Motivation plans (avg-check plan, total-revenue plan — configured in Zabot) | read (own income portion) | read + write (in Zabot UI) |
| Agent additional settings (adaptive bar, priority positions, communication limits) | read (own portion) | read + write |
| Motivational type + profile scales (values) | descriptive on request ("how the system sees me") | **no access** |
| Traffic light (status + history) | no (never shown as a label) | **no access**, except red-escalation fact + "share of green weeks" aggregate in period report |
| Master↔AI correspondence | own — yes | **no access, in any form** |
| Period report (§14): metrics, rec conversion, aggregated conclusions | — | read |

**Principle:** the owner manages frames (goals, motivation, priorities) and sees results + aggregates; the psychological layer (scales, tone, correspondence, statuses) is the service's technical interior, accessible only to algorithms. This is the condition of master trust in the AI — without it, honest screening answers are not possible.

### 3.2 Inter-salon isolation (owner-confirmed 23.08.2026)

- Strict tenant isolation at the salon level. Owner of salon A sees nothing about a master's work in salon B.
- A master working in two salons: **one** Telegram dialogue and **one** psychological profile (type + scales — a property of the person, not the salon), but **two independent work contexts** (goals, bar, metrics, recommendations, reports — separate). The AI always explicitly identifies which salon it is discussing.
- Because the psychological profile is disclosed to no owner, its shared nature creates no conflict of interest.
- Architecture baseline: row-level multi-tenancy (NFR-G).

## 4. User Journeys

Journeys below are structured from the BRD's canonical examples (Приложение А) — `[ASSUMPTION]` tags mark what the PRD inferred beyond written sources. Reviewers should validate flow order and moment-of-truth framing.

### UJ-1: A shift in the life of Марина, "Achiever" (Достигатор)

Марина, hair stylist, 3 years in the salon, motivated by records and growth. Shift 10:00–19:00, 8 clients booked.

1. **09:40 — shift start message:** plan of the day (8 clients, 3 with recommendation potential), one day focus (not five), motivational framing in her energized business tone: *"Вчера ты сделала чек 3 900 ₽ — личный рекорд месяца. Замахнёмся сегодня на 4 200 ₽?"* Her communication contract: 3–4 touches per shift, full stats, 70/30 challenge/support.
2. **13:30 — pre-visit (T-30…60 min):** for the 14:00 client Анна К. — recommendation in *what / why / how* format: restoration procedure after coloring, justified by Анна's dryness complaints and never-sold care in history; a full script — even though Марина's sales-confidence scale would normally allow thesis-only — because this cross-sell is new to her.
3. **15:10 — micro-support (green status, gap in schedule):** praise when Анна accepts the care service: *"твоя подача сработала."*
4. **19:05 — shift totals:** revenue, avg check, which recommendations landed; progress toward period bar and income forecast *"если держать этот темп — к выплате выйдет ≈ X ₽"* — **computed deterministically** (FR-9), the AI only narrates; one specific praise for one specific action.
5. **Failure path:** on a below-pace day — analysis + new plan, never same-day hot debrief for sensitive types; for Марина (achiever) the debrief happens the same evening with a constructive redirect.

### UJ-2: Екатерина, "Cautious" (Осторожный/тревожный), overcoming the psychology barrier

Екатерина, nail master, fears seeming pushy; communication contract: 1–2 touches, gentle tone, 15/85 challenge/support, only positive dynamics shown.

1. **16:00 pre-visit:** one tiny idea: Наталья's cuticle oil is running out; one ready-made phrase to say when finishing: *"Кстати, масло, которое вам понравилось, снова есть — взять вам?"* — *"Это всё, больше ничего предлагать не нужно."*
2. **Next day:** oil appears in the check (system knows from CRM only — it **never asks** the master whether she offered, FR-5.4): *"Ты предложила — она согласилась, и никакой неловкости. Так это и работает."*
3. **Failure path:** no oil in check — normalization + optional rehearsal offer (*"можем один раз потренировать фразу прямо здесь, со мной… Без оценок"*).
4. **Over weeks:** systematic non-conversion of a recommendation type triggers a soft MI-style coaching conversation initiated by the AI, diagnosing the barrier (knowledge / skill / psychology) and matching the intervention (FR-7.4) — coaching care, not compliance control.

### UJ-3: Елена, salon owner — pay-period close

Елена owns the salon; avg-check and total-revenue plans configured in Zabot (FR-7).

1. **Pay-period end:** AI delivers a Telegram report per master: metrics vs. plan and vs. previous period; each master's plan-attainment position and income dynamics; recommendation conversion (from CRM); specific praise facts; what to improve and how she can help (training, assortment, booking); aggregated state signals (*"стоит поддержать, высокая нагрузка"*) — **no correspondence quotes, ever** (§9.3).
2. **Red-status escalation (out-of-band):** only for a red traffic light or systemic anomalies (e.g., one priority position under-performing across all masters → assortment/price problem, not a master problem).
3. **Plan change:** applies from the next pay period; the AI explains to each master what changed in *their* plan/progress.

### UJ-4: Onboarding — any master, first contact

Master receives a deep link, starts the bot in Telegram (`/start`), grants **4 separate consents** (FR-1.1: PDn+profiling, mood data, correspondence retention, cross-border transfer) before any profiling question, completes primary profiling in 3–5 minutes (5–7 conversational questions — see Addendum A.4 — plus CRM-history analysis for a realistic starting bar), and hears the working agreements (*"я буду писать примерно так и вот столько; это можно поменять в любой момент"*). First 2 weeks run in **calibration mode**: the AI asks for format feedback more often.

## 5. Feature Groups & Functional Requirements

### F1 — Onboarding & Consent

- **FR-1.1** Onboarding via Telegram deep link + `/start`; consent capture is a first-class step before any profiling question. **Four separate consents** collected at onboarding (owner-confirmed 23.08): (1) PDn processing + profiling for communication personalization; (2) emotional-state data processing (screenings, tone analysis); (3) correspondence history retention; (4) cross-border transfer of depersonalized data to the LLM provider. Without consent (1) the service is not activated. A bot cannot message a user who has not started the chat — no cold messaging is possible by design.
- **FR-1.2** Primary profiling runs as a live 3–5 minute dialogue (one question at a time, reactions to answers); it determines starting motivational type, starting scale values, preferred tone/frequency, personal quiet hours. Mandatory measurements and question list — Addendum A.4.
- **FR-1.3** CRM history analysis at onboarding (current avg check, complexity, dynamics) so the starting bar is realistic before the first dialogue. Cold start (no CRM history): conservative config-defined priors; onboarding is never blocked (see FR-11.4).
- **FR-1.4** The AI states the working agreements at the end of onboarding and obtains the master's confirmation (SDT autonomy). First 2 weeks = calibration mode with elevated format-feedback requests.
- **FR-1.5** Consent withdrawal (owner-confirmed 23.08): consents (2) and (3) are independently revocable via a bot command, with fact + date recorded. Withdrawing (2) disables screenings and tone analysis (traffic light operates on CRM signals only). Withdrawing (3) switches memory to **aggregated-profile-only mode** — raw correspondence and quotes are deleted; the aggregated profile (motivational type, profile scales + current values, traffic-light status + transition history) is retained. Withdrawing (1) deactivates the service entirely. Every profiling decision must link to an active consent record. **PDn operator** = the service's legal entity **[уточнить: наименование юрлица-оператора ПДн]**; the salon is an independent PDn operator of its clients — the agent processes client data on commission (ч. 3 ст. 6 152-ФЗ) per a commission-processing clause in the salon contract. Roskomnadzor notification filed before pilot launch.

### F2 — Master Profiling (hybrid: type + live scales)

- **FR-2.1** Profile = **motivational type** (one of 5 archetypes — Addendum A.2; assigned at onboarding; explainable preset) + **live scales** (9 continuous 0–100 characteristics — Addendum A.3; continuously refined). Scales, not the type, drive real behavior over time.
- **FR-2.2** Dynamic profiling from four signal streams: master replies (content, tone, length, speed, emoji, direct requests), behavior (answered/ignored by message class), CRM results (recommended positions landing in checks; metric dynamics after communication changes), state screenings (F6).
- **FR-2.3** Scales move smoothly (exponential smoothing); α is a per-scale config parameter (fast scales 0.3–0.5, slow scales 0.1–0.2 starting values), changeable without release; values and versions are logged. Calibration method: start by signal type, then tune on pilot history for "stability under noise + speed of reaction to sustained change."
- **FR-2.4** Type change: the system continuously scores how well the master fits each of the 5 types (from message reactions, format choices, micro-variation results). A type change occurs when an alternative type scores higher than the current one by a sustained delta (starting value: **+15 points out of 100**) for **≥ 2 consecutive pay periods**. The change is logged with justification; the master is never told "your label changed" — the style simply shifts smoothly. Every significant profile change is logged with justification (explainability for debugging and owner reporting).
- **FR-2.5** An explicit master request ("пиши короче", "без эмодзи", "не пиши до 10:00") applies **immediately**, bypassing exponential smoothing, and is logged as a "manual setting" (owner-confirmed 23.08).
- **FR-2.6** The type is never disclosed to the master as a label; the master may ask how the system sees them and gets a soft descriptive answer.
- **FR-2.7** **Progress definition** (owner-confirmed 23.08; gates bar raises in FR-5.5, FR-7.6): sliding 2-week window; progress = key bar metric growth **≥ +5%** vs. the previous window **or** bar retention **≥ 95%** throughout the window — at load **≥ 80%** of the master's typical (to avoid confusing demand drop with master drop). Both thresholds are config-defined.
- **FR-2.8** **Cold start** (owner-confirmed 23.08): no CRM history (new employee) → first pay period runs in **observation + support mode**: no bar, no income forecast; onboarding, introductions, and pre-visit recommendations work from day one (built on client history, not master history). The bar is first set in period 2 from period-1 actuals — an "introductory" bar, deliberately attainable. If primary profiling is incomplete: a default max-caution profile activates (low frequency, soft tone, no challenges — "Cautious" type settings); missing answers are gathered one question at a time during natural dialogue pauses over 1–2 weeks.

### F3 — Communication Engine (the "communication contract")

- **FR-3.1** Per master, the system maintains an actual communication contract: touch frequency, message length, tone, challenge/support ratio, number format (detailed tables ↔ one figure), send times. Starting values by type — Addendum A.2.
- **FR-3.2** Hard caps: ≤ 5 initiative messages per shift, ≤ 2 on days off; lower on yellow/red status. Quiet hours default 21:00–9:00 **master TZ** (NFR-F), guaranteed on the send side (NFR-D); configurable by owner and master.
- **FR-3.3** Pre-visit recommendations sent T-30…60 min before the appointment, evaluated in **salon TZ** (NFR-F).
- **FR-3.4** Message-class disable ladder: when reducing, period-total and pre-visit recommendation classes are disabled **last** — pre-visit only on explicit master request (FR-13.1).
- **FR-3.5** Ignore detection: ≥ 70% messages ignored per master over 2 weeks → reduce frequency to minimum and ask once, directly, what format would be useful. The AI never escalates pressure on a disengaged master.
- **FR-3.6** Trigger arbitration: when proactive triggers compete, the highest expected-income-value message is sent; others are deferred or merged — always inside the caps of FR-3.2.

### F4 — Recommendation Engine (next best offer)

- **FR-4.1** Signal sources: full client visit history (services, goods, amounts, intervals, comments), product purchase cycles, service cyclicity and "gaps," seasonality, visit comments (complaints, plans, allergies), owner priorities, past refusals.
- **FR-4.2** Candidates = owner priority positions ∪ history-logical positions (repeat purchase, cross-sell, up-sell to the booked service). Exclusion filters: ≥ 2 consecutive client refusals → N-month pause; contraindications/allergies from comments; owner stop-list; incompatibility with the booked service.
- **FR-4.3** Ranking by expected value: acceptance probability (client history + master statistics) × margin/priority.
- **FR-4.4** Per visit the master receives 1–3 recommendations — fewer is better; the goal is one confident offer, not a menu. Format is always *what / why / how*: the item, the history-based justification, and a ready phrase adapted to the master's psychotype and the client's context. Depth depends on the sales-confidence scale: full script for novices, thesis for veterans.
- **FR-4.5** Zero-survey feedback loop (owner-confirmed rewording 23.08): the BRD §8.4 ban applies **only to reporting/control surveys** ("did you offer? did it sell?"). Care-oriented mood check-ins are permitted and governed by F6 / §10 (frequency 2–3×/week, right not to answer without consequence). The system never asks the master whether they offered. Outcomes are reconciled automatically from check contents only. Non-conversion does not distinguish "didn't offer" from "client refused" — and the system does not interrogate the master to find out.
- **FR-4.6** Automatic outcomes update: client profile (accepts / consistently declines), master profile (conversion by recommendation type), and engine quality (which recommendations work for this master).

### F5 — Coaching Cycles

Three rhythms: **shift** (day plan, day focus, pre-visit recommendations, micro-support, shift totals), **week** (mini-retrospective: what worked, one skill in focus, pace correction), **pay period** (full GROW session: totals, income, plan-attainment progress, new bar, plan agreement).

- **FR-5.1** Shift-start message: short day plan (clients, who has recommendations), one day focus, mood screening 2–3×/week (not daily — anti-fatigue), motivational message in psychotype tone.
- **FR-5.2** Between visits — micro-support only if a schedule gap exists and status is green.
- **FR-5.3** Shift totals: revenue, avg check, recommendation outcomes, progress toward period bar and deterministic income forecast, one specific praise for one specific action. Reaction to a bad day follows the type matrix (Addendum A.2); no hot debrief for sensitive types.
- **FR-5.4** GROW session at period end: Goal (bar + nearest money lever of the salon's motivation plan), Reality (honest totals, self-comparison only), Options (2–3 focus options, master chooses — autonomy), Will (agreements fixed: bar, focus, what the AI will do).
- **FR-5.5** Forcing (raise bar/intensity) requires **all three**: sustained progress per FR-2.7 (≥ +5% or ≥95% retention over 2-week window at ≥80% load), green status, and the master's explicit consent in dialogue. Automated sprint triggers always pass through this GROW consent gate — never auto-initiated. Proximity trigger: plan attainment < 10–15% away → show how close the plan is and offer a sprint (promotion types: exciting; prevention types: "don't lose what's almost earned").
- **FR-5.6** Pace reset (hold/lower bar, switch to support) when: yellow/red status; ≥ 2 weeks without progress per FR-2.7 at normal load (diagnose the barrier — don't push); life circumstances reported by the master; after a forced sprint — a planned recovery window without ambitious goals.
- **FR-5.7** Barrier work: when recommendations of a type systematically miss checks (CRM-visible, no surveys), the AI soft-raises the topic, diagnoses the barrier (knowledge / skill / psychology) via MI-style open questions, and applies the matching intervention matrix (Addendum A.5). This is a coaching conversation initiated with care, not compliance control.

### F6 — Emotional Monitoring & Traffic Light

- **FR-6.1** Signal sources: direct screenings (short scale questions 2–3×/week; WHO-5-derived check-in every 2 weeks, conversational, non-clinical), correspondence tone analysis (length, speed, style change, emoji disappearance in an emoji-active master, ignoring), indirect CRM signals (output drop at same booking level, cancellations up, shifts shortened).
- **FR-6.2** Traffic light = composite state score (0–100) from three streams (screenings normalized 0–100; LLM tone assessment 0–1 with confidence threshold; CRM signals), weights are config parameters. **Status transitions are decided in code, never by the LLM.** Tone assessment below confidence threshold (start ≥ 0.7; burnout markers ≥ 0.8) cannot change status.
- **FR-6.3** Hysteresis: entry/exit thresholds differ, with minimum stay (starting values — pilot-calibrated): yellow entry < 60 three days running (or tone < 0.4 at ≥ 0.7 confidence), exit ≥ 70 held 3 days; red entry < 40 for 7 days (or burnout markers at ≥ 0.8 confidence + output drop > 20% at same booking over 2 weeks), exit ≥ 55 held 7 days; min stay 3 / 7 days. **Calibration guidance (owner-confirmed 23.08):** false reds ≤ 1 per 10 masters/month (each extra escalation spends owner trust); missed real burnouts = 0 (on doubt, lean yellow not green); yellow↔green transitions ≤ 1/week per master (else hysteresis is too weak).
- **FR-6.4** Status behavior: green — standard, forcing allowed; yellow — frequency ↓, challenge ↓, support ↑, forcing forbidden, soft open question; red — support only, no goals, no sales talk, offer to discuss workload, delicate owner escalation.
- **FR-6.5** Ethics of monitoring: screening framed as care, not control; non-response is a signal but never a reason for pressure; no diagnoses, no clinical terms; at serious distress the AI gently recommends a professional; red-status escalation to owner carries conclusion + recommendation only — **no correspondence quotes**.

### F7 — Goals, Adaptive Bar & Motivation Plans

- **FR-7.1** Terminology (owner-confirmed 23.08, tied to Zabot's actual data): **Goal (цель)** = a plan set by the owner in Zabot — one of two types only: **plan by master's average check** or **plan by total revenue** — unified per salon, read-only to the agent, the AI never changes it and cannot. **Adaptive bar (планка)** = an internal intermediate agent value (lives in the agent's calculation DB): the individual trajectory of the master toward the Zabot plan. The AI adapts the bar and the path, never the goal.
- **FR-7.2** The goals/motivation module is **read from Zabot** (the 2 plan types), not built inside the Mentor service. Two-way sync does not exist — direction is strictly Zabot → agent, read-only (corrects BRD §11.1). The 5-type scheme constructor from BRD §11.2 is **deferred to backlog** — it becomes relevant only when the service ships its own bonus module. BRD §11 will be corrected accordingly (v2.2); §11.3 and §11.5 require correction too **[уточнить: content of §11.3/§11.5 corrections pending scheme-constructor removal]**.
- **FR-7.3** Owner configures in Zabot: the two plan types (avg-check target, total-revenue target per pay period). In the agent's own settings (stored in the agent calculation DB) the owner configures: priority services & goods, stop-list, default quiet hours, communication limits, and — optionally — remuneration rules (rates, percentages) if ruble income calculations are wanted (see FR-9.4). Pay period (week / two weeks / month) is read from Zabot.
- **FR-7.4** **Stage 1 supports only the 2 Zabot plan types.** No scheme constructor, no tier/rate/bonus configuration, no percent-base question, no rule engine. The agent reads plans + actuals from Zabot/CRM and computes everything derived (progress to plan, pace, attainment forecast, adaptive bar within the plan, decomposition "how much per visit/shift") in its own calculation DB. Goal framing uses the plan metric. The 5-type taxonomy (Addendum A.6) is retained as backlog reference only.
- **FR-7.5** On incomplete plan data, the AI invents no income figures — metrics only + clarification request to the owner (config-completeness degradation).
- **FR-7.6** Adaptive bar (Locke–Latham): specific, measurable, difficult-but-attainable (~60–70% attainment probability at normal effort **[уточнить: method for computing ~60–70% probability — e.g., linear projection of current trend + historical dispersion band]**), accepted by the master in GROW. **Corridor rules (owner-confirmed 23.08, starting values, config-defined):** calculated bar = forecast from the master's actual dynamics in "difficult-but-attainable" logic; allowable deviation of the adaptive bar from the calculated bar = **±15%**; raise step = **≤ +10% per period**; tactical lowering on yellow/red status = **not below −15%** of the calculated bar and not below the master's actual average over the last 2 periods. The bar **cannot exceed the Zabot plan**; if the Zabot plan is below the master's actual level, the agent holds the master at their actual level and reports to the owner in the period report that the plan needs revision. Movement rules: raise only on sustained progress (FR-2.7) + consent; stagnation — hold + diagnose; decline — never raised. The bar is never framed as punishment; always in income/metric terms.
- **FR-7.7** Income transparency: at any moment the master can ask "how much have I earned?", "how far to the plan?", "what would +2 goods/day give me?" — answered by deterministic calculation. The visible action→money link is the system's primary motivational mechanism. Ruble income figures appear only if the owner has entered remuneration rules in agent settings (FR-9.4); otherwise the agent works in metric and plan-progress terms ("240 ₽/visit left to the avg-check plan" — plan-relative, not salary).
- **FR-7.8** Plan changes (made by the owner in Zabot) apply from the next pay period; the AI explains to the master what changed in their plan/progress.

### F8 — Proactive Triggers

- **FR-8.1** Trigger catalogue (condition → reaction): period-bar risk → plan re-assembly, focus on high-potential visits; strong growth opportunity → day-potential message ("завтра день с потенциалом +4 500 ₽"); proximity to plan attainment → sprint offer via the GROW consent gate (FR-5.5); negative pattern (e.g., recommendation conversion down 3 weeks) → soft barrier diagnostics; positive pattern → reinforcement ("это уже навык"); master silence beyond profile norm → one gentle bridge message, no reproach.
- **FR-8.2** All initiative messages pass through caps, priorities, and arbitration (FR-3.5–3.6). Proactivity ≠ frequency.

### F9 — Deterministic Money Math & LLM Roles (the determinism boundary)

- **FR-9.1** **All** figures — income, forecasts, bar values, plan progress, scores, rankings, cap counts — are computed deterministically by the agent's calculation engine over its **calculation DB** (a separate DB replicating the needed CRM/Zabot entities + all derived values: metric dynamics, plan progress, adaptive bar, recommendation conversion, traffic-light score). CRM/Zabot is master for operational data + motivation plans; the agent is master for all derived data — conflict is excluded by construction (the data sets do not overlap, each metric has exactly one owner). The LLM receives computed values as bound inputs and is forbidden from generating, estimating, or rounding any figure.
- **FR-9.2** The LLM has exactly three roles: (a) narrator of pre-computed facts in psychotype-calibrated prose; (b) structured-output classifier (tone 0–1 + confidence; below threshold it cannot change state); (c) bounded MI/GROW coaching-dialogue partner under versioned prompts.
- **FR-9.3** On LLM outage or budget trip, narration degrades to deterministic templates — **wording degrades, correctness never does**. Zero figure-accuracy incidents is a hard requirement (CM-4).
- **FR-9.4** **Output validator** (owner-confirmed 23.08): every money-type number in an outgoing message must match the corresponding computed number (rounding is done only by the engine, before passing to the LLM). A message that fails validation is **not sent**. This is the hard enforcement layer on top of FR-9.1.
- **FR-9.5** **Ruble calculation gate** (owner-confirmed 23.08): if remuneration parameters (rates, percentages) are not available via the Zabot API, the agent **does not compute salary in rubles** — it works in metrics and plan-progress terms. Ruble income forecasts are enabled **only if the owner has entered remuneration rules in the agent settings** (stored in the agent calculation DB); then the agent computes by those rules and explicitly labels the result as a service estimate, not Zabot data.

### F10 — Owner Reporting & Escalation

- **FR-10.1** Per pay period, per master, the owner receives (Stage 1: Telegram): metrics vs. plan and previous period; plan-attainment position and income dynamics; recommendation conversion (CRM-measured); specific praise facts; improvement areas + how the owner can help (training, assortment, booking); aggregated state signals only; profile status (how the master responds to communication, what was changed).
- **FR-10.2** Out-of-band escalation only on red status or systemic anomalies (e.g., one priority position sagging across all masters — assortment/price problem, not masters).
- **FR-10.3** Confidentiality: master↔AI correspondence is never transmitted to the owner in any form except aggregated conclusions (§9.3). The aggregate-vs-detail boundary must be enforceable — no verbatim, no quote-length fragments, threshold-defined aggregation. `[ASSUMPTION]` The precise aggregation rule is a config-defined deliverable at pilot.

### F11 — CRM Integration & Data Freshness

- **FR-11.1** Data received via Zabot (per-salon CRM): visit history per client per master incl. comments; sales of services/goods by master by client; shift load and schedule; future bookings; check composition per visit; metric dynamics; cancellations and rescheduling.
- **FR-11.2** Freshness thresholds (owner-confirmed 23.08, config-defined, pilot-calibrated): checks/sales ≤ 60 min (post-visit praise, shift totals); schedule/bookings/cancellations ≤ 15 min (pre-visit recommendations); dynamics/period totals ≤ 24 h (income forecast, GROW).
- **FR-11.3** Degradation ladder (owner-confirmed 23.08): **Level 1 (stale but usable)** — data older than threshold but under hard limits (checks < 24 h; schedule until end of day) used with a visible timestamp label ("по данным на 14:30"); monetary forecasts suppressed. **Level 2 (hard-stale / CRM down)** — communication continues without figures: support, coaching, profile/history-based recommendations; money math, visit-specific praise, and forecasts suspended; the AI tells the master honestly. **Recovery:** re-sync, totals recomputed on actuals; missed event messages are never sent retroactively — folded into shift/period totals — **with one exception** (owner-confirmed 23.08): praise for a successful recommendation may be sent late, within 60 min but no later than the end of the same shift; this is the most valuable reinforcing message, better late than never. Honesty in figures outweighs narrative continuity.
- **FR-11.4** Cold start: new master / new salon / new client → config-defined conservative priors per entity; onboarding and basic operation never blocked on data sparsity. For a new master with no CRM history specifically: observation + support mode in period 1, first bar in period 2 (FR-2.8).
- **FR-11.5** **Sync mechanism** (owner-confirmed 23.08): primary channel = Zabot webhooks on events (booking created/changed, visit/check closed, cancellation) — **unverified, marked as such** pending API confirmation (team item 1); REST API polling for entities without webhooks; safety net = nightly full reconcile to heal missed events. **Direction is strictly one-way: CRM/Zabot → agent, read-only.** No writes to Zabot, no two-way sync (corrects BRD §11.1). The canonical CRM entity set is pending Zabot API field verification **[OQ-1 narrowed: verify Zabot API surface — plans, checks, bookings, webhooks]**. Architecture reserves a fixture-CRM mode that keeps M0 fully unblocked.

### F12 — Memory & Personalization

- **FR-12.1** Long-term memory: master profile (type, scales, agreements, barriers, what worked/didn't), client profiles in recommendation terms (refusals, preferences), bar history and results. Short-term focus: current period, week focus, open agreements.
- **FR-12.2** Freshness priority: fresh signals outweigh old; stale observations are archived out of the prompt set (archival periods config-defined, pilot-calibrated — `[ASSUMPTION]` retention periods interact with 152-ФЗ retention duties, OQ-3).
- **FR-12.3** Memory is used for help, never pressure: the AI does not remind masters of past failures; negative episodes are stored only as material for choosing support.

### F13 — Communication Floor, Pause & Opt-out (owner-confirmed 23.08)

Adopted as requirements (resolving the "communication never stops" vs. autonomy contradiction):

- **FR-13.1** Minimum floor (owner-confirmed 23.08): **1 period-summary message + reactive answers to the master's incoming questions** (reactive mode is always available). Pre-visit recommendations are disabled **last** — and only on the master's explicit request.
- **FR-13.2** Pause / vacation mode (owner-confirmed 23.08): **automatic** pause when no shifts are scheduled for ≥ N days (starting N = 5, config-defined); **manual** pause ("I'm on vacation until..."). During a pause: silence except reactive answers to incoming. Goals/bar logic accounts for the pause.
- **FR-13.3** Full opt-out (owner-confirmed 23.08): the master can disable the service entirely, degrading to legally required notices only (changes to PDn processing terms, etc.). The owner sees only the fact "master disabled the assistant" — no reasons, no details. Equals consent withdrawal in effect (FR-1.5). The system tracks CM-2.
- **FR-13.4** Principle 4 restated (owner-confirmed 23.08, corrects BRD §2): not "communication never stops" but **"communication never stops on the AI's initiative"** — only the master can stop it. While consent is active, the floor applies; autonomy and legal withdrawal rights always win.

### F14 — Configuration, Calibration & Audit

- **FR-14.1** All behavioral parameters are config-managed, changeable **without release**: smoothing α per scale, traffic-light thresholds and hysteresis, freshness thresholds, caps and floors, bar corridor parameters (±15% / +10% / −15%), trigger offsets. Config is insert-only versioned; config version participates in message reproducibility (GM-11); rollback < 5 min.
- **FR-14.2** Every significant decision — profile change, status switch, config change, consent event, egress event, erasure — lands in an append-only audit log with justification and inputs.
- **FR-14.3** Config-seed deliverables at pilot start: profile scale definitions, barrier→intervention matrix, starting thresholds, memory archival policy, aggregation rule for owner-visible conclusions (FR-10.3), bar corridor starting values, progress thresholds (FR-2.7), type-divergence delta (FR-2.4).

## 6. Constraints & Dependencies

- **C-1 Compliance (152-ФЗ, launch gates):** PDn storage and primary processing only on RU infrastructure (ч. 5 ст. 18); LLM = OpenAI via depersonalization gateway (owner decision 13.08, reconfirmed 23.08) — direct identifiers (names, contacts, client names) stripped before egress; **direct identifiers must not enter prompts even in the depersonalized circuit** — use internal IDs + placeholder names with reverse substitution on our side (owner-confirmed 23.08); art. 12 cross-border consent + Roskomnadzor notification required before launch; erasure must propagate everywhere incl. CRM-mirror tombstones; logs PII-scrubbed. **PDn operator** = the service's legal entity **[уточнить: наименование юрлица-оператора ПДн]**; the salon is an independent PDn operator of its clients — the agent processes client data on commission (ч. 3 ст. 6 152-ФЗ) per a commission-processing clause in the salon contract. LLM connected via a single LLM port — provider swap without domain rework (the RU-native-provider alternative considered and rejected for Stage 1 — Addendum A.8).
- **C-2 Channel:** Telegram-only at Stage 1. Channel constraints accepted as Stage-1 limitations (owner-confirmed 23.08): no delivery/read guarantees → engagement measured by answers/reactions, not sends (GM-8); inline keyboards available and **must** be used for screenings (1–5 button scale) and quick replies — reduces friction, raises answer share, no separate widget needed; **quiet hours are guaranteed on the send side** (the service simply does not send in that interval) — not best-effort. All format/frequency/tone requirements are channel-agnostic.
- **C-3 Integration dependency:** Zabot CRM API surface to be verified (team item 1) — webhook availability, REST field set, plan/check/booking entities. Sync mechanism decided (FR-11.5: webhooks + REST polling + nightly reconcile, read-only). Fixture CRM keeps M0 unblocked; M1 gated on API verification.
- **C-4 Scale & shape:** hundreds of masters ≈ a few messages/second; scalability is not a Stage-1 driver. Team 2–4 engineers; machine-to-machine keys, no OAuth. Infra envelope ~$100–150/month + LLM costs (low hundreds $/month at hundreds of masters); egress markup a live variable (OQ-6).
- **C-5 DR:** RPO ≤ 15 min, RTO ≤ 4 h, quarterly restore drill; staging via dedicated test bot.
- **C-6 Tech (pinned by architecture, final):** Python 3.12+ modular monolith, FastAPI + aiogram 3, PostgreSQL 17, Redis 8, docker compose on 2 Yandex Cloud VMs, GitHub private + self-hosted RU runner. Detail lives in the architecture docs — not normative here.

## 7. Milestones (product-level view)

| Milestone | Weeks | Product content |
|---|---|---|
| M0 | 1–4 | Onboarding + consent, config versioning, scheduler + quiet hours, template messages, audit — zero CRM dependency (fixture CRM) |
| M1 | 5–8 | Real CRM sync, freshness SLO, degradation Level 1 *(gated on Zabot API verification — OQ-1)* |
| M2 | 9–14 | Traffic light, income/forecast engine, recommendation engine, triggers/arbitration/floors, prompt library + LLM port, golden tests |
| M3 | 15–18 | Owner reporting, degradation drills, Roskomnadzor notification file, **pilot with 1–2 salons** |

## 8. Open Questions

### 8.1 Open

| ID | Question | Blocks | Owner |
|---|---|---|---|
| OQ-1 | **Narrowed (23.08):** sync mechanism decided (FR-11.5: webhooks + REST polling + nightly reconcile, read-only). Remaining: verify Zabot API field surface (plans, checks, bookings, webhooks) — team item 1 | M1, FR-11 | Zabot owner |
| OQ-3 | **Partially resolved (23.08):** 4 separate consents + revocation model + aggregated-profile definition confirmed (FR-1.5). Remaining: PDn operator legal entity name **[уточнить]**; retention periods (interact with 152-ФЗ retention duties) | Launch gate (Roskomnadzor), FR-1, FR-12.2 | Owner + counsel |
| OQ-6 | Egress mechanism: own foreign VM vs ruble-billed intermediary (intermediaries are unauthorized resellers outside OpenAI ToS — volatility risk) + model selection | C-1 implementation, cost | Owner + tech |
| OQ-7 | Monetization / pricing / sales motion (out of PRD scope, must be decided before launch) | Go-to-market | Owner |
| OQ-9 | Confidentiality aggregation rule specifics (FR-10.3 `[ASSUMPTION]`) | FR-10.3 | PM + counsel |
| OQ-10 | **[уточнить]** Method for computing ~60–70% attainment probability for the calculated adaptive bar (FR-7.6) — e.g., linear projection of current trend + historical dispersion band | FR-7.6 | Owner + tech |
| OQ-11 | **[уточнить]** PDn operator legal entity name (FR-1.5, C-1) | Launch gate (Roskomnadzor) | Owner + counsel |
| OQ-12 | **[уточнить]** BRD §11.3 and §11.5 corrections pending scheme-constructor removal (FR-7.2) — content to be defined for BRD v2.2 | BRD v2.2 release | Owner + PM |

### 8.2 Resolved / obsolete (23.08.2026)

| ID | Status | Resolution | PRD ref |
|---|---|---|---|
| OQ-2 | Resolved | Full access matrix + inter-salon isolation — owner-confirmed | §3.1, §3.2 |
| OQ-4 | Resolved | F13 floor / pause / full opt-out confirmed as requirements | FR-13.1–13.4 |
| OQ-5 | Obsolete | 5-type constructor → backlog; Stage 1 = 2 Zabot plan types only | FR-7.4, A.6 |
| OQ-8 | Resolved | Progress = +5% key metric or ≥95% bar retention over 2-week window at ≥80% load | FR-2.7 |

## 9. Ethics & Trust (normative for all features)

- **E-1** The AI never changes goals or KPIs (owner only); never punishes or shames; never compares masters to each other (self-comparison only); never threatens escalation or uses it as a lever.
- **E-2** No manipulation: no guilt, no fear of firing, no toxic positivity. Every interaction should leave the master more resourced than before it.
- **E-3** No psychological diagnoses; WHO-5-derived check-ins are conversational, non-clinical; at serious distress — gentle recommendation to see a professional.
- **E-4** Recommendations to clients only from owner priorities + client-history logic; the master's "no" is respected — any insistent offer at most twice, then fixed in the profile and suppressed.
- **E-5** Honesty in figures always beats motivational framing: no embellished forecasts (FR-9).
- **E-6** Master↔AI correspondence is confidential; owner sees aggregates only; red-status escalation carries conclusion + recommendation, no quotes.
- **E-7** The system is based on established empirical models (SDT, regulatory focus, Locke–Latham, MI, GROW, Big Five markers, WHO-5, Maslach) — prompts and logic must explicitly reference them, not "intuitive psychology" (model table — Addendum A.1).

## 10. Non-Functional Requirements

### 10.1 Determinism & correctness
- **NFR-A:** 100% of figures deterministic (FR-9); zero figure-accuracy incidents (CM-4); every message reproducible from (facts, config_version, prompt_version) — 100% coverage (GM-11); status transitions decided in code, never by LLM.

### 10.2 Compliance & privacy
- **NFR-B:** RU-zone PDn residency; depersonalized-only egress through an audited gateway; art. 12 consent + Roskomnadzor notification as launch gates; append-only audit of consent, config, egress, erasure; PII-scrubbed logs; erasure propagation incl. CRM-mirror tombstones; consent-withdrawal → auto-degrade (FR-1.5). Legal sign-offs pending for: WHO-5/mood data as special category (Art. 10), Art. 22 register, Art. 16 threshold effects, crypto-shredding vs destruction (counsel — non-blocking for M0–M2).

### 10.3 Reliability & operations
- **NFR-C:** LLM outage → deterministic template fallback (FR-9.3); degradation ladder FR-11.3 with quarterly drills; DR RPO ≤ 15 min / RTO ≤ 4 h with quarterly restore drill; config rollback < 5 min.

### 10.4 Channel realism
- **NFR-D:** Telegram (owner-confirmed 23.08): no delivery/read receipts → engagement measured by answers and reactions, not by send facts (GM-8); **quiet hours guaranteed on the send side** (the service does not send in that interval); inline keyboards for screenings (1–5 buttons) and quick replies. "Read share" explicitly out of scope for Stage 1.

### 10.5 Scalability & cost
- **NFR-E:** Hundreds of masters, a few messages/second — no exotic scaling; LLM cost controls mandatory: response length caps, per-master daily token meter, budget-trip template fallback.

### 10.6 Time & geography
- **NFR-F:** Russia spans UTC+2..+12, no DST since 2011 — static zones. **Store both salon TZ and master TZ** (master TZ defaults to salon TZ, overridable) (owner-confirmed 23.08). Quiet hours and all personal sends to the master — evaluated in **master TZ**; pre-visit T-30…60 recommendations — evaluated in **salon TZ** (where the visit physically occurs).

### 10.7 Security & isolation
- **NFR-G:** Inter-salon data isolation (owner-confirmed 23.08: strict tenant isolation at salon level; master in two salons = one psych profile, two work contexts — §3.2); architecture baseline: row-level multi-tenancy; machine-to-machine keys; secrets in vault; PII-scrubbed logging.

### 10.8 Explainability
- **NFR-H:** Every behavioral decision (profile change, status switch, bar move, trigger fired) is logged with inputs and justification, retrievable for debugging and owner reporting; config and threshold versions recorded with every change.

## 11. Glossary (working terms)

| Term | Meaning |
|---|---|
| Goal (цель) | Owner-set plan in Zabot (avg-check or total-revenue); read-only to the agent; the AI never changes it |
| Adaptive bar (планка) | Internal agent value — individual per-period trajectory toward the Zabot plan; AI moves it within corridor rules (±15%, +10%/period, −15% floor) |
| Motivation plan (план мотивации) | Stage 1: one of 2 Zabot plan types (avg-check, total-revenue). The 5-type constructor is backlog |
| Tier (ступень процентов) | *Backlog only* — progressive-scale threshold; not in Stage 1 (no scheme constructor) |
| Recommendation (рекомендация) | what/why/how offer hint for a specific client visit |
| Check complexity (комплексность чека) | Services + goods per client per visit |
| Traffic light (светофор состояния) | Green/yellow/red composite emotional-state status |
| Communication contract | Current frequency/tone/format agreements per master |
| Day/week focus (фокус дня/недели) | The single priority concentrated on in the period |

Full terminology detail and the barrier matrix — Addendum A.5; scientific-basis table — A.1; type matrix — A.2; scale set — A.3; onboarding questions — A.4; motivation plans — A.6; timeline — A.7; rejected alternatives — A.8.
