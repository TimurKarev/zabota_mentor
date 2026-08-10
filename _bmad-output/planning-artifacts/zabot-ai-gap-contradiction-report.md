# Gap & Contradiction Report — ИИ-помощник мастера Zabot (BRD v2.0)

**Analyst:** Mary (Business Analyst) · **Date:** 2026-08-10 · **Source:** `docs/zabot_ai.md` (281 lines, v2.0)
**Scope:** Requirements analysis — completeness, white spaces, contradictions, Russian-market & legal fit.

> **Headline finding:** The document is strategically coherent and unusually strong on product psychology, but it reads as a **converted export with systematically dropped tables/lists**. Roughly **10 structural sections are empty headings** (textual prose survives, enumerated tables/lists do not). Several of these empty tables are **load-bearing control-flow** (traffic light, barrier matrix, motivation-scheme types, proactivity triggers) — i.e. the system's behavior literally cannot be implemented as written because the decision rules are absent. On top of that, the **money/LLM boundary** and the **CRM integration contract** — the two highest-risk implementation areas — are not defined anywhere.

---

## How to read this report

Each finding is tagged: **[Completeness]**, **[White Space]**, **[Contradiction]**, **[Market/Legal]**.
Severity tiers: **BLOCKING** (cannot implement / cannot ship legally) → **IMPORTANT** (forces rework or ambiguity in core flows) → **NICE-TO-HAVE** (polish, clarify later).

Findings within a tier are roughly ordered by blast radius.

---

# TIER 1 — BLOCKING

## B1 — [Completeness] §3 «Участники» is entirely empty; no actor/permission model exists
**Section:** §3 (lines 28–29 — heading only, body absent).
**What's missing:** The actors table and, with it, the entire role/permission model. The text later implies at least **мастер**, **собственник/управляющий**, the **AI service itself**, and a **Zabot/CRM** system; likely also a ** salon administrator** and a **platform operator/support**. None are enumerated, and there is no statement of who can read/write what.
**Structural bug confirming conversion loss:** `§3.1 Каналы коммуникации` appears physically *under* the §4 «Научная основа» heading (line 33) but carries a §3.x number — an orphaned subsection whose parent body was dropped. This is the signature of a broken markdown/table conversion, not deliberate omissions.
**Why it matters:** AuthN/AuthZ, data isolation between salons, the confidentiality boundary between master↔owner (§13, §10.3), and report scoping (§14) all depend on a roles model. You cannot design the data model, API authorization, or the escalation rules without it.
**Resolution / questions:**
- Restore the actors table. Minimum columns: *actor · authentication · data they can read · data they can write · actions they can trigger*.
- Confirm the full actor set. Is there a per-salon manager distinct from owner? A platform-level operator with cross-salon access? An auditor role?
- Decide where the **AI service** sits as an actor: is it a trusted system principal with full read on master PD, or constrained?

## B2 — [White Space] No Zabot/CRM integration contract (the data backbone is undefined)
**Section:** §5.2 (data sourced «через Zabot»), §11.1 («двусторонняя синхронизация с Zabot»), §14.
**What's missing:** The entire integration contract — API surface, schema, sync direction(s), real-time vs batch, push vs pull, idempotency, conflict resolution, failure/timeout handling, and the read-mode fallback mentioned in §11.1 («режим чтения»). §5.2 lists *what* data is needed but not *how* it arrives or how fresh it must be.
**Why it matters:** CRM data is the sole ground truth for: income math (§11.5), recommendation-effect measurement (§8.4 — explicitly «только по цифрам из CRM»), mood via CRM proxies (§10.1), and bar/progress logic (§9.4). The whole feedback loop collapses if sync is stale, partial, or lossy. §8.4 even states the system **cannot distinguish** «didn't offer» from «client refused» from CRM alone — so data quality is a first-class design constraint, not a detail.
**Resolution / questions:**
- Specify contract: transport (REST/webhook/gRPC), entities (client, visit, receipt line, appointment, shift, cancellation), ownership of IDs, and a **freshness SLA** per entity (e.g. receipts ≤ N minutes; schedule real-time).
- Define the **sync master** per field (who wins on conflict — especially for the goals module §11.1, which is bi-directional).
- Specify degradation behavior: what the AI does when CRM is unreachable or stale (see B6/W5).

