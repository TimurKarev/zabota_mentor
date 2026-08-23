# PRD Addendum — Zabot AI Mentor (Stage 1)

Depth that belongs in downstream documents (architecture, solution design, UX spec) or earned a place but does not fit the PRD narrative. Source: BRD v2.1 + research digests + architecture run. Not normative for epics unless referenced from the PRD.

## A.1 Scientific basis (BRD §4 — normative for prompt design)

Requirement: prompts and AI logic must explicitly lean on these models, not "intuitive psychology."

| Model | Authors | What the system takes |
|---|---|---|
| Self-Determination Theory (SDT) | Deci, Ryan | Three basic needs — autonomy, competence, relatedness. Identify the master's leading motivation source and feed it. Internal motivation outlasts external: pressure destroys results |
| Regulatory Focus Theory | Higgins | Promotion vs prevention focus. Determines goal framing: "earn 15% more" vs "don't lose your level" |
| Goal-Setting Theory | Locke, Latham | Goals: specific, measurable, difficult-but-attainable, regular feedback, accepted by the person. Basis of the adaptive bar |
| Motivational Interviewing (MI) | Miller, Rollnick | Coaching dialogue style: open questions, reflection, autonomy support, ambivalence work ("want to earn more but don't want to push") |
| GROW | Whitmore | Coaching session structure: Goal → Reality → Options → Will |
| Big Five | Costa, McCrae | Light personality markers (extraversion, neuroticism, conscientiousness) for tone/frequency calibration — via indirect signs, no full testing |
| WHO-5 Well-Being Index | WHO | Basis of short conversational state screenings (adapted wording, not medical diagnostics) |
| Maslach burnout model | Maslach | Burnout risk markers: exhaustion, cynicism, falling perceived efficacy — for the traffic light and escalation |

## A.2 Motivational types — full matrix (BRD §6.2, §7.2, Прил. А)

| | Achiever (Достигатор) | Competitor (Соревнующийся) | Stable pro (Стабильный) | Caring server (Заботливый) | Cautious (Осторожный) |
|---|---|---|---|---|---|
| Science anchor | Promotion; competence (internal) | Status (external); promotion | Prevention; autonomy | Relatedness (SDT) | High neuroticism; prevention; low sales confidence |
| Motivated by | Growth, records, levels, ambitious bars | Beating yesterday's self, ratings, visible progress | Predictable income, reliability, respect for experience | Client gratitude, usefulness, relationships | Safety, support, small guaranteed steps |
| Demotivated by | Stagnation, no challenge, "too easy" | Invisible/unrecognized progress | Abrupt change, micromanagement, pressure | Anything resembling pushing; sale-vs-care conflict | Publicity, pressure, rejection fear, "pushy" fear |
| Touches per shift | 3–4 | 3–4 | 1–2 | 2–3 | 1–2 |
| Tone | Energetic, business | Playful, competitive | Respectful, calm | Warm, human | Soft, gentle |
| Goal framing | Challenge: "go for a record?" | Progress: "2 800 ₽ to next level" | Stability: "hold the week's pace" | Meaning: "3 clients genuinely need care today" | Micro-steps: "one offer to one client" |
| Challenge/support | 70/30 | 60/40 | 40/60 | 30/70 | 15/85 |
| Number format | Full stats, forecasts | Progress scales, "X left to goal" | One short daily summary | Client stories + 1–2 figures | Positive dynamics only, no "lagging" |
| Bad-day reaction | Analysis + new plan | Streak restart | Normalization: "it happens, pace is fine" | Support + meaning | Support only; debrief next day |

Full canonical message examples per type (shift start / pre-visit / failure / success) — BRD Прил. А; treat as tone references, not templates: the AI generates dynamically within the register.

## A.3 Profile scales (BRD §6.3)

Ambitiousness · Pressure sensitivity · Need for support · Sales confidence · Sale framing (care ↔ pushing) · Preferred frequency · Preferred tone (business ↔ friendly, emoji, length) · Execution discipline (reminders, checklists, micro-steps) · Failure reaction (recovery content dosage). All 0–100, smoothing per FR-2.3.

## A.4 Primary profiling questions (BRD Прил. Б)

