# Reconcile Review — BRD v2.1 vs Architecture Spine (2026-08-18)

Reviewer role: reconcile check of `docs/zabot_ai.md` (BRD v2.1, 13.08.2026) against `ARCHITECTURE-SPINE.md`.
Method: every BRD section (§1–§16, appendices А/Б/В) checked for an architectural consequence; findings listed only where the spine ignores, drops, or contradicts that consequence. Pure product/content decisions excluded.

Overall: the spine is strong exactly where the owner decisions of 13.08.2026 are numeric and infra-shaped (freshness/degradation §5.2.1 → AD-9; smoothing α §6.5 and traffic-light criteria §10.2.1 → AD-6; 152-ФЗ §13.1 → AD-5). It is weak where the BRD's requirements are conversational, ethical, or stateful-but-quiet: the LLM's actual role, re-personalization after depersonalization, visit comments in the canonical model, config-completeness degradation, ethics enforcement state, and business-KPI instrumentation.

---

## BLOCKING

### B1. AD-1 ("LLM only rephrases pre-computed facts") contradicts BRD §10.2.1 — an owner decision dated 13.08.2026
BRD §10.2.1 makes the LLM a **classifier whose output is a number**: "LLM-оценка тона переписки (0–1)", with a fixed confidence threshold (≥ 0.7 / ≥ 0.8) gating traffic-light transitions, and "изменение тона определяется LLM-оценкой". This score is a required input stream to the composite state score (one of three weighted flows).

AD-1 as written says the LLM "may not emit a currency figure or metric it was not handed" and frames the LLM as a rephraser of deterministic facts. A 0–1 tone score with confidence is exactly a metric the LLM was not handed. The spine nowhere carves out the sentiment-classification call, so a literal reading of AD-1 makes §10.2.1 unimplementable.

The same under-specification infects the coaching loop: §9.5 requires the AI to diagnose barriers "по разговору" in MI style (открытые вопросы, работа с амбивалентностью), §9.3 requires generating 2–3 focus options in GROW, Appendix Б requires adaptive onboarding dialogue, Appendix А.5 requires in-chat phrase rehearsal ("напиши, как бы ты сказала, а я подскажу"). These are multi-turn generative dialogues, not rephrasing.

**Fix:** amend AD-1 to define the LLM's permitted roles explicitly: (a) constrained rephrasing of bound facts for narrative messages; (b) structured-output classification (tone score + confidence, barrier classification) whose outputs feed deterministic engines but never reach the master unvalidated; (c) bounded coaching dialogue under versioned prompts where all figures remain bound variables. Keep the invariant that no *money/score/ranking* figure is ever LLM-authored, and that classification below the confidence threshold cannot change state — the rest of AD-1 stands.

---

## HIGH

### H1. No re-personalization step after the depersonalization gateway (§13.1 × Appendix А)
BRD §13.1: the gateway strips direct identifiers — ФИО, контакты, **имена клиентов** — before egress; the LLM sees only обезличенный контекст. Yet every example message in Appendix А is addressed by name ("Доброе утро, Марина!") and references clients by name ("В 14:00 — Анна К."). BRD §8.3 requires the "как" part of a recommendation to be a ready phrase adapted to the client's context.

Architectural consequence the spine drops: the LLM must generate against placeholder/pseudonym tokens and final message assembly must **bind real names inside the RU zone after the LLM returns** (same mechanism as bound numeric variables, extended to identifiers). Without this, either depersonalization is violated (names sent to OpenAI) or messages cannot contain names at all. The spine's `llm` module ("prompt assembly, LlmPort calls, template fallback") and AD-5 are silent on the return path.

### H2. Canonical model omits visit comments (§5.2, §8.1, §8.2)
BRD §5.2 requires from CRM "история визитов… включая комментарии к визитам". Comments are load-bearing, not decoration: §8.1 lists them as a recommendation signal (жалобы на сухость, планы «отрастить длину», аллергии), and §8.2 makes them a hard exclusion filter ("противопоказания/аллергии из комментариев"). §10.1 does not use them, but the recommendation engine cannot be correct without them.

The spine's canonical model (AD-3, ER diagram) has `Master, Client, Appointment, Visit, CheckLine` — no comment entity, and the CRM-mirror sync/watermark design never mentions syncing them. Since comments are free text, they also interact with AD-5: they flow into prompts and must pass the depersonalization gateway.

**Fix:** add `VisitComment` (or `Visit.commentary`) to the canonical model, sync it with its own watermark/freshness class, and route it through the gateway like other narrative context.

