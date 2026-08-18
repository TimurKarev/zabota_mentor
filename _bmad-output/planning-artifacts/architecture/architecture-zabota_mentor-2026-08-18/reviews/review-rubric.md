# Rubric Review — ARCHITECTURE-SPINE.md (Zabot AI Mentor, Stage 1)

- **Reviewed:** `_bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md`
- **Reviewer role:** rubric walker (good-spine checklist)
- **Date:** 2026-08-18
- **Verdict:** **APPROVE WITH REVISIONS** — no BLOCKING findings. Two HIGH findings (an internal contradiction between the module map and AD-11; a silent sub-dimension in the operational envelope) should be fixed before this spine is used as the gate for the level below.

## Severity Tiers

### BLOCKING

None. The spine decides the real divergence points for module-level design: pipeline-vs-agent (AD-1), port discipline (AD-2), CRM anti-corruption (AD-3), durability backbone (AD-4), data residency (AD-5), config versioning (AD-6), tenancy (AD-7), time (AD-8), degradation ladder (AD-9), arbitration centralization (AD-10), module boundaries (AD-11), delivery semantics (AD-12). The Deferred list is safe. The diagrams are valid mermaid and do convey structure. It is terse and decision-shaped.

### HIGH

**H-1. Module map contradicts AD-11: `llm` "(uses `messaging` rows)".**
The module→schema table gives `llm` no schema and states it uses `messaging` rows. AD-11 mandates "zero shared-table access across modules; cross-module calls only through each module's published interface." As written, the `llm` module is chartered to violate the boundary rule it is bound by. Fix is cheap but must land before module-level design starts, because it decides who owns prompt context assembly data flow: either `llm` reads only via `messaging`'s published interface, or `llm` is a library sub-component of `messaging` rather than a peer module. Two units could diverge on exactly this.

**H-2. Operational envelope: backup / DR / retention is silent.**
Deployment & environments (2 VMs, docker compose, Yandex Cloud, webhook-vs-polling profiles), infra/provider strategy (Yandex Cloud, Lockbox, Container Registry, self-hosted RU runner), and operations (Sentry/Grafana, user-visible SLO alerting) are all decided — good. But there is no decision, deferral, or open question for: Postgres backup cadence / RPO / restore procedure, PDn-retention periods (152-ФЗ requires a stated retention basis; the audit schema records export/delete requests but the spine never says how long correspondence and CRM-mirror data live), or what happens when the single Postgres dies. AD-4 makes Postgres the durability backbone for everything, so this is the one ops sub-dimension whose silence two units (worker/sync vs app, or later compliance tooling) could resolve differently. Add one row (decision or explicit deferral with owner) — likely also a BRD/owner input (retention period is a legal choice, so an Open Question is acceptable, but it must appear).

### MEDIUM

**M-1. Enforcement mechanisms are named unevenly across ADs.**
AD-1 (payload shape + promptfoo golden tests in CI), AD-3 (fixture CRM contract suite), AD-6 (config_version stored on every message/score row), AD-7 (salon key on every row) are concretely enforceable. AD-2 ("no external call from the domain layer", "no framework imports in domain"), AD-11 ("zero shared-table access"), and AD-8 (UTC storage) state the rule but name no enforcement — no import-linter/arch-unit test, no schema-ownership CI check. These are exactly the rules that erode silently in a monolith. One sentence naming the enforcement vehicle (e.g., import-linter contract in CI; a test asserting one-schema-per-module ownership) would close the gap.

**M-2. Capability map omits BRD sections that ADs themselves bind to.**
AD-10 binds "BRD §7.3, §12"; AD-1 binds "§9.2, §11.5, §15". The Capability → Architecture Map has rows for §5.2.1, §6, §8, §9, §10, §11, §12, §13, §14, and onboarding — but no row for §7 as a whole and none for §15. If §7 is proactivity/pacing it is arguably covered by the §12 row, but a reader auditing coverage from the map will conclude §7 and §15 are unplaced. Either add rows or narrow the AD bindings.