## B3 — [White Space] No separation between deterministic money math and LLM narrative
**Section:** §9.2 («прогноз дохода ≈ X ₽»), §11.2, §11.5 («сколько я уже заработал? … ИИ отвечает расчётом»), §15 («честен в цифрах: не приукрашивает прогноз»).
**What's missing:** An explicit architectural boundary stating that **all money figures, forecasts, bar values, and «next %» calculations are computed deterministically** from CRM + the salon's motivation scheme, and the LLM is only permitted to *narrate* pre-computed numbers — never to generate, estimate, or round them.
**Why it matters:** This is the single highest correctness + ethics + trust risk in the product. §15 promises honesty in numbers; §11.5 promises exact answers on demand. If an LLM produces income figures, it will hallucinate them (wrong % thresholds, invented bonuses, rounded-up «motivational» forecasts). That is both a financial-accuracy defect and a direct violation of the stated ethics (§15). §11.2 already half-anticipates this («при неполной конфигурации схемы ИИ не выдумывает цифры дохода») — but the rule must be generalized and enforced structurally, not left to prompt discipline.
**Resolution / questions:**
- Add an architecture rule: **Money/projection/bar math = deterministic service; LLM = phrasing only.** The LLM receives computed values as bound variables and is forbidden from emitting currency figures it wasn't handed.
- Define the projection model inputs (current metrics, period elapsed, scheme rules) and mark it as a versioned, testable component.

## B4 — [Market/Legal] 152-ФЗ — provider choice & data localization not addressed (likely blocking)
**Section:** §10.1 (mood/WHO-5 screenings), §6 (psychological profiling), §13 (long-term memory of profile + mood + correspondence), §3.1 (Telegram channel).
**What's missing:** No statement on **where personal data is processed and stored**, no consent architecture, no LLM-provider decision. The system collects (a) a *psychological profile*, (b) *mood/emotional-state data* (energy 1–5, WHO-5-derived check-ins), (c) *behavioral* signals, and (d) free correspondence — and infers mental-state conclusions («красный» distress, §10.3). Under 152-ФЗ this is personal data; mood/psychological-state data is arguably **special-category-adjacent** and demands heightened handling.
**Why it matters:**
- **Localization:** PD of Russian subjects must be stored in databases **in the Russian Federation** (entry in the registry of PD operators). Routing master correspondence + profile through an OpenAI-via-proxy stack where the data leaves the RF is non-compliant absent depersonalization/adequacy handling. GigaChat / YandexGPT keep processing in-RF and are the compliant default.
- **Consent:** Must be specific, informed, for enumerated purposes; purpose limitation bars reusing profiling/mood data beyond the stated coaching purpose; data subjects have access/correction/deletion/withdrawal rights.
- **Profiling + automated decisions:** §6 is automated profiling of employees by an employer's tool — this touches labor and PD-protection sensitivities and may require explicit consent and transparency.
**Resolution / questions:**
- Commit to an **in-RF LLM provider** (GigaChat/YandexGPT) as the compliant baseline; if a foreign model is contemplated, define the depersonalization boundary and justify it.
- Design the **consent flow** (separate consents advisable: profiling, mood data, correspondence retention) with withdrawal mechanics — this links directly to C2 (no real opt-out defined today).
- Register as a PD operator; define retention periods (§13 says stale observations are «archived» but gives no schedule or deletion rule).

## B5 — [Completeness] §11.2 «Типы схем мотивации» is empty — but money math depends on it
**Section:** §11.2 (lines 179–180 — «Поддерживаемые типы схем» list absent, «список расширяемый»).
**What's missing:** The enumerated schema types the goals module must store and the AI must compute against (e.g. flat %, progressive %-tiers, bonus thresholds, category-rate, hybrid). The section explicitly makes AI income math *conditional on the salon's specific scheme* («по формуле салона, а не по универсальному шаблону»), yet the set of supported schemes — the schema of `scheme type + parameters` — is missing.
**Why it matters:** This directly blocks B3. You cannot build the deterministic money engine without the scheme taxonomy and each scheme's parameter contract (tier boundaries, rates, bonus rules, caps, period boundary). §11.5's on-demand income queries are unimplementable without it.
**Resolution / questions:**
- Ship a **v1 scheme taxonomy** (say 3–5 canonical schemes) with a parameter schema per type, even if the list is meant to grow.
- Confirm whether arbitrary custom schemes must be supported (rule-engine) or only the enumerated set (fixed code paths). This materially changes scope.

---

# TIER 2 — IMPORTANT