### H3. Ethics constraints have no enforcement home (§15, §2, §10.3)
The BRD's quiet requirements with real state/architecture consequences:

- "уважает «нет» мастера: любое настойчивое предложение делается **максимум дважды**, дальше — фиксация в профиле" — requires a per-topic/per-offer insistence counter in the profile module and a dispatcher/engine check that suppresses the third attempt. Nothing in the spine models this counter or the suppression rule.
- "не сравнивает мастеров между собой", "не угрожает эскалацией", "не манипулирует… не использует чувство вины" — these are prompt+eval constraints, but the spine's golden tests cover only "facts present, no invented numbers" (AD-1). There is no ethics/register eval set (e.g., no cross-master comparison strings, no guilt/threat language, register held per motivational type per Appendix А).
- §10.3: escalation to the owner must carry "только вывод и рекомендацию… без цитат переписки" — the capability map says "aggregate only, no quotes" for §14, but the red-status escalation path (§10.2/§10.3) is a distinct, out-of-period message flow; the spine doesn't say where the redaction/aggregation boundary is enforced for it.

**Fix:** add an insistence-counter state to `profile`, a dispatcher-level suppression rule, and extend the promptfoo golden set with tone/ethics cases per motivational type and per escalation report.

---

## MEDIUM

### M1. Two-way Zabot goals sync absent (§11.1)
BRD §11.1 places the goals/premium module inside the service "с возможностью двусторонней синхронизации с Zabot", with a future read-only mode if Zabot ships its own goals. The spine has only `CrmPort` (one-directional polling for CRM data). There is no port, module responsibility, or deferred decision for outbound goal/bars/premium-config replication to Zabot. Either add a deferred item + port sketch (`GoalsSyncPort`) or record the owner decision to drop stage-1 sync — currently it is silently missing.