Live Telegram dialogue, one at a time, adaptive order/wording; mandatory measurements in brackets: (1) what do you like most about your work [SDT source]; (2) ideal work month: record income / even schedule / happy regulars [promotion/prevention, ambitiousness]; (3) hints: detailed or short [format]; (4) attitude to offering extras — from "easy, part of service" to "awkward, afraid to be pushy" [sales confidence, care/pushing frame — key question]; (5) after a bad day: dissect or breathe first [failure reaction, pressure sensitivity]; (6) useful message frequency [starting frequency — direct consent]; (7) do-not-write times + preferred address [quiet hours, boundaries]. Ends with summarized agreements + confirmation.

## A.5 Barrier → intervention matrix (BRD §9.5 — config-seed deliverable)

| Barrier | Sign | Intervention |
|---|---|---|
| Knowledge | "Don't know what/whom to offer" | Richer justifications in recommendations; mini content on product composition/effects |
| Skill | "I offer — they decline" | Ready scripts, phrasing analysis, micro-rehearsal in dialogue with the AI, analysis of the master's own successful cases |
| Psychology | "Awkward, afraid to seem pushy" | Sale=care reframing on her own client cases, micro-steps (one offer/day), positive-outcome fixation, rejection normalization |

## A.6 Motivation plans — Stage 1 (owner-confirmed 23.08.2026; supersedes BRD §11.2 constructor)

**Stage 1 works only with the 2 plan types that exist in Zabot** — no constructor, no rule engine, no tier/rate/bonus configuration:

1. **Plan by master's average check** — target avg-check value per pay period.
2. **Plan by total revenue** — target revenue value per pay period.

The agent reads these plans + actuals from Zabot/CRM (read-only) and computes everything derived (progress, pace, forecast, adaptive bar, decomposition) in its own calculation DB. The 5-type constructor from BRD §11.2 (progressive percent scale; fixed + percent; category rates; period-goal bonuses; combinations) is **deferred to backlog** — it becomes relevant only when the service ships its own bonus module. Retained here as backlog reference:

*Backlog (not Stage 1):* (1) progressive percent scale — metric thresholds → stepwise master rate; (2) fixed + percent; (3) category rates — own % for services/goods/repeat visits; (4) period-goal bonuses — fixed premium for reaching the period bar; (5) combinations of the above. Open parameter questions (percent base, combination expressiveness) are deferred with the constructor.

## A.7 Stage-1 timeline & deferred items (research 16.08, architecture final)

M0 wks 1–4 (webhook, /start + consent, config versioning, scheduler + quiet hours, templates, audit; fixture CRM) → M1 wks 5–8 (real CRM, freshness SLO, degradation L1; gated on Zabot API verification) → M2 wks 9–14 (traffic light, income/forecast, recommendation engine, triggers/arbitration/floors, prompt library + LLM port, golden tests) → M3 wks 15–18 (owner reporting, degradation drills, Roskomnadzor file, pilot 1–2 salons). Deferred beyond Stage 1: pgvector similarity search, Telegram Mini App (RU-hosted when built), pseudonymization tokens, multi-provider routing, agentic capabilities, 5-type motivation-scheme constructor (backlog — when the service ships its own bonus module). CRM/Zabot sync is strictly read-only — two-way sync is not planned.

## A.8 Rejected alternatives & rationale

- **RU-native LLM provider (GigaChat/YandexGPT Tier 1, RU-hosted Qwen/DeepSeek Tier 2)** — recommended by the 11.08 research as the compliance-simple baseline. Rejected by owner decision 13.08 in favor of **OpenAI via depersonalization gateway** (RU storage + stripped-payload egress + art. 12 consent + Roskomnadzor notification). The single LLM port keeps the swap open without domain rework. Trade-offs carried: egress mechanism choice (OQ-6), intermediary ToS/volatility risk if a ruble-billed reseller is used, egress markup up to ~×4.3 model-dependent.
- **Generic motivation-scheme rule engine** — rejected for Stage 1: originally a fixed 5-type taxonomy with parameter schemas (A.6) was chosen to bound implementation complexity; **further superseded 23.08.2026** — Stage 1 now uses only the 2 Zabot plan types (avg check, total revenue), and the 5-type constructor itself is deferred to backlog (A.6).
- **Webhook-first CRM sync** — **reversed by owner decision 23.08.2026.** The original rejection ("watermark polling is the source of truth; webhooks only accelerate") is superseded: webhooks (unverified, marked pending API confirmation) are now the primary channel, REST polling covers entities without webhooks, and a nightly full reconcile heals missed events. Direction is strictly read-only (CRM/Zabot → agent). This corrects BRD §11.1 "двусторонняя синхронизация."
- **Additional Stage-1 roles (salon admin, platform operator, support)** — rejected by owner 13.08; closed set master + owner; owner config editing via reviewed CLI only.