## I1 — [Completeness] Four empty tables that are *referenced as control flow*
These are empty headings, but unlike a glossary, the system **branches on their contents elsewhere**, so their absence creates downstream ambiguity:

| § | Heading | Empty content | Where it's used as logic |
|---|---|---|---|
| §6.3 | Профильные шкалы (0–100) | the scale set | §8.3 («шкала уверенность в продажах»), §10.1 (energy), behavior tuning |
| §9.1 | Три ритма | the three rhythms | §9.2 (shift), §9.3 (period) — only **two** are self-evident; the third is unknown |
| §9.5 | Барьеры (знание/навык/психология) | intervention matrix | §8.4 & §9.5 invoke a coaching intervention chosen «по типу барьера» |
| §10.2 | Светофор состояния | green/yellow/red criteria | §7.3 caps, §9.4 force/relax, §10.3 escalation, §14 reports, §16 KPIs **all branch on this status** |

**Why it matters:** The traffic light (§10.2) is the most damaging gap — it is a state variable consumed by at least five other sections, yet its **transition criteria are undefined**. Implementers will invent five different definitions. §9.1 «three rhythms» is ambiguous (shift + period are visible; the third is not).
**Resolution:** Treat all four as required-to-implement, not prose. For §10.2, define **entry/exit criteria for each color** and the inputs (mood + tone + CRM proxies). For §9.1, name the third rhythm explicitly. For §6.3, enumerate the canonical scales. For §9.5, give the barrier→intervention table.

## I2 — [Completeness] §6.2 «Мотивационные типы» empty — but recoverable from Приложение А
**Section:** §6.2 (lines 65–67 — heading + caveat only, no list of the «пять архетипов»).
**What's missing:** The canonical list of 5 archetypes is absent **in §6.2**, but **Приложение А fully describes all five** with tone examples: **Достигатор, Соревнующийся, Стабильный профессионал, Заботливый сервисник, Осторожный/тревожный.**
**Why it matters:** Lower severity than B5/I1 because the information exists elsewhere — but §6.2 is the normative location and §7.2 («стартовые настройки по типам») is also empty, so the type→default-settings mapping (frequency, tone, length, challenge/support ratio) that §6.1 promises («задаёт стартовые настройки») is missing.
**Resolution:** Restore the 5-type list in §6.2 (copy names from Прил. А) and populate §7.2's type→default-settings table. Decide whether types are normative presets or illustrative.

## I3 — [Completeness] §12 «Проактивность ИИ» triggers list is empty
**Section:** §12 (lines 198–200 — «ИИ имеет право сам инициировать контакт по триггерам:» followed by no list).
**What's missing:** The enumerated proactive triggers. The surrounding text gives the **policy** (priority by income value, throttle per §7.3, merge on conflict) but not the **trigger set**.
**Why it matters:** Proactivity is a headline product property («проактивный персональный ассистент»). Without the trigger list there is no spec for what initiates contact. Some triggers are inferable from elsewhere in the doc (near-next-% threshold §9.4, recurring-product depletion §8.1, red-status §10.2, missed-recommendation coaching §8.4/§9.5) — consolidate them here.
**Resolution:** Author the trigger catalogue, each with: *condition · channel · priority · min-interval · which types it applies to*.

## I4 — [Contradiction] «Zero surveys / zero load» (§8.4) vs mood screenings 2–3×/week (§9.2, §10.1)
**Section:** §8.4 («Никаких опросов и отчётности — ноль дополнительной нагрузки») vs §9.2 («лёгкий скрининг настроения … 2–3 раза в неделю») and §10.1 (energy 1–5 + WHO-5-derived check-ins every 2 weeks).
**The tension:** A mood screening that asks the master to self-rate **is** a survey question. «Zero surveys» is literally violated by mandated 2–3×/week check-ins. The intent is clearly different (no *performance* reporting burden vs allowed *care* check-ins), but the spec doesn't say so.
**Why it matters:** This is a recurring ambiguity implementers and reviewers will flag; it also muddies the KPI in §16 («доля мастеров, попросивших снизить частоту»).
**Resolution:** Reword §8.4 to scope the prohibition precisely: **no performance/compliance reporting surveys**; *care-oriented* brief check-ins are permitted and governed by §10. State that check-ins are optional (§10.3 already allows non-response as a signal).