### M2. Config-completeness degradation mode missing (§11.2)
BRD §11.2: "при неполной конфигурации схемы ИИ не выдумывает цифры дохода — использует только метрики… и запрашивает у собственника уточнение настроек". This is a third degradation ladder (alongside AD-9's CRM freshness): a *config* completeness check that suppresses monetary figures and emits an owner-clarification request. AD-6 validates config shape at the editing boundary but says nothing about semantically incomplete scheme configurations at decision time. AD-9 covers only stale CRM data, not absent/misconfigured motivation schemes.

### M3. Profile-change explainability not in the audit surface (§6.5)
BRD §6.5: "каждое значимое изменение профиля логируется с обоснованием (объяснимость для отладки и для отчёта собственнику)"; type change only after ≥ 2 зарплатных periods of sustained divergence; explicit master requests override the model immediately. The spine's `audit` enumeration is "config changes, consent events, export/delete requests, sync runs" — profile scale/type changes and their justifications are absent, and MESSAGE_LOG/TRAFFIC_LIGHT_SCORE carry `config_version` but no analogous `profile_version` provenance. Also worth stating as an engine rule: type-change gating by pay periods, not wall-clock.

### M4. Business KPI module unmapped (§16), with a measurability trap
BRD §16 requires system-quality KPIs: доля прочитанных и отвеченных сообщений, конверсия рекомендаций в чек, доля «зелёных» недель, доля мастеров, попросивших снизить частоту. The spine's observability row is entirely operational SLOs (freshness, outbox age, error rates). No module owns business-KPI computation/storage, and nothing feeds the owner's period report (§14) or the pilot calibration the BRD repeatedly relies on (α calibration "на исторических данных пилота", traffic-light thresholds "калибруются на пилоте" — both §6.5/§10.2.1 owner decisions presuppose KPI instrumentation exists).

Measurability note to surface to the owner: the Telegram Bot API provides no read receipts, so "доля прочитанных" is not directly measurable — only answered/ignored. The same limitation affects §6.5's behavioral stream ("читает ли сообщения") and §10.1's ignore detection; the architecture should define engagement as reply/ignore-based and flag the delta to the BRD owner.

### M5. Memory lifecycle rules dropped (§13)
BRD §13: "приоритет актуальности: свежие сигналы весят больше старых; устаревшие наблюдения архивируются"; "негативные эпизоды хранятся только как материал для подбора поддержки" (memory-for-help-not-pressure is also §2). The spine's `profile` module owns scales/state but there is no recency weighting, archival, or negative-episode handling policy anywhere. Consequence: prompt assembly will naively include stale or harmful-context memories. Needs a stated rule (what is archived when, what may enter a prompt) — this is also a quiet ethics/§13.1 interaction, since memory content crosses the gateway.

---

## LOW

### L1. AD-6 parameter enumeration drops owner inputs (§5.1)
AD-6's list omits: приоритетные услуги/товары, стоп-лист, зарплатный период, referral/refusal pause N (§8.2). The "all business parameters" catch-all arguably covers them, but the enumeration is what implementers read; the stop-list in particular gates the recommendation engine and should be named.

### L2. Channel-independence not stated as a constraint (§3.1)
"Все требования к формату, частоте и тону не зависят от канала", with own mobile app + Zabot duplication named as the growth path. The spine's messaging/dispatcher design is Telegram-shaped (chat_id as identity anchor, per-chat token buckets). Fine for stage 1, but one sentence — message rendering channel-agnostic, Telegram specifics confined to the adapter — would honor the BRD's stated future. The Deferred section's "Telegram Mini App" only partially covers this (the BRD says own app, not Mini App).

### L3. Screening content and register enforcement not versioned (§4, §10.1, Appendix Б)
BRD §4 makes the scientific models a requirement on prompts ("промпты и логика ИИ должны явно опираться на перечисленные модели, а не на интуитивную психологию"), and WHO-5-based check-ins are semi-structured content. Prompt templates and screening instruments should be versioned artifacts under AD-6-style governance with the models named; currently only "promptfoo golden set" is mentioned, and prompts are not in the config/audit story. Overlaps with H3's eval-set gap.

### L4. First-two-weeks calibration mode (Appendix Б)
"Первые 2 недели — режим калибровки: ИИ чаще спрашивает обратную связь о формате" — a profile-state-driven messaging mode. Small, but it is a distinct scheduler behavior tied to profile age; worth a line in `profile`/`messaging` ownership so it isn't lost.

---

## Section-by-section pass (covered / no finding)

- §1, §2 (goals owner-only, adapt path not goal, no cross-master comparison in master-facing comms) — covered by engines + AD-1/AD-10 except as noted in H3.
- §3 role model (closed set, no admin/support roles stage 1) — consistent; Q2 correctly carries the open isolation question; owner-config CLI in Deferred is compatible.
- §3.1 channels — Telegram-first honored; see L2.
- §5.2.1 freshness/degradation (owner decision 13.08.2026) — AD-9 is a faithful, complete implementation, including no retroactive event messages and post-recovery recompute. Best-covered owner decision in the spine.
- §5.3 explicit preferences apply immediately — AD-10 covers.
- §6.1–§6.4 hybrid type+scales, onboarding — profile module + capability map cover; see M3, L4.
- §7.1–§7.3 caps, floors, quiet hours, ignore-rate rule — AD-10 + AD-8 cover thoroughly, including the "money class disabled last" ladder.
- §8 engine (candidates/filters/rank/1–3 cap, no-survey reconciliation) — AD-1/AD-3/AD-12 cover; comment gap is H2.
- §9.1–§9.5 rhythms, GROW, forcing/sprint/recovery — engines + messaging cover the trigger math; conversational side is B1.
- §10.1–§10.3 — §10.2.1 is B1; escalation confidentiality is H3; screening ethics otherwise prompt-level.
- §11.3–§11.5 adaptive bar, transparency of income — engines + AD-6 cover bar logic and on-demand income questions; scheme-config gap is M2, Zabot sync M1.
- §12 proactivity triggers + arbitration — AD-10 covers, including trigger competition and merge/defer.
- §13.1 LLM provider / 152-ФЗ (owner decision 13.08.2026) — AD-5 is faithful (RU residency, gateway, art. 12 consent + RKN notification as launch gates, LlmPort for swap); Q3/Q4 match the BRD's open questions. Return-path gap is H1.
- §14 owner report — capability map covers aggregate-only reporting; red-status escalation path noted in H3; systemic cross-master pattern (assortment problem) is engine work, no structural gap.
- §16 — M4.
- Appendices А/Б — register/calibration findings (B1, H3, L3, L4); Appendix В glossary — no architectural content.

## Verdict

**Revise before build.** One blocking contradiction (AD-1 vs §10.2.1 owner decision + generative coaching), three high gaps (re-personalization return path, visit comments in the canonical model, ethics-enforcement state and evals), and five medium drops (Zabot goals sync, config-completeness degradation, profile-change audit, business-KPI module, memory lifecycle). None of the fixes require a paradigm change — the hexagonal/pipeline shape holds — but AD-1 must be reworded and the canonical model, audit surface, and golden-test scope extended before stories are cut against this spine.