**M-3. AD-4 vs AD-12: dedup keys live in the "never durable" store.**
AD-12 dedups Telegram handlers on `update_id`; the only dedup facility the spine names is Redis ("dedup keys"), while AD-4 declares Redis holds "never durable state." A Redis flush therefore silently drops the dedup guarantee mid-redelivery-window. The outbox natural-key idempotency likely covers the effects, but the spine should say so explicitly (e.g., "update_id dedup is best-effort; outbox idempotency is the correctness backstop") — otherwise one unit implements Redis-only dedup and trusts it.

### LOW

**L-1. Stack version pinning is vague.**
"FastAPI — current stable", "aiogram 3.x", "PostgreSQL 16/17" defer the actual pin to the research doc dated 2026-08-16/17. Fresh enough to pass the verified-current bar today, but "16/17" leaves a real fork (two units could build on different majors). Pick one major per component at cold-start.

**L-2. Environments row covers only prod and dev.**
No staging/pre-prod is decided or explicitly deferred. Acceptable for Stage 1 given the webhook-secret and fixture-CRM story, but a one-word "no staging at Stage 1 (deliberate)" would make it a decision instead of a silence.

**L-3. `suppress_backdated_events` mechanism is under-specified.**
AD-9's "per-class flag on the trigger's source-data timestamp" is the tersest sentence in the document and is doing real work (never-send-retroactively is a honesty-contract rule). One more clause — where the flag lives (config row vs trigger definition, presumably AD-6-governed) — would prevent divergent readings.

**L-4. Diagram nits.**
- First diagram: `adapters -.implements.-> ports` is accurate but the domain→ports edge has no label; fine, but the ports subgraph mixes interfaces (`CrmPort`) with facilities (`Clock`, `ConfigStore`) — harmless.
- Structural seed: the `GW` (depersonalization gateway) box sits in the RU-zone subgraph but on no node; a reader must guess which VM runs it. One word ("on app VM" / "separate") fixes it.
- ER diagram: `APPOINTMENT }o--|| VISIT : becomes` encodes "many appointments → exactly one realized visit" (rebooking) — correct but worth confirming that is the intended semantics, since it forbids walk-in visits without an appointment row.

## Checklist Walk

| Check | Result | Notes |
| --- | --- | --- |
| Fixes the real divergence points for the level below; misses none | **Pass** | 12 ADs cover the genuine forks (LLM role, externals, CRM semantics, durability, residency, config, tenancy, time, degradation, arbitration, boundaries, delivery). Missed items are sub-dimensional (H-2, M-2). |
| Every AD's Rule is enforceable and prevents its stated divergence | **Pass with gap** | All ADs prevent their stated divergence; enforcement naming is uneven (M-1). No AD is aspirational. |
| Nothing under Deferred could let two units diverge | **Pass** | Queue library (Postgres-first is decided), egress mechanism (behind `LlmPort`), admin surface (AD-6 governs the boundary), Mini App, pgvector/tokens, multi-provider routing, horizontal scaling, ID formats — each deferral has its divergence point already pinned by an AD or a port. |
| Named tech is verified-current | **Pass** | Versions pinned by research dated 2026-08-16/17; vagueness noted (L-1). |
| Every owned dimension decided / deferred / open | **Pass with gap** | Deployment, environments, infra/provider, operations all present; backup/DR/retention silent (H-2); staging silent (L-2). |
| Diagrams valid mermaid and convey structure | **Pass** | All three render: graph LR, graph TB (`<-->` and cylinder syntax valid), erDiagram (cardinalities and quoted labels valid). Nits in L-4. |
| Build substrate (terse, decisions not rationale) | **Pass** | Exceptionally disciplined; rationale appears only as one-line "Prevents:" fields. |
| Internal consistency | **Pass with gap** | H-1 is a genuine AD-vs-module-map contradiction; M-3 a mild AD-vs-AD tension. Conventions table contradicts no AD. All capability-map AD references (AD-1…AD-12) point at real ADs — no dangling references. |

## Recommended fixes before the gate closes

1. Resolve H-1: give `llm` a boundary-compliant relationship to `messaging` (interface call or sub-component).
2. Add a backup/DR/retention decision, deferral, or open question (H-2).
3. Name enforcement vehicles for AD-2 / AD-11 / AD-8 (M-1).
4. Add or narrow §7 / §15 in the capability map (M-2).
5. One sentence in AD-12 subordinating Redis dedup to outbox idempotency (M-3).
