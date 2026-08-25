# Glossary — Zabot AI Mentor, Stage 1

> Working terms. Several BRD terms were corrected by the 23.08 owner decisions (§11.1 two-way sync removed; §11.2 5-type constructor → backlog); this glossary reflects the corrected, spec-canonical meanings.

| Term | Meaning |
| --- | --- |
| Goal (цель) | Owner-set plan in Zabot — one of 2 types only: **plan by master's average check** or **plan by total revenue**. Unified per salon, **read-only to the agent**; the AI never changes it and cannot. |
| Adaptive bar (планка) | Internal agent value (lives in the agent calculation DB) — the individual per-period trajectory of the master toward the Zabot plan. The AI adapts the bar and the path, never the goal. Corridor: ±15% deviation from calculated bar, +10%/period raise, −15% tactical floor (not below 2-period actual), bar cannot exceed the Zabot plan. |
| Motivation plan (план мотивации) | Stage 1: one of the 2 Zabot plan types (avg-check, total-revenue). The 5-type constructor (BRD §11.2) is **backlog**. |
| Tier (ступень процентов) | **Backlog only** — progressive-scale threshold; not in Stage 1 (no scheme constructor). |
| Recommendation (рекомендация) | A what/why/how offer hint for a specific client visit — the item, the history-based justification, and a ready phrase adapted to the master's psychotype and the client's context. |
| Check complexity (комплексность чека) | Services + goods per client per visit. |
| Traffic light (светофор состояния) | Green/yellow/red composite emotional-state status (0–100 score from screenings + LLM tone + CRM signals). Status transitions decided in code, never by the LLM. |
| Communication contract | Current frequency/tone/format agreements per master. |
| Day/week focus (фокус дня/недели) | The single priority concentrated on in the period. |
| Agent calculation DB | The agent's own Postgres schemas (`crm_mirror` replica + `engines`/`profile` derived values). CRM/Zabot is master of operational data + the 2 plan types; the agent is master of all derived data. Conflict excluded by construction (AD-3). |
| RenderFacts | Pydantic model owned by `messaging` — the bound-variables contract (message class, pre-computed facts, fallback template). The LLM may not invent, derive, or round any field absent from it (AD-1). |
| TriggerCandidate | The dispatcher's only ranking input (message class, expected income, deadline, source-data timestamps), published by engines (AD-10). |
| Output validator | Named egress component owned by `messaging`; hard-fails any mismatched money-type number or leaked placeholder, queueing a template fallback (AD-16). |
| Aggregated-profile-only mode | Mode entered on consent #3 revocation: raw correspondence and quotes deleted; aggregated profile (motivational type, scales + values, traffic-light status + transition history) retained (AD-17). |
| PDn operator | The service's legal entity (name pending — OQ-11). The salon is an independent PDn operator of its clients; the agent processes client data on commission (ч.3 ст.6 152-ФЗ). |