## I5 — [Contradiction] «Communication never stops» (§2, §7.3) vs right to reduce frequency with no full opt-out
**Section:** §2 («Коммуникация не прекращается никогда»), §7.3 (same, + «пиши реже … применяется немедленно»), §6.5, §16 (KPI of masters who asked to reduce).
**The tension:** «Never stops» is absolute; yet autonomy is a stated core value (SDT, §6.4) and the system tracks how many masters ask to reduce contact. There is **no defined hard stop, pause, or full opt-out** — only frequency reduction down to an implied floor («итоги периода и рекомендации перед визитами отключаются последними»).
**Why it matters:** Legally and ethically, an employee-facing automated messenger with no true off-switch is a red flag (links to B4 consent/withdrawal). Product-wise, «never» clashes with the autonomy principle.
**Resolution:** Define an explicit **minimum contact floor** (already half-stated) **and a real pause/opt-out path** (e.g. vacation mode, «mute for N days», or full withdrawal that degrades to legally/contractually required notices only). Reconcile the word «never» with this.

## I6 — [Contradiction] «AI adapts the path, not the goal» (§2) vs the bar being «tactically lowered» (§11.4)
**Section:** §2 («адаптирует планку и путь, а не цель») vs §11.4 (bar «может быть тактически снижена … чтобы сохранить ощущение достижимости») and §9.4 (force/relax the bar).
**The tension:** Lowering the bar *is* changing the target the master is measured against. The slogan and the mechanism conflict unless «goal» and «bar» are carefully distinguished — which the spec gestures at (§11.3: unified goal vs *adaptive individual bar*) but doesn't lock down.
**Why it matters:** This is the kind of imprecision that produces contradictory stakeholder interpretations and gaming of the bar.
**Resolution:** Define terminology cleanly: **Goal** (owner-set, unified, immutable by AI) vs **Adaptive bar** (per-master, per-period, AI-adjustable within owner rules). Rewrite §2 as «adapts the *bar and path*, never the *goal*». Make explicit the floor/ceiling rules within which the bar may move (owner constraints, §11.4).