## A.9 Architecture pointers (not normative for the PRD)

Deterministic engines + bounded LLM roles; hexagonal ports (LlmPort/CrmPort/TelegramPort/Clock/ConfigStore) with anti-corruption layer; DB-backed scheduling (UTC storage, transactional outbox, SKIP LOCKED); insert-only versioned config; audit tables; RLS multi-tenancy (owner-confirmed 23.08, §3.2); depersonalization gateway as Policy Enforcement Point with two-zone residency and RU-side name re-binding; test strategy (pytest, promptfoo golden set, contract tests, red-team guardrail tests). Full detail: `_bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/` (ARCHITECTURE-SPINE.md, SOLUTION-DESIGN.md — status final).

## A.10 Input reconciliation notes

- Gap report (10.08, vs v2.0) findings B1–B5, I1–I3: closed by v2.1 owner decisions (roles, freshness, traffic-light criteria, α, provider, scheme types restored). I4/I5/I6: resolved in this PRD (FR-4.5 rewording, F13, FR-7.1 terminology) — I5/I6 owner confirmation folded into OQ-4 and FR-7.6 config bounds.
- Owner letter "прошу подтвердить" items: freshness thresholds and traffic-light starting values are adopted as config-defined pilot-calibration parameters (not fixed numbers), matching the letter's own framing.

### A.10.1 Update 23.08.2026 — Team Q&A reconciliation (`docs/Вопросы_команды_и_ответы_по_БТ_v2_1.md`)

Source: owner answers to team questions + "Требуемые правки БТ" checklist. All changes owner-confirmed 23.08.2026.

| Change | OQ status | PRD ref |
|---|---|---|
| Access matrix + inter-salon isolation | OQ-2 resolved | §3.1, §3.2 |
| Communication floor / pause / opt-out / Principle 4 | OQ-4 resolved | F13 (FR-13.1–13.4) |
| Progress definition + cold start | OQ-8 resolved | FR-2.7, FR-2.8 |
| 5-type constructor → backlog; 2 Zabot plan types only | OQ-5 obsolete | FR-7.4, A.6 |
| 4 separate consents + revocation + aggregated profile | OQ-3 partially resolved | FR-1.1, FR-1.5 |
| Sync mechanism decided (webhooks + REST + nightly reconcile) | OQ-1 narrowed | FR-11.5 |
| CRM sync reversed (webhooks primary, was rejected) | override | FR-11.5, A.8 |
| Output validator + ruble calculation gate | new | FR-9.4, FR-9.5 |
| Agent calculation DB | new | FR-9.1 |
| Adaptive bar corridor (±15% / +10% / −15%) | new | FR-7.6 |
| Timezone split (salon TZ pre-visit, master TZ quiet) | new | NFR-F, FR-3.2–3.3 |
| Telegram: quiet hours guaranteed, inline keyboards | new | NFR-D, C-2 |
| Retroactive praise exception (≤60 min, same shift) | new | FR-11.3 |
| Direct IDs barred from prompts | new | C-1 |
| Salon as PDn operator of clients (commission processing) | new | C-1, FR-1.5 |
| Traffic-light calibration guidance | new | FR-6.3 |
| BRD v2.2 corrections required | new | OQ-12 |
| Attainment probability method | new [уточнить] | OQ-10, FR-7.6 |
| PDn operator legal entity name | new [уточнить] | OQ-11, FR-1.5, C-1 |