## I7 — [White Space] Profiling math is undefined
**Section:** §6.5 («шкалы двигаются плавно (экспоненциальное сглаживание)»; type change at «≥ 2 зарплатных периодов»), §9.4 («устойчивый прогресс ≥ 2 недель»), §11.4 (bar movement on «прогресс»/«стагнация»/«спад»).
**What's missing:**
- **Smoothing weights / alpha** and per-signal normalization (how a 1–5 mood maps onto a 0–100 scale; how a behavior signal weights vs an answer).
- **«Progress» is undefined** — progress toward the bar? absolute metric growth? sustained-at-bar? It gates forcing (§9.4) and bar raises (§11.4), so its definition changes income trajectories.
- **Type-change mechanics:** «≥2 periods of sustained divergence» — divergence *measured how*? There is no function from the scale-vector back to a type (see I8).
**Why it matters:** Profiling is the personalization engine; undefined math means unrepeatable, untestable behavior and no explainability (contradicting §6.5's own logging-for-explainability requirement).
**Resolution:** Specify at least: smoothing constants (or that they are tuned per-scale with a documented method), the normalization scheme, an operational definition of «progress», and the type↔scale mapping (I8).

## I8 — [White Space / Contradiction] The type ↔ scale relationship is underspecified
**Section:** §6.1 (type = «preset»; scales drive real behavior; «тип может быть пересмотрен»), §6.5 (type change rule).
**The gap:** §6.1 claims a clean hybrid (type for explainability, scales for precision) but never defines **how the scale-vector maps to a type** or **when the type is recomputed**. «Divergence from type for ≥2 periods» needs a divergence metric that doesn't exist.
**Why it matters:** Type and scales will drift inconsistently; the «preset» becomes stale or contradicts the live scales, undermining the explainability story §6.1 is built for.
**Resolution:** Define the type↔scale mapping function (or state that type is a *labeling* of a scale-vector cluster and give the clustering rule), and the recomputation cadence/triggers.

## I9 — [Market/Legal] Multi-timezone model absent (Russia = 11 time zones)
**Section:** §7.3 («тихие часы 21:00–9:00 локального времени»), §9.2 («перед визитом за 30–60 минут»).
**What's missing:** A timezone model for masters, salons, and appointments. «Local time» is undefined when a master and a salon and a CRM appointment can each carry a different zone; Russia spans UTC+2 to UTC+12.
**Why it matters:** Quiet-hours enforcement and pre-visit timing — the two most «money»-adjacent message types — depend on correct tz math. Getting it wrong means messaging masters at 23:00 or after the client already arrived.
**Resolution:** Define tz storage (per master and per salon, derived at onboarding), appointment tz source (CRM), and the quiet-hours evaluation rule. Note Russia has no DST since 2011, so the model is static zones — simpler, but still must be modeled.

## I10 — [White Space] Cold-start / missing-data fallbacks not generalized
**Section:** §6.4 (onboarding analyzes CRM history — silent on the no-history case), §11.2 (incomplete scheme → ask owner, good), §8.2 (recommendation ranking needs history).
**What's missing:** A general fallback hierarchy when CRM data is sparse (new master, new salon, new client, first visits). §11.2 handles one case (incomplete scheme config); the rest is implicit.
**Why it matters:** Cold-start is the first experience for every new salon onboarded; a weak cold-start kills adoption and the projection/bar logic (B3) has nothing to compute on.
**Resolution:** Define per-entity fallback states (new master → conservative bar from defaults; new client → category/seasonality priors; no CRM link → degraded mode with explicit messaging).

---

# TIER 3 — NICE-TO-HAVE / CLARIFY

## N1 — [Completeness] §4 «Научная основа» promises an enumerated model list but only states the requirement
**Section:** §4 (lines 30–31).
The section requires prompts/logic to cite named models (SDT, Locke–Latham, MI, WHO-5, promotion/prevention appear scattered) but never consolidates them into the promised scientific-basis table. Consolidate so the «evidence-based» claim is auditable.

## N2 — [Completeness] Приложение В «Глоссарий» is empty
**Section:** Прил. В (lines 280–282). Low impact now, but terms (барьер, планка, цель, светофор, ритм, рычаг схемы, NBO) recur with overloaded meaning — a glossary prevents drift. Populate after I6 terminology is settled.

## N3 — [Market/Legal] Telegram channel specifics
**Section:** §3.1. Telegram gives no guaranteed delivery/read receipts, no native scale widget (build via inline keyboards), and bot-side rate limits; a bot can only *defer* sends, so quiet-hours compliance is best-effort. Also: Telegram storage of correspondence interacts with 152-ФЗ (B4). Worth a short «channel constraints» note.

## N4 — [Contradiction] Forcing requires master consent (§9.4 GROW) — ensure all §12 proactivity respects that gate
**Section:** §9.4 («мастер сам подтверждает готовность») vs §12 automated triggers. Risk: an automated trigger initiates a «спринт» without the consent gate. Make explicit that any force/sprint trigger passes through the §9.4 GROW consent check.

## N5 — [White Space] Confidentiality boundary «aggregate vs detail» (§13, §10.3, §14) needs a definition
The spec says correspondence is never shared «except as aggregated conclusions», and red-status escalation carries «вывод и рекомендация … без цитат». Define what counts as aggregate (thresholds, no verbatim, no quote length) so the boundary is enforceable, not judgment-based.

## N6 — [Completeness] KPIs (§16) reference undefined inputs
«Доля зелёных недель» needs §10.2 defined (I1); «конверсия рекомендаций» needs the §8.4 CRM-measurement caveat formalized; «вышедших на следующий уровень схемы» needs §11.2 types (B5). Resolving the blocking/important items unblocks the KPI layer.

---

# Summary scorecard

| Theme | Count | Severity mix |
|---|---|---|
| Empty / dropped sections | 10 (§3, §6.2, §6.3, §7.2, §9.1, §9.5, §10.2, §11.2, §12, Прил.В) | 2 Blocking, 5 Important, 3 Nice |
| Undefined mechanisms (white space) | 6 (integration, money/LLM, profiling math, consent, cold-start, confidentiality) | 3 Blocking, 3 Important |
| Contradictions | 4 (zero-surveys vs screenings; never-stops vs opt-out; path-not-goal vs lowered bar; type↔scale) | all Important |
| Market/legal (RU) | 4 (152-ФЗ/provider, consent, tz, Telegram) | 1 Blocking, 2 Important, 1 Nice |

**Top 3 to resolve first:** B4 (152-ФЗ/provider — sets the entire infra direction), B2+B3 (CRM contract + money/LLM boundary — the engine room), B5+I1 (scheme types + traffic light — the missing control-flow tables). Everything else is tractable once these are pinned.

---

*Prepared by Mary, Business Analyst. Findings grounded in `docs/zabot_ai.md` v2.0 as supplied; severity reflects implementation readiness for a Telegram-first MVP in the Russian market. Recommend a follow-up clarification session on the BLOCKING items before architecture begins.*
