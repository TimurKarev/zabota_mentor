---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments: []
workflowType: 'research'
lastStep: 6
research_type: 'technical'
research_topic: 'Stage-1 reference architecture — technology stack and deployment for a Telegram-first AI coaching service for beauty salon masters (Zabot AI Mentor), integrated with Zabot CRM, compliant with 152-ФЗ'
research_goals: '1) Zabot CRM integration surface (API/webhooks/exports, entities, polling/push model) + anti-corruption layer design; 2) Timezone-aware scheduled messaging engine (quiet hours, pre-visit triggers, frequency floors, degradation modes); 3) Stack & deployment under RU data-residency constraints (backend, DB, RU hosting comparison, CI/CD, depersonalization gateway); 4) Versioned, auditable runtime configuration of business parameters. Deliverable: recommended stage-1 reference architecture with trade-offs and CRM-owner-dependent open items.'
user_name: 'Timurkarev'
date: '2026-08-16'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-08-16
**Author:** Timurkarev
**Research Type:** technical

---

## Research Overview

This research establishes the stage-1 reference architecture for the **Zabot AI Mentor** — a Telegram-first AI coaching service for beauty-salon masters, integrated with Zabot CRM and compliant with 152-ФЗ (RU personal-data law). It answers four priority questions: (1) the Zabot CRM integration surface and anti-corruption-layer design, (2) a timezone-aware scheduled messaging engine with quiet hours, tiered freshness degradation, frequency floors and caps, (3) the technology stack and deployment model under RU data-residency constraints including a depersonalization gateway for LLM calls, and (4) versioned, auditable runtime configuration of business parameters.

The method was live web research with source verification at every step (Steps 2–5 above), cross-checked against the business requirements document (`docs/zabot_ai.md` v2.1) and revised after an external gap review — the freshness tiers, trigger arbitration, recommendation-engine sketch, frequency floors, owner reporting, and risk rows 7–8 in the body above come from that revision pass.

The headline finding: a deliberately conservative architecture — Python modular monolith, PostgreSQL as the durability backbone, two container VMs in Yandex Cloud — wins because the three binding constraints are integration uncertainty (Zabot CRM has no public API docs), provider geo-blocking (OpenAI blocks RU IPs), and legal zoning (all PDn in RU, only depersonalized context abroad). The full narrative, executive summary, and strategic recommendations follow in the Research Synthesis section below.

---

## Technology Stack Analysis

*Researched 2026-08-16. Sources verified via live web search; confidence levels marked per claim.*

### Programming Languages

The workload profile is unusual: ~90% of the system is **orchestration, not computation** — scheduled jobs, CRM sync, rule evaluation, prompt assembly, Telegram transport. Only the income/forecast engine requires deterministic arithmetic (deliberately kept out of the LLM).

**Python (recommended, high confidence).** The LLM ecosystem gravity is decisive: OpenAI SDK, structured outputs, prompt tooling, and evaluation frameworks land in Python first. The coaching/personalization logic (traffic-light scoring, exponential smoothing of profile scales, MI-style dialogue orchestration) is exactly the kind of code a small team iterates fastest on in Python. Performance is irrelevant at stage-1 scale (hundreds, not millions, of masters: ≈ a few messages/second peak).
_Popular alternatives_: TypeScript/Node (strong option, see below), Go (excellent for schedulers/queues but LLM ecosystem maturity lags; slower iteration on prompt-heavy code), C#/Kotlin (viable, smaller LLM-tooling community in RU context)._
_Trade-off to accept_: Python's async task-queue story is weaker than Node's BullMQ; Celery is sync-first and its async support is a known pain point, with newer async-native libraries (Taskiq, FastStream, Repid) emerging as challengers — see [Aleksul's 2026 task-queue comparison](https://aleksul.space/posts/choosing-python-task-queue-library/) and [community discussion](https://www.reddit.com/r/Python/comments/1u775lo/choosing_a_python_task_queue_library_in_2026/)._
_Source: https://aleksul.space/posts/choosing-python-task-queue-library/_

**TypeScript/Node (credible runner-up, high confidence).** grammY has overtaken Telegraf as the best-maintained Telegram bot framework, and BullMQ is a more mature async job queue than anything in Python ([grammY framework comparison](https://grammy.dev/resources/comparison), [2026 bot framework overview](https://saqarmax.com)). If the team were TS-first, NestJS + grammY + BullMQ would be a fully defensible stack. The deciding factor is the LLM tooling edge of Python, not Telegram integration quality.
_Source: https://grammy.dev/resources/comparison_

### Development Frameworks and Libraries

**API/service layer + bot (recommended).**
- **FastAPI** (Python) for internal APIs and webhooks (Telegram webhook endpoint, future owner-facing endpoints). Fast, typed, Pydantic-native — Pydantic doubles as the schema layer for LLM structured outputs and for config validation. See [FastAPI vs NestJS vs Go 2026](https://acquaintsoft.com/blog/fastapi-vs-nodejs-vs-go-performance-benchmarks) and [NestJS vs FastAPI 2026](https://emporionsoft.com/nestjs-vs-fastapi-2026/) — benchmark deltas (NestJS/Fastify somewhat faster) are immaterial at this scale.
- **aiogram 3** (Python) for the Telegram bot: async-first, router/dispatcher architecture suited to long-running bots ([aiogram 3 architecture overview](https://saqarmax.com)). Pair with **FastAPI for webhooks + aiogram polling in a worker** (stage 1) or webhook mode behind the gateway (stage 1+).

**Background jobs (recommended).** Given the freshness thresholds (≤15 min for appointments), the job volume is small but timing-sensitive:
- **Taskiq or Celery + Redis broker** for Python. Taskiq is async-native and fits FastAPI; Celery is battle-tested with more operational lore but sync-first. For stage-1 simplicity, a **DB-backed scheduler + task queue hybrid** (see Integration Patterns step) may beat a heavy broker — flagged for Step 3 analysis.
- Alternative: Node **BullMQ** if TS stack chosen.

**LLM orchestration.** No heavy agent framework needed at stage 1 — the system is a **pipeline, not an autonomous agent**: deterministic engines compute numbers and scores; the LLM only *rephrases pre-computed facts* into psychotype-calibrated prose (per §11.2 requirements). A thin internal module (the "LLM port" — one interface, OpenAI adapter behind it) plus OpenAI SDK structured outputs suffices. This directly satisfies the "provider swappable without domain rework" constraint and keeps the depersonalization gateway as a single choke point.

### Database and Storage Technologies

- **PostgreSQL (managed) — primary store, high confidence.** All domain state: master profiles (type + scales + audit log of changes), client recommendation histories, appointments cache (synced from CRM), config versions, message log, traffic-light score history. One database keeps stage-1 operations simple; JSONB covers semi-structured profile/config payloads; row-level versioning tables cover the audit requirement (§6.5, §10.2.1). Managed PostgreSQL 16/17 available at all three RU providers compared ([ADG provider comparison](https://adg.ru/blog/2024-10-vk-cloud-selectel-otechestvennye-subd/), [Yandex Managed PostgreSQL](https://yandex.cloud/en/services/managed-postgresql)).
- **Redis — queue broker, rate-limiter, dedup, hot cache.** Frequency caps per master (≤5 initiative messages/shift), dedup keys for trigger suppression, Celery/Taskiq broker. Small footprint; can start on the same managed Redis offering or a tiny instance.
- **No NoSQL / warehouse at stage 1.** Recommendation-engine "probability of acceptance" stats fit Postgres tables; pgvector optional later for client-history similarity search — defer.
- **Object storage (S3-compatible)** only for logs/exports archival; Yandex Object Storage or Selectel S3.

### Development Tools and Platforms

- **Git + CI/CD under RU constraints.** GitHub remains practically usable from RU but carries account/billing risk; the resilient pattern is **self-hosted GitLab CE or Gitea + Actions on RU infrastructure**, with CI runners inside the same network that deploys to the RU cloud ([GitLab alternatives overview](https://www.bunnyshell.com/comparisons/gitlab-alternatives/), [Refine 2026 roundup](https://refine.dev/blog/github-alternatives/)). Pragmatic stage-1: GitHub private repo + self-hosted runner in RU cloud (deploy access stays in-country), with GitLab CE as the fallback if account risk materializes.
- **Testing.** pytest (+ pytest-asyncio) for engines: traffic-light hysteresis, smoothing-α updates, freshness degradation, motivation-scheme income math — these are pure functions and highly testable; snapshot/contract tests for the CRM adapter.
- **Observability.** Structured JSON logs, Sentry (self-hosted option if strict), Prometheus/Grafana or Yandex Cloud Monitoring; alerting on CRM sync staleness (the degradation-mode trigger is an SLO, not just a log line).

### Cloud Infrastructure and Deployment

**⚠️ Critical finding: OpenAI geo-blocks Russian IPs (high confidence).** OpenAI's supported-countries list excludes Russia and API calls from RU IPs are blocked by OpenAI itself ([official list](https://help.openai.com/ru-ru/articles/5347006-openai-api-supported-countries-and-territories), [VC.ru overview](https://vc.ru/provod/2962649-openai-api-v-rossii-2026-kak-rabotat-bez-vpn), [Habr technical analysis](https://habr.com/ru/articles/850620/)). Consequence for architecture: the depersonalization gateway (RU-side) must forward sanitized payloads through an **egress point outside RU** (own small VM abroad or a RU-billed intermediary like [ProxyAPI](https://proxyapi.ru/)). This composes with the legal design: PДn stays in RU; only depersonalized context crosses the border under art. 12 consent + Roskomnadzor notification. The LLM port abstraction should hide *both* the provider and the egress hop.

**Hosting comparison for this workload (RU residency mandated by ч.5 ст.18 152-ФЗ):**

| Criterion | Yandex Cloud | VK Cloud | Selectel |
|---|---|---|---|
| Managed PostgreSQL | Mature (16/17, autoscaling, backups) | Available (16/17) | Available (16/17) |
| 152-ФЗ posture | Strongest: dedicated [152-ФЗ compliance program](https://yandex.cloud/en/solutions/152-fz), FSTEC/FSB certifications documented ([conformity docs](https://yandex.cloud/en/docs/security/conform)) | 152-ФЗ compliant offerings | Compliant bare-metal/cloud, strong DB lineup |
| Ecosystem fit | Serverless, MQ, Object Storage, Lockbox (secrets), Cloud Logging — all in-region | Similar breadth | Leaner managed catalog |
| Notes | Best default for a PДn-heavy stage-1 system | Credible second source | Good for bare-metal egress/control planes |

Recommendation: **Yandex Cloud primary** (compliance documentation depth matters for the Roskomnadzor notification file), keep workloads portable (containers) so VK Cloud/Selectel remain exit options. ([Yandex data privacy](https://yandex.cloud/en/security/data-privacy), [ADG comparison](https://adg.ru/blog/2024-10-vk-cloud-selectel-otechestvennye-subd/), [2026 RU IaaS rankings](https://www.cloud4y.ru/en/blog/top-iaas-provider-2026/))

**Compute model (stage 1):** a small **Compute Cloud VM group running containers (docker compose)** — one app node (FastAPI webhook + bot worker) and one scheduler/worker node — beats Serverless Containers here: the scheduler and queue workers are long-lived, stateful-ish processes; serverless adds cold starts and execution limits for little cost benefit at this scale ([Yandex Serverless Containers](https://yandex.cloud/en/services/serverless-containers)). Managed Kubernetes is overkill for stage 1; container images keep the path open.

### Technology Adoption Trends

- **Async-native Python job queues** (Taskiq, FastStream, Repid) are where community energy is moving as Celery's async story stagnates — but Celery's operational maturity still wins for conservative teams ([source](https://aleksul.space/posts/choosing-python-task-queue-library/)).
- **Telegram bot frameworks:** grammY (TS) has the momentum; aiogram 3 is the Python standard; Telegraf is in maintenance decline ([comparison](https://grammy.dev/resources/comparison), [Telegraf discussion](https://github.com/telegraf/telegraf/discussions/386)).
- **RU hosting:** consolidation around Yandex Cloud/VK Cloud/Cloud.ru for regulated PДn workloads; self-hosted Git platforms rising as sanction-hedging ([rankings](https://www.cloud4y.ru/en/blog/top-iaas-provider-2026/)).
- **LLM access from RU is an active, shifting constraint** — intermediary proxy services with ruble billing (ProxyAPI et al.) are a recognized pattern; the provider-port design hedges against both regulatory and provider-side changes.

---

## Integration Patterns Analysis

*Researched 2026-08-17. Sources verified via live web search; confidence levels marked per claim.*

### CRM Integration Surface (Goal 1)

**⚠️ Critical finding: Zabot CRM has no public developer documentation (high confidence).** Searches of [zabot.org](http://zabot.org/) and its [personal cabinet](https://lk.zabot.org/) surface marketing features (client return, average-check growth, analytics) but no public API/webhook docs. Integration today is described through ready-made connectors — notably, **PROFZABOT is installable inside YClients** ("Интеграции > Уведомления" → app "PROFZABOT", per [YClients support docs](https://support.yclients.com/71-630-75-828--integraciya-i-profzabot/)) — and third-party automation hubs ([Albato](https://albato.ru/apps-crm), ApiX-Drive, ApiMonster) advertise Zabot webhook connectivity. _Source: http://zabot.org/, https://support.yclients.com/71-630-75-828--integraciya-i-profzabot/_

**Reference surface: the YClients API (documented, high confidence).** If Zabot runs on/alongside YClients, the well-documented [YClients REST API (Apiary)](https://yclientsen.docs.apiary.io/) and [developer portal](https://developers.yclients.com/ru/) become the realistic integration surface: bookings, clients, staff (masters), schedules — most operations available to third-party developers. Peer booking platforms show the webhook shape to expect: booking created/updated events pushed near-real-time ([Square bookings webhooks](https://developer.squareup.com/docs/bookings-api/use-webhooks), [MINDBODY webhooks](https://www.mindbodyonline.com/WebhooksDocumentation), [Cal.com webhooks](https://cal.com/docs/developing/guides/automation/webhooks)).
_Source: https://yclientsen.docs.apiary.io/_

**→ CRM-owner-dependent open items (must be answered by Zabot's owners before adapter code is written):**
1. Does the Mentor read data via **Zabot's own API** (exists? auth model? rate limits? sandbox?) or via the **host platform API** (YClients token per salon)?
2. Are **webhooks/push events** available for appointment create/update/cancel, or is polling the only option?
3. Are **historical client visit & payment records** exportable (needed to seed the income/forecast engine), or only forward-looking data?
4. Multi-salon/multi-master **entity identifiers** — stable across exports?

**Anti-corruption layer (ACL) design (recommended, high confidence).** Regardless of which surface answers land, isolate it behind an ACL per the [Strangler Fig / ACL guidance](https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig) (see also [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/strangler-fig.html)): a single `crm_adapter` module exposing the Mentor's **canonical model** (Master, Client, Appointment, Visit, Payment) in our own terms; the adapter translates CRM payloads (field names, status enums, timezone handling, money formats) at the boundary. Zabot's concepts (traffic-light scoring, recommendation semantics) must never leak into the coaching engines, and vice versa. This is cheap at stage 1 (one adapter, contract-tested) and makes surface #1–4 swappable later.
_Source: https://learn.microsoft.com/en-us/azure/architecture/patterns/strangler-fig_

**Sync model: watermark polling as the baseline (recommended).** Given no confirmed push channel, design for **scheduled incremental polling with a watermark/cursor** — the standard pattern for external-CRM-to-local-cache sync ([Airbyte incremental sync](https://docs.airbyte.com/platform/connector-development/connector-builder-ui/incremental-sync), [Ashby pagination & incremental sync](https://developers.ashbyhq.com/docs/pagination-and-incremental-sync), [watermark-based sync pipelines](https://inquir.org/use-cases/scheduled-data-sync)): store `last_synced_at` per entity type, walk cursor-paginated changes, upsert into the Postgres appointments/clients cache, handle deletes via periodic snapshot reconciliation. If webhooks are later confirmed, they become an **accelerator on top of polling** (event → immediate targeted re-fetch by ID), never the sole source of truth — webhooks can be dropped or reordered ([Svix webhook-vs-polling guidance](https://www.svix.com/resources/faq/webhooks-vs-long-polling/)). Freshness SLO (≤15 min for appointments) degrades gracefully: sync staleness is an observable metric with alerting, and engines already have degradation modes for stale data (per §research scope).
_Source: https://docs.airbyte.com/platform/connector-development/connector-builder-ui/incremental-sync_

### Telegram Transport (Goals 1–2)

**Webhook in production, polling as dev/fallback (high confidence).** Webhooks give lower latency, no idle request cost, and horizontal scaling behind a load balancer; long polling requires a single poller instance (one `getUpdates` consumer) but works behind any firewall with no TLS/domain setup ([Gramio webhook guide](https://gramio.dev/updates/webhook), [grammY deployment types](https://grammy.dev/guide/deployment-types), [production comparison](https://nbmit.ru/en/blog/dev/max-webhook-vs-long-polling-production), [Svix comparison](https://www.svix.com/resources/faq/webhooks-vs-long-polling/)). Stage-1 recommendation: **webhook mode on FastAPI** behind the gateway with Telegram's `secret_token` header validation, one bot instance; keep aiogram polling as the local-dev profile. Note the single-webhook-per-bot limit (ports 443/80/88/8443 only) — one bot token implies one webhook endpoint.
_Source: https://gramio.dev/updates/webhook_

**Update delivery is at-least-once** — Telegram may redeliver updates, so inbound handlers must be idempotent (dedup on `update_id`, aligning with the Redis dedup keys from Step 2).

### Communication Protocols and Data Formats

- **HTTPS/JSON everywhere at stage 1 (high confidence).** All integrations — Telegram Bot API, CRM adapter, LLM provider — are HTTPS+JSON. **gRPC/WebSockets: not needed.** No internal service mesh: this is a modular monolith plus workers on one network. Binary formats (Protobuf/MessagePack) buy nothing at hundreds-of-masters scale.
- **Pydantic as the single schema layer.** Inbound validation of CRM/webhook payloads, internal canonical model definitions, LLM structured-output schemas, and config validation all share Pydantic models — one definition of Master/Appointment/MessageConfig from transport to storage (JSONB columns typed via the same models).
- **CSV/flat exports** only as a one-off seeding path if Zabot answers open item #3 with "export file" rather than API.

### Scheduling and Messaging Engine Patterns (Goal 2)

**DB-backed scheduler + transactional outbox (recommended over a heavy broker at stage 1).** The messaging engine's correctness requirements — quiet hours in the salon's local timezone, pre-visit triggers (e.g., T-24h/T-2h before appointment), frequency caps (≤5 initiative messages/shift), dedup of triggers — are all **data problems, not throughput problems**. Recommended shape:

1. **Store all times in UTC in Postgres; render schedules in the salon's timezone** — the Airflow model: UTC-in-DB, timezone-aware local schedules, DST-safe ([Airflow timezone docs](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timezone.html), [timezone-aware cron pitfalls](https://medium.com/@sohail_saifi/time-zone-handling-in-scheduled-jobs-why-your-cron-jobs-run-at-the-wrong-time-8c935e7f8762), [K8s CronJob `timeZone` field](https://oneuptime.com/blog/post/2026-02-09-cronjob-timezone-scheduling/view)). Russia currently has no DST, but the pattern costs nothing and survives per-salon `Europe/*`→`Asia/*` diversity and future changes. Quiet hours are evaluated at *send-decision time* against the master's local clock, never baked into the job's fire time.
2. **A `scheduled_messages` table (durable schedule) + an `outbox` table (transactional sends)** rather than burying jobs in Redis only: if Redis flushes, scheduled intents survive; the outbox pattern removes dual-write between "decide to message" and "record message" ([transactional outbox context](https://news.ycombinator.com/item?id=44490510)).
3. **Dispatcher = periodic sweep (every 15–30 s) of due rows** (``WHERE due_at <= now() AND status='pending'`` with `FOR UPDATE SKIP LOCKED`), plus optional **Postgres LISTEN/NOTIFY as a latency accelerator** — notifications fire at commit ([PostgreSQL LISTEN docs](https://www.postgresql.org/docs/current/sql-listen.html)), but are fire-and-forget, so the polling sweep remains the source of truth ([DBOS: LISTEN/NOTIFY scales](https://www.dbos.dev/blog/postgres-listen-notify-scalability), [practitioner caveats](https://www.reddit.com/r/ExperiencedDevs/comments/1co3w3h/what_are_the_reasons_not_to_listennotify_in/)). This resolves the Step-2 flag: at this volume, **Postgres-first scheduling beats standing up Celery/Taskiq as the durability layer**; the task queue (if kept) handles only fan-out of already-durable intents.
4. **Degradation ladder as scheduled behavior — three freshness tiers, two degradation levels, explicit recovery (§5.2.1)**:
   - **Freshness classes are per-entity, not global**: checks/sales ≤ 60 min (visit praise, shift totals), schedule/appointments ≤ 15 min (pre-visit recommendations), dynamics/period totals ≤ 24 h (income forecast, GROW). The sync engine already stores watermarks per entity type; staleness is tracked and alerted per class — the SLO is three SLOs, not one.
   - **Level 1 — stale but usable** (older than tier threshold, younger than hard limit: checks 24 h, schedule end-of-current-day): data is used *with a visible timestamp label* («по данным на 14:30») rendered into the message; monetary forecasts are suppressed on labeled data.
   - **Level 2 — hard degradation** (older than hard limit, or CRM unavailable): communication continues *without figures* — support, coaching, profile/client-history recommendations; money calculations, visit-specific praise, and income forecasts are suspended; the master is honestly told why and the system returns to figures after recovery.
   - **Post-recovery reconciliation (the "coming back up" rule)**: on resync, period/shift totals are recomputed from actual data; missed *event* messages (praise for a specific visit) are **never sent retroactively** — they are folded into shift/period totals instead. The dispatcher enforces this via a per-message-class `suppress_backdated_events` flag evaluated against the trigger's source-data timestamp.
   - **Other rungs**: quiet-hours miss → defer to next allowed window; LLM port failure → deterministic template fallback (already pre-computed facts, per Step 2's "pipeline not agent" principle).
5. **Trigger arbitration in the dispatcher (§12)**. The business trigger set is: risk of missing the period target, strong growth opportunity, proximity to the next motivation tier (<10–15% sprint trigger), negative pattern, positive pattern, master silence beyond profile norm. When triggers compete, **the one with the highest expected value for the master's income wins; the rest are deferred (retried on a later sweep) or merged into one message**. Concretely: the outbox row carries a priority computed from (message class, expected-income value, trigger freshness), and the sweep sends the top-priority intent per master per decision window — arbitration is a dispatcher concern, not prompt-level logic.
6. **Frequency floors, not just caps (§7.3)**. Message classes carry an explicit **disable-priority ladder**: communication never stops entirely — period totals and pre-visit recommendations are the *last* classes disabled (the "денежный" class goes last), support/coaching content scales down first. Complemented by an **ignore-detection feedback loop**: per-master, per-class ignore rate ≥70% over 2 weeks → reduce frequency to the master's minimum + send one direct question about the preferred format (a scheduled job over the message-log tables, not an LLM judgment).

_Source: https://www.postgresql.org/docs/current/sql-listen.html_

### Integration Security Patterns

- **Telegram webhook**: `secret_token` per-bot constant in a header, TLS only, reject non-matching — plus IP allowlisting of Telegram's published ranges on the gateway ([Telegram webhook setup guidance](https://gramio.dev/updates/webhook)).
- **CRM credentials**: per-salon tokens (if YClients-style) or a single partner token (if Zabot-native) stored in **Yandex Lockbox** (Step 2), never in config files; rotation without redeploy.
- **Outbound LLM hop**: the depersonalization gateway remains the single egress choke point (Step 2); integration-wise it is an ACL in reverse — internal canonical context in, sanitized provider request out, provider identity and egress hop hidden behind the LLM port.
- **No OAuth needed at stage 1** — machine-to-machine API keys suffice; no end-user-facing auth flows beyond Telegram's own identity (chat_id is the user identity anchor).
- **Audit trail as an integration concern**: every CRM read (watermark, entity counts) and every outbound message (template id, config version used) is logged with the config-version reference — this is the join point for Goal 4 (auditable runtime config) and satisfies §6.5/§10.2.1 audit requirements from the scope.

### Cross-Cutting Findings Summary

| Integration | Pattern chosen | Confidence | Key trade-off accepted |
|---|---|---|---|
| Zabot CRM in | ACL + canonical model, watermark polling, Postgres cache | High (pattern) / **Low (surface facts — owner-dependent)** | Polling latency vs no confirmed push channel |
| Telegram | Webhook (prod) + polling (dev), idempotent handlers | High | Single webhook endpoint per bot |
| Scheduling | Postgres UTC schedules + outbox + SKIP LOCKED sweep, Redis only for rate-limit/dedup | High | Not horizontally scalable beyond ~10³ msg/s — irrelevant at stage 1 |
| LLM | LLM port + depersonalization gateway egress | High | Extra infra hop for cross-border sanitized calls |

---

## Architectural Patterns and Design

*Researched 2026-08-17. Sources verified via live web search; confidence levels marked per claim.*

### System Architecture Patterns

**Modular monolith — one deployable, enforced internal boundaries (recommended, high confidence).** For a 2–4 engineer team building a pipeline-style system (CRM sync → engines → scheduler → Telegram), the modular monolith is the 2026 consensus sweet spot: single codebase with module-level APIs and a single deployable unit — monolith dev speed without the operational tax of microservices ([ByteByteGo comparison](https://blog.bytebytego.com/p/monolith-vs-microservices-vs-modular), [2026 decision guide](https://www.javacodegeeks.com/2025/12/microservices-vs-monoliths-in-2026-when-each-architecture-wins.html), [DX analysis](https://getdx.com/blog/monolithic-vs-microservices/)). A 2024 DZone study cited there found teams spent **35% more time debugging microservices** than modular monoliths — a cost this project cannot absorb. Microservices pay off with 15+ engineers and independently scalable workloads; neither holds here. The boundaries are designed for later extraction: `crm_sync`, `engines` (scoring/forecast), `messaging` (scheduler/outbox), `llm`, `config` — separate Python packages, cross-module calls only through published interfaces, zero shared table access across modules.
_Source: https://blog.bytebytego.com/p/monolith-vs-microservices-vs-modular_

**Bounded contexts map 1:1 to modules** (DDD-lite, no event storming ceremony needed at this size): Master Profile, Coaching Engagement (dialogue state), Scheduling/Messaging, CRM Mirror (the synced cache), Configuration. The CRM Mirror is deliberately a *separate* context — it holds projections of external state, not authoritative domain objects.

### Design Principles and Best Practices

**Hexagonal architecture (ports and adapters) as the code-level rule (recommended, high confidence).** The Step-2/Step-3 decisions (LLM port, CRM ACL, Telegram transport) are exactly ports-and-adapters: the domain defines `Protocol` interfaces, infrastructure implements them, wiring happens at the edge via FastAPI dependency injection — the standard Python/FastAPI hexagonal layout ([ports & adapters in FastAPI](https://hemanthhari2000.medium.com/the-ports-and-adapters-pattern-unraveling-the-mystery-2efbf678ab9b), [reference repo](https://github.com/marcosvs98/hexagonal-architecture-with-python), [application-layer wiring](https://elpic.medium.com/hexagonal-architecture-in-python-wiring-adapters-dependency-injection-and-the-application-layer-1f2f83910deb), [Szymon Miks' example](https://blog.szymonmiks.pl/p/hexagonal-architecture-in-python/)). Concrete stage-1 ports: `LlmPort` (OpenAI adapter behind it, egress hop hidden), `CrmPort` (Zabot adapter), `TelegramPort` (aiogram adapter), `Clock` (injectable time — makes quiet-hours/DST logic unit-testable), `ConfigStore` (versioned config reads). **Domain layer stays framework-agnostic** — engines are pure functions over dataclasses, which is what makes the traffic-light hysteresis and income math cheaply testable (Step 2's pytest strategy).
_Source: https://blog.szymonmiks.pl/p/hexagonal-architecture-in-python/_

**Pipeline, not agent (restated as an architectural constraint).** Deterministic engines compute; the LLM only rephrases pre-computed facts into psychotype-calibrated prose. This bounds LLM failure blast radius: LLM outage degrades message *wording* to templates, never message *correctness*.

**ADRs.** Record the decisions in this document as Architecture Decision Records (context/decision/consequences) in-repo from day one — the CRM-surface uncertainty and OpenAI geo-block are exactly the kind of decisions future contributors will need rationales for.

### Scalability and Performance Patterns

**Explicitly not a stage-1 driver (high confidence).** Stage-1 load: hundreds of masters ≈ a few messages/second peak, sync jobs every few minutes. Design for **vertical scaling + horizontal dispatcher**: the `SKIP LOCKED` outbox sweep (Step 3) already allows N stateless workers if volume ever grows; Postgres and Redis scale up in place. Avoid premature distribution: no Kafka, no service mesh, no K8s ([monolith scaling guidance](https://getdx.com/blog/monolithic-vs-microservices/)). The one real performance requirement is **latency of the webhook path** (Telegram expects a fast ack) — handled by acknowledging immediately and pushing work to the outbox/queue, the standard webhook-decoupling pattern.

### Integration and Communication Patterns

Consolidated from Step 3 (details there): ACL + canonical model at the CRM boundary; watermark polling baseline; webhook-mode Telegram with idempotent handlers; transactional outbox + DB-backed scheduler as the messaging backbone; LLM behind a port with the depersonalization gateway as the single egress choke point. Architecturally these are all instances of two rules: **(a) nothing external is called from the domain layer; (b) every side effect with audit value goes through a durable record first** (outbox row, config-version reference, audit log entry).

### Security Architecture Patterns

**Zone model for 152-ФЗ (recommended, high confidence).** Two zones: **RU zone** (Yandex Cloud) holds all PDn — master profiles, client histories, appointments cache, message log; **egress zone** (small VM abroad or ruble-billed intermediary) receives only depersonalized context. This matches the current catalog of AI data-residency patterns: **edge redaction before the boundary is the cheapest residency control**, and a **gateway as Policy Enforcement Point** for AI inference is the recognized enterprise blueprint ([six residency patterns 2026](https://www.digitalapplied.com/blog/ai-data-residency-architecture-patterns-2026), [sovereign gateway PEP blueprint](https://medium.com/@himanshuaa/digital-sovereignty-architecture-for-ai-and-data-residency-a-practical-enterprise-blueprint-2e0750f0e5fc), [enforcement levels: code vs gateway vs infrastructure](https://blog.frankel.ch/data-residency/1/)). Key design choice: depersonalization happens **inside the RU zone** (the gateway sanitizes, then forwards) — enforcement at the gateway, not in every caller ([enforcement-level analysis](https://blog.frankel.ch/data-residency/1/)). Optional hardening later: pseudonymization tokens (client → opaque id) so even the egress logs are re-identifiable only inside RU — the "privacy vault per jurisdiction" idea at toy scale ([Databunker residency pattern](https://databunker.org/use-case/data-residency-compliance/), [Skyflow](https://www.skyflow.com/post/what-is-data-residency)).
_Source: https://www.digitalapplied.com/blog/ai-data-residency-architecture-patterns-2026_

**Secrets & access**: Yandex Lockbox for CRM tokens, bot token, provider keys; least-privilege service accounts; Telegram `secret_token` on the webhook; no PDn in logs (structured logging with a PII-scrubbing formatter in the RU zone too — logs are the usual leak path).

### Data Architecture Patterns

**Single PostgreSQL, module-owned schemas (high confidence).** One database, one schema per module (`crm_mirror`, `profile`, `messaging`, `config`, `audit`); JSONB for semi-structured payloads (profile scales, per-psychotype prompt fragments); plain tables + indexes for the hot paths (outbox sweep, due-message lookup).

**Versioned, auditable runtime config (Goal 4 — recommended pattern, high confidence).** Business parameters — quiet-hours windows per region; frequency caps **and floors** (message-class disable-priority ladder); trigger offsets T-24h/T-2h; motivation-scheme coefficients; per-entity freshness thresholds and hard limits (§5.2.1); traffic-light composite-score weights per signal stream, tone-confidence thresholds (≥0.7 for status change, ≥0.8 for burnout markers) and hysteresis entry/exit thresholds with 3/7-day minimum-stay (§10.2.1); per-scale smoothing α (§6.5) — live in an **insert-only, versioned config table**: immutable rows `(version, params JSONB, author, created_at, valid_from)`, with `valid_from`/`valid_to` validity intervals — the standard versioned key-value/history-table approach for settings ([audit-trail strategies](https://stackoverflow.com/questions/23770/effective-strategy-for-leaving-an-audit-trail-change-history-for-db-applications), [Redgate: version-number + insert-only design](https://www.red-gate.com/blog/database-design-for-audit-logging/), [audit-tables vs audit-columns](https://softwareengineering.stackexchange.com/questions/358586/what-is-the-proper-way-to-save-audit-information-in-a-database)). Two properties this buys, both required by §6.5/§10.2.1: (1) **reproducibility** — every outbound message row and every traffic-light score row stores the `config_version` used to compute it, so any historical decision can be re-derived; (2) **instant rollback** — activating a prior version is a new row, never an UPDATE. Pydantic models validate params on write; invalid configs are rejected at the editing boundary, and the engines read config *by version* at decision time (no mid-message config drift). Changes to config are themselves audit events (who/when/why), giving the owner-facing "why did the bot say that" answer for free.
_Source: https://www.red-gate.com/blog/database-design-for-audit-logging/_

**Audit log as a first-class table**, not just log files: append-only `audit` schema capturing config changes, consent events (art. 12 152-ФЗ), data-export/delete requests, and CRM sync runs — the compliance narrative Roskomnadzor expects is a query, not a log-scraping exercise.

### Deployment and Operations Architecture

**Containerized modular monolith on two small VMs (high confidence, from Step 2).** App node: FastAPI (webhook + internal API) + bot process; worker node: scheduler + outbox dispatcher + CRM sync jobs; docker compose per node, images in Yandex Container Registry. This stays a hair's breadth from Managed K8s if ever needed (images are portable) without paying its cost now. CI/CD: GitHub + self-hosted RU runner (GitLab CE fallback) per Step 2; deploys are rolling per node since the outbox makes messaging stateless-safe. **Observability as SLOs**: CRM-sync staleness, outbox oldest-pending age, LLM-port error rate, quiet-hours defer rate — each maps to a degradation mode, so alerting is on user-visible behavior, not CPU ([deployment-type guidance](https://grammy.dev/guide/deployment-types), [reliability practices](https://grammy.dev/advanced/reliability)).
_Source: https://grammy.dev/guide/deployment-types_

---

## Implementation Approaches and Technology Adoption

*Researched 2026-08-17. Sources verified via live web search; confidence levels marked per claim.*

### Technology Adoption Strategies

**Thin-slice walking skeleton first, CRM-dependent features second (recommended, high confidence).** The single biggest schedule risk is the unresolved Zabot API surface (Step 3 open items). De-risk by sequencing so that no CRM answers are on the critical path of week 1–4: build the **walking skeleton** (Telegram webhook ↔ config-versioned template messages ↔ outbox scheduler ↔ quiet hours) with a *fixture CRM* (recorded JSON payloads behind the `CrmPort` interface), then swap in the real adapter once the owners answer. This is expand-and-contract inside one module: the port's contract is written from the Mentor's canonical model, so the adapter — own API, host-platform API, or even CSV export — only changes the adapter's translation code. Two Telegram platform facts shape onboarding design: **a bot cannot message a user until the user has started the chat (`/start`)**, and per-chat rate limits apply (below) — so master onboarding (deep link `t.me/…?start=ref` + consent flow) is a first-class feature, not an afterthought ([proactive-messaging constraints](https://zendesk.oapps.io/hc/en-us/articles/…), [Telegram Bot API limits as commonly documented](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)).

### Development Workflows and Tooling

- **Trunk-based, small PRs, CI on self-hosted RU runner** (per Step 2). CI gates: lint (ruff), type check (mypy), unit tests, contract tests, image build.
- **Contract tests at the CRM seam**: the fixture payloads double as the adapter's acceptance suite — replay recorded CRM responses and assert canonical-model translations. When the real surface lands, record real payloads into the same suite (classic consumer-driven contract testing, just without a broker).
- **Config changes are code-like**: versioned config rows are edited via a reviewed process (small internal admin script at stage 1), with Pydantic validation rejecting invalid params at write time (Step 4).

### Recommendation Engine Design Sketch (§8 — the financial core)

The engine gets more than a table — its shape is fixed by business requirements even at reference-architecture level:

- **Candidate generation (deterministic)**: candidates = (owner's priority services/goods) ∪ (positions logically implied by client history: repeat-purchase cycles from purchase intervals, cross-sell/upsell to the booked service, cyclical "gaps" in service history). Signal sources: full visit history incl. comments, product repurchase cycles, service regularity gaps, seasonality, past refusals.
- **Exclusion filters (data + config rules)**: ≥2 consecutive refusals of a position → N-month pause; contraindications/allergies parsed from visit comments; owner's stop-list; incompatibility with the booked service. Refusal history is per-client profile state, not engine logic.
- **Ranking**: expected value = probability of acceptance (client history × master's per-type conversion statistics) × margin/priority weight. The acceptance-probability statistics live in Postgres tables (Step 2), updated by the feedback loop below.
- **Output cap**: **1–3 recommendations per visit, fewer is better** — the product goal is one confident offer, not a menu. Cap enforced in the engine, not left to the LLM.
- **Message format**: what / why / how — the "why" is the evidence from client history (deterministic fact), the "how" (ready-to-say phrase) is where the LLM's psychotype calibration applies. Depth of the "how" (full script vs. thesis) is driven by the master's sales-confidence scale.
- **Feedback loop (§8.4) — "never ask the master"**: recommendation outcomes are determined *automatically* from check contents synced from the CRM after the visit — recommended position in check → worked; not in check → didn't (deliberately not distinguishing "didn't offer" from "client declined"). Outcomes update the client profile (accepts/steadily refuses), the master profile (conversion by recommendation type), and engine quality stats. Systematic non-conversion becomes a coaching-cycle trigger (§9.5), surfaced as an MI-style conversation — never as compliance checking.
- **Architecturally**: this is a pure deterministic engine (unit-testable per Step 2's pytest strategy) consuming the CRM-mirror cache and producing pre-computed facts for the LLM port — consistent with "rephrases, never computes".

### Testing and Quality Assurance

**Three-layer test strategy (recommended, high confidence).**
1. **Pure-function unit tests (pytest)** — traffic-light hysteresis, smoothing-α updates, income math, quiet-hours/DST boundary tables via the injectable `Clock` (Step 4). Deterministic, fast, the bulk of the suite.
2. **LLM golden tests with deterministic assertions** — promptfoo is the current standard: YAML test cases with `contains`/`equals`/`regex`/JSON-schema assertions that run reliably in CI, plus model-graded evals for softer quality criteria ([promptfoo assertions docs](https://www.promptfoo.dev/docs/configuration/expected-outputs/), ["pytest for prompts" experience report](https://medium.com/israeli-tech-radar/testing-ai-you-cant-unit-test-my-journey-with-promptfoo-adaf9f523b67), [CI/CD guide](https://mager.co/blog/2026-02-23-promptfoo-llm-validation/)). For this system the natural golden set: *given pre-computed facts + psychotype, output must contain the facts, never invent numbers, respect tone constraints* — asserting the "rephrases, never computes" contract. Python-native alternative: assertllm for pytest-style semantics ([overview](https://www.reddit.com/r/Python/comments/1rph9e9/assertllm_pytest_for_llms_test_ai_outputs_like/)).
3. **End-to-end smoke against a test bot** — Telegram sandbox chat, fixture CRM, real outbox sweep; asserts the full loop including rate-limit pacing.

_Source: https://www.promptfoo.dev/docs/configuration/expected-outputs/_

### Deployment and Operations Practices

- **Rolling per-node deploys** (2 VMs, docker compose, Step 4); outbox statelessness makes restarts safe. Postgres: managed backups + PITR (Yandex Managed PostgreSQL default tooling — [pricing/ops](https://yandex.cloud/en/docs/managed-postgresql/pricing)); DR objective at stage 1: RPO ≤ 15 min (PITR), RTO ≤ 4 h (rebuild node from images + restore).
- **On-call lite**: alerting on the SLO set (per-entity CRM freshness — three tiers per §5.2.1; oldest pending outbox row; LLM-port error rate; quiet-hours defer spike); runbooks per degradation mode and per recovery path ([reliability guidance](https://grammy.dev/advanced/reliability)).
- **Rate-limit-aware sender**: the dispatcher must pace sends per Telegram's documented limits (~30 messages/s global; ~1 msg/s per chat, bursts ≤20/min to one chat) — a token-bucket per chat_id in Redis, which also enforces the product's own ≤5 initiative messages/shift cap. Batch pre-visit reminder waves accordingly (spread over minutes, not seconds).

### Team Organization and Skills

A 2–4 person team covers stage 1: 1–2 backend Python (FastAPI + async, the engines), 1 infra-hat (Yandex Cloud, compose, CI — not a dedicated DevOps), 1 product/methodology owner (MI-style coaching content, prompt library, config parameters). Prompt-engineering-as-discipline matters here: someone must own the psychotype prompt fragments and the golden-test set as versioned artifacts.

### Cost Optimization and Resource Management

**Infrastructure (order-of-magnitude, medium confidence — verify with the [calculator](https://yandex.cloud/en/prices)).** Yandex Cloud VMs start at ~$1.5–2.85/month (burstable) with usable dedicated configs from ~$20/month ([pricing](https://yandex.cloud/en/prices)); managed PostgreSQL is billed per hour (~$0.19/h/host in the documented example — [pricing policy](https://yandex.cloud/en/docs/managed-postgresql/pricing)), with third-party entry-level estimates around **$40/month** ([comparison](https://sourceforge.net/software/compare/Yandex-Managed-Service-for-MySQL-vs-Yandex-Managed-Service-for-PostgreSQL/)). Stage-1 infrastructure budget: **roughly $100–150/month** (2 small VMs + single-host managed PG + Redis + object storage) — infrastructure is noise next to LLM spend.
**LLM spend (medium confidence).** [ProxyAPI](https://proxyapi.ru/) resells OpenAI/Claude/Gemini access with ruble billing, small markup over official prices, VAT included ([tariffs](https://proxyapi.ru/pricing/list), [overview](https://proxyapi.ru/), [price comparison vs peers](https://vc.ru/provod/2962658-proxyapi-i-prompta-sravnenie-cen-i-uslug)). Because the architecture sends only *pre-computed facts* (short prompts, capped output), token spend is predictable: e.g., at ~2–4K tokens per coaching message all-in, hundreds of masters × a few messages/shift lands in the low hundreds of dollars/month. **Cost controls built in**: response length caps in the LLM port, template fallback when spend budget trips, per-master daily token meter.
_Source: https://proxyapi.ru/pricing/list_

### Risk Assessment and Mitigation

| # | Risk | Likelihood | Impact | Mitigation (already in architecture) |
|---|---|---|---|---|
| 1 | Zabot API surface unusable/absent | **High** (no public docs found) | Blocks CRM-dependent features | `CrmPort` + fixture CRM; CSV-import fallback adapter; escalate to owners with the 4 open items (Step 3) |
| 2 | OpenAI geo-block / intermediary shutdown | Medium | Messaging degrades | LLM port hides provider + egress hop; deterministic template fallback keeps the product alive ([Step 2 sources](https://habr.com/ru/articles/850620/)) |
| 3 | Telegram rate limits / spam reports | Medium | Reminder waves delayed; bot restricted | Per-chat token buckets; pacing in dispatcher; onboarding via `/start` consent ([limits](https://core.telegram.org/bots/faq#my-bot-is-hitting-limits-how-do-i-avoid-this)) |
| 4 | 152-ФЗ violation finding | Low–Medium | Legal | RU zone + PEP gateway + audit tables + consent records (Steps 2–4); Roskomnadzor notification before launch |
| 5 | Prompt drift (LLM invents numbers/tones) | Medium | Trust erosion | "Rephrases, never computes" contract enforced by golden tests (promptfoo) + structured outputs |
| 6 | Vendor lock-in (Yandex Cloud) | Low | Migration cost | Containers + plain Postgres; VK Cloud/Selectel exit options documented (Step 2) |
| 7 | Inter-salon data isolation & role-access model unresolved (§3 open question) | Medium | Schema redesign if retrofitted | Salon-scoped keys / row-level tenancy from day one — retrofitting multi-tenancy into a live schema is a rewrite; escalate model in owner letter |
| 8 | Consent model unresolved: unified vs separate, revocation mechanism, PDn operator/registry (§13.1 open questions) | Medium | Legal / launch blocker | Gate the Roskomnadzor notification on these answers; consent events already modeled as audit-table entries with revocation as a first-class event |

## Technical Research Recommendations

### Implementation Roadmap

1. **M0 — Walking skeleton (weeks 1–4):** repo + CI + RU infra; Telegram webhook, `/start` onboarding + consent record; config versioning (Goal 4) with first parameters; outbox + scheduler + quiet hours; template messages only; audit tables. *No CRM dependency.*
2. **M1 — CRM integration (weeks 5–8, gated on owner answers):** adapter against confirmed surface (or CSV fallback), watermark sync, CRM-mirror cache, staleness SLO + first degradation mode; fixture-driven contract tests replayed against real payloads.
3. **M2 — Coaching & recommendation engines (weeks 9–14):** traffic-light scoring (config-driven composite score, tone-confidence thresholds, hysteresis per §10.2.1), income/forecast math per the salon's motivation scheme, recommendation engine (candidate generation, exclusion filters, ranking, 1–3-per-visit cap, check-reconciliation feedback loop per §8), §12 trigger taxonomy with dispatcher arbitration, frequency caps **and floors** (message-class disable-priority ladder, ignore-detection loop per §7.3); prompt library + LLM port via egress gateway; promptfoo golden set in CI.
4. **M3 — Owner reporting, hardening & launch prep (weeks 15–18):** per-pay-period owner reports in Telegram (metrics vs goals, motivation-scheme position, recommendation conversion, aggregated state signals — **no chat quotes**, §14/§10.3) plus the red-status escalation path; degradation drills incl. post-recovery reconciliation; Roskomnadzor notification file; DR test (restore PITR); cost telemetry; pilot with 1–2 salons. (Owner-report data aggregation can start in M2 if slack allows — reporting is a stage-1 channel per §3.1, not a nice-to-have.)

### Technology Stack Recommendations (consolidated)

Python 3.12+ · FastAPI (webhooks/API) · aiogram 3 (bot) · PostgreSQL 16/17 managed (Yandex Cloud) — module schemas, versioned config, outbox, audit · Redis (dedup, per-chat pacing, hot cache) · docker compose on 2 VMs · GitHub + self-hosted RU runner (GitLab CE fallback) · pytest + promptfoo · ProxyAPI or own egress VM as LLM hop · Sentry + Grafana/Cloud Monitoring. Full rationale in Steps 2–4.

### Skill Development Requirements

Async Python discipline (the scheduler/outbox is all async I/O); contract-testing habit; prompt-versioning + eval mindset (promptfoo); enough 152-ФЗ literacy to own the consent/notification process without counsel for routine changes; light Yandex Cloud ops (networking, Lockbox, backups).

### Success Metrics and KPIs

- **Reliability SLOs:** per-entity CRM freshness (p95): checks/sales < 60 min, schedule/appointments < 15 min, dynamics < 24 h (§5.2.1); oldest pending outbox row < 60 s; LLM-port success > 99% (else template fallback engaged < 1% of sends).
- **Product:** opt-in → active-week-4 retention; master response rate to initiative messages; ≤5 initiative messages/shift cap never breached (hard invariant, tested); opt-out rate < 5%/month; **share of masters requesting frequency reduction (intrusiveness indicator, §16 — must stay low)**; **recommendation→check conversion, measured automatically from CRM (§16)**.
- **Compliance/ops:** every message reproducible from (facts, config_version, prompt_version) — 100% coverage; config rollback < 5 min; DR restore meets RPO/RTO in quarterly drill.
- **Cost:** LLM $/active master/month trending flat as prompts stabilize.

---

# Research Synthesis: Stage-1 Reference Architecture for the Zabot AI Mentor

*Synthesized 2026-08-18 from Steps 2–5 (live web research, 2026-08-16/17) plus the external gap-review revision. All load-bearing claims verified against current sources; confidence levels carried over from the body sections.*

## Executive Summary

This document establishes the stage-1 reference architecture for the Zabot AI Mentor: a Telegram-first coaching service for salon masters that turns Zabot CRM data into psychotype-calibrated coaching, recommendations, and owner reporting, under 152-ФЗ. The architecture that emerges is deliberately conservative in shape and aggressive in isolation: a **Python 3.12 modular monolith** (FastAPI + aiogram 3) on **two container VMs in Yandex Cloud**, with **PostgreSQL as the durability backbone** — versioned config, transactional outbox, per-entity freshness tracking, CRM mirror, audit tables — and Redis relegated to rate-limiting, pacing, and dedup. No Kubernetes, no message broker as source of truth, no microservices, no agent framework: the system is a **pipeline, not an agent** — deterministic engines compute every number, and the LLM only rephrases pre-computed facts into prose calibrated to the master's motivational profile.

Three constraints dominated every decision. **(1) Zabot CRM has no public API documentation** — the single biggest schedule risk, answered by a `CrmPort` anti-corruption layer over a canonical model, watermark polling as the sync baseline, and a fixture-CRM walking skeleton that keeps CRM answers off the critical path of weeks 1–4. **(2) OpenAI geo-blocks Russian IPs** — answered by a depersonalization gateway inside the RU zone that strips direct identifiers and forwards sanitized context through a foreign egress point (own VM or ruble-billed intermediary), keeping all PDn in-country per ч.5 ст.18 152-ФЗ, with consent (art. 12) and the Roskomnadzor notification as launch gates. **(3) Business-requirements fidelity is an architecture concern, not a detail** — the tiered freshness model (§5.2.1), trigger arbitration (§12), frequency floors (§7.3), the recommendation engine's "never ask the master" feedback loop (§8.4), and no-chat-quotes owner reporting (§14) all have first-class designs in the body sections above.

**Key Technical Findings:**

- **Anti-corruption layer + watermark polling** is the only defensible CRM integration pattern given the unconfirmed push channel; webhooks, if they appear, are accelerators — never the source of truth.
- **DB-backed scheduling beats a broker at this scale**: UTC-in-Postgres schedules, quiet hours evaluated at send-decision time against the master's local clock, `FOR UPDATE SKIP LOCKED` sweep, transactional outbox — with trigger arbitration and message-class disable-priority as dispatcher-level rules.
- **Degradation is a two-way ladder**: three per-entity freshness tiers with a labeled "stale-but-usable" level and a no-figures hard mode, plus post-recovery reconciliation that folds missed events into totals instead of backdating messages.
- **Insert-only versioned config** delivers §6.5/§10.2.1 auditability and instant rollback: every message and score stores its `config_version`; the owner's "why did the bot say that" becomes a query.
- **LLM cost is a model-selection problem**: intermediary markups are model-dependent (from modest to ~×4.3, e.g. ProxyAPI GPT-5.4 pricing) — but because only pre-computed facts cross the border, prompts are short and spend is predictable if model choice is priced explicitly.

**Technical Recommendations:**

1. Proceed with the consolidated stack (Section 8 below); defer Celery/Taskiq, Kubernetes, and pgvector.
2. Run M0 with zero CRM dependency; escalate the four CRM-owner open items and the two business open items (salon isolation, consent model) in parallel.
3. Treat the depersonalization gateway + LLM port as one compliance-and-resilience unit: single egress choke point, provider and hop both swappable, template fallback on failure.
4. Enforce "rephrases, never computes" with promptfoo golden tests in CI from M2 onward.
5. Design salon-scoped tenancy (row-level keys) into the schema from day one — retrofitting multi-tenancy is a rewrite.
6. File the Roskomnadzor notification before pilot; the audit tables are designed to make that file a query, not a project.

## Table of Contents

1. Technical Research Introduction and Methodology
2. Technical Landscape and Architecture Analysis *(incl. Frontend Strategy)*
3. Implementation Approaches and Best Practices
4. Technology Stack Evolution and Current Trends
5. Integration and Interoperability Patterns
6. Performance and Scalability Analysis
7. Security and Compliance Considerations
8. Strategic Technical Recommendations
9. Implementation Roadmap and Risk Assessment
10. Future Technical Outlook and Innovation Opportunities
11. Technical Research Methodology and Source Verification
12. Technical Appendices and Reference Materials

## 1. Technical Research Introduction and Methodology

### Significance

The Zabot AI Mentor sits at the intersection of three 2026 realities that make its architecture non-obvious: LLM-first product logic under a provider that geo-blocks the operating country; a hard data-residency statute (152-ФЗ) that zones infrastructure; and an integration target (Zabot CRM) whose developer surface is undocumented. Most AI-coaching reference architectures assume a US/EU cloud and a documented API — neither assumption holds here, and the value of this research is precisely the verified mapping of standard patterns (ACL, outbox, versioned config, PEP gateway) onto these constraints.

_Method: live web research with per-claim source verification, cross-checked against business requirements `docs/zabot_ai.md` v2.1 (incl. owner decisions of 13.08.2026), then revised after an external gap review._

### Methodology

- **Scope**: stack, integration, architecture, implementation, deployment — bounded by the four research goals (CRM integration, scheduling engine, RU-resident stack, versioned config).
- **Sources**: official provider documentation (Telegram, Yandex Cloud, PostgreSQL, OpenAI), framework documentation (FastAPI, aiogram, grammY), practitioner analyses (Habr, VC.ru, Redgate, ByteByteGo), and the business-requirements document as the normative source for engine behavior.
- **Verification**: every load-bearing claim carries a source; confidence levels marked in the body (high/medium/low); the two owner-dependent unknowns (CRM surface, business open items) are carried as explicit open items rather than assumed.
- **Revision loop**: an external review against the business requirements produced nine accepted corrections (freshness tiers, post-recovery, owner reporting, trigger taxonomy, recommendation engine, frequency floors, open-item cross-references, config inventory, KPIs) — all integrated into the body sections above.

## 2. Technical Landscape and Architecture Analysis

**Modular monolith with hexagonal boundaries** — one deployable, five modules (`crm_sync`, `engines`, `messaging`, `llm`, `config`), cross-module calls only through ports (`LlmPort`, `CrmPort`, `TelegramPort`, `Clock`, `ConfigStore`). DDD-lite bounded contexts map 1:1 to modules; the CRM Mirror is deliberately a separate context holding projections of external state. Details and sources: *Architectural Patterns* section above.

**Pipeline, not agent** — the load-bearing invariant. Deterministic engines (traffic-light scoring, income/forecast math, recommendation engine, trigger arbitration) compute; the LLM rephrases pre-computed facts. LLM outage degrades wording, never correctness. The §8.4 feedback loop (recommendation outcomes from check contents, never from asking the master) and the §12 arbitration rule (highest expected income value wins) are engine concerns precisely because they must be testable, not probabilistic.

### Frontend Strategy

**Stage 1: no separate frontend — the Telegram chat is the UI.** All master-facing interaction (onboarding via `t.me/…?start=ref`, consent, coaching dialogue, screening) runs through aiogram inline keyboards and messages; the owner/admin surface is a CLI script against the versioned config tables (Pydantic validation on write, audit event on every change). Zero web frontend, zero mobile app.

**Growth path: Telegram Mini App, not a website.** When chat buttons run out of room (consent forms, progress dashboards, owner analytics), the answer is a Mini App — a web page rendered inside Telegram and attached to the bot, developed in React or any JS framework, served over HTTPS, authenticated via `WebApp.initData` validated server-side against the bot token ([Mini Apps docs](https://core.telegram.org/bots/webapps), [2026 comparison](https://freeblock.medium.com/telegram-mini-apps-vs-native-apps-vs-web-apps-2026-whats-best-for-your-product-1e72c12ebb1b)). Critically for this project: it must be **hosted in the RU zone** (static assets via Yandex Object Storage or FastAPI, behind the gateway) — 152-ФЗ forbids parking PDn-touching UI on US/EU CDNs. It is one extra page in the existing deployment, not a new application; `chat_id` remains the single identity anchor.

**Explicitly out of scope at stage 1:** marketing website, native iOS/Android apps, custom web portal.

## 3. Implementation Approaches and Best Practices

Thin-slice walking skeleton first (M0), CRM-dependent features second: the `CrmPort` contract is written from the Mentor's canonical model, and a fixture CRM (recorded JSON payloads) doubles as the contract-test suite until the real surface lands. Three-layer test strategy: pure-function pytest for engines (hysteresis, α-updates, income math, quiet-hours/DST via injectable `Clock`); promptfoo golden tests asserting the "contains the facts, never invents numbers" contract; end-to-end smoke against a test bot with rate-limit pacing. Deployment: rolling per node, outbox makes restarts safe. Full detail: *Implementation Approaches* section above, including the recommendation-engine design sketch and the §5.2.1/§7.3/§12 engine rules.

## 4. Technology Stack Evolution and Current Trends

Python's LLM-ecosystem gravity decided the language; async-native queue libraries (Taskiq, FastStream) are where community energy is moving but were deliberately *not* adopted as the durability layer — Postgres-first scheduling wins at this volume. grammY (TS) has Telegram-framework momentum, aiogram 3 is the Python standard. RU hosting consolidates around Yandex/VK/Selectel for regulated workloads. **LLM access from RU remains the most volatile layer**: the geo-block persists (verified 2026-08-18), the intermediary market is active and price-divergent — markups range from modest to ~×4.3 depending on model and service (ProxyAPI vs AITunnel vs Polza, per [VC.ru pricing comparison](https://vc.ru/provod/2962649-openai-api-v-rossii-kak-rabotat-bez-vpn)) — so the LLM port must treat the intermediary's price list as a selection criterion alongside quality, and model choice is a first-order cost lever, not a procurement detail.

## 5. Integration and Interoperability Patterns

HTTPS/JSON everywhere, Pydantic as the single schema layer from transport to storage. CRM in: ACL + canonical model, watermark polling baseline, per-entity freshness tracking. Telegram: webhook in production (secret_token, IP allowlisting) with polling for dev, idempotent handlers on `update_id`. Scheduling: UTC-in-DB + timezone-aware rendering, outbox + `SKIP LOCKED` sweep + optional LISTEN/NOTIFY accelerator, trigger arbitration, message-class floors. LLM out: single egress choke point behind a port. Cross-cutting summary table in the *Integration Patterns* section above.

## 6. Performance and Scalability Analysis

Explicitly not a stage-1 driver: hundreds of masters ≈ a few messages/second. The webhook path must ack fast (decouple via outbox); the dispatcher scales horizontally if ever needed (`SKIP LOCKED`); Postgres and Redis scale in place. The real "performance" surface is **timeliness under degradation** — per-entity freshness SLOs, oldest-pending-outbox age, defer rates — which is why alerting targets user-visible behavior, not CPU.

## 7. Security and Compliance Considerations

Two-zone model: RU zone (Yandex Cloud) holds all PDn; the egress zone receives only depersonalized context. Depersonalization happens *inside* the RU zone — gateway as Policy Enforcement Point, not per-caller responsibility. Secrets in Yandex Lockbox; PII-scrubbed structured logging (logs are the usual leak path); audit tables as first-class compliance surface (config changes, consent events, export/delete requests, sync runs). Open legal items carried as risks #7–8: salon isolation/role-access model and the consent triad (unified vs separate, revocation, operator/registry) — both gate launch artifacts, the first also gates schema design.

## 8. Strategic Technical Recommendations

**Consolidated stack:** Python 3.12+ · FastAPI (webhooks/API) · aiogram 3 (bot, chat-only UI at stage 1) · PostgreSQL 16/17 managed (Yandex Cloud) with module schemas, versioned insert-only config, outbox, per-entity freshness, audit · Redis (dedup, per-chat pacing, hot cache) · docker compose on 2 VMs · GitHub private repo + self-hosted RU runner (GitLab CE fallback; migration is a `git push --mirror` away) · pytest + promptfoo · ProxyAPI or own egress VM as LLM hop with explicit model pricing · Sentry + Grafana/Cloud Monitoring · **no frontend** (Telegram Mini App as the named growth path).

**Decision framework:** accept boring infrastructure, spend novelty budget on the coaching engines and the compliance choke points. Every external dependency sits behind a port; every side effect with audit value goes through a durable record first.

## 9. Implementation Roadmap and Risk Assessment

M0 walking skeleton (wks 1–4, no CRM dependency) → M1 CRM integration (wks 5–8, gated on owner answers) → M2 coaching & recommendation engines with trigger arbitration and floors (wks 9–14) → M3 owner reporting, hardening, Roskomnadzor file, pilot (wks 15–18). Full milestones and the 8-row risk register (top risk: Zabot API surface absent, likelihood High, mitigated by port + fixture + CSV fallback) in the *Technical Research Recommendations* section above.

## 10. Future Technical Outlook and Innovation Opportunities

Near-term: pgvector for client-history similarity in the recommendation engine; pseudonymization tokens so even egress logs are re-identifiable only inside RU. Medium-term: second-source hosting rehearsal (VK Cloud/Selectel); engine extraction to services only if team and load justify; Telegram Mini App when the UI budget opens. Long-term: multi-provider LLM routing on price/quality per message class; agentic capabilities only inside the coaching-dialogue seam, never in the numeric engines.

## 11. Technical Research Methodology and Source Verification

Primary sources: official documentation (Telegram Bot API/Mini Apps, Yandex Cloud, PostgreSQL, OpenAI country list) and the normative business-requirements document. Secondary: practitioner analyses and comparisons cited inline throughout Steps 2–5. Confidence levels marked per claim in the body; the two owner-dependent unknowns are stated as open items rather than resolved by assumption. Limitations: Zabot CRM integration facts are pattern-level (high confidence) but surface-level facts are owner-dependent (low confidence until answered); RU-infrastructure pricing is order-of-magnitude.

## 12. Technical Appendices and Reference Materials

- **Reference architecture at a glance:** 2 VMs (app: FastAPI webhook + bot; worker: scheduler + outbox dispatcher + CRM sync) · managed PostgreSQL (schemas: `crm_mirror`, `profile`, `messaging`, `config`, `audit`) · Redis · egress VM/intermediary · GitHub + self-hosted runner.
- **Key tables:** `scheduled_messages`, `outbox`, versioned `config` (insert-only), `audit` (append-only), CRM-mirror projections, message log with `config_version`/`prompt_version`, per-master per-class ignore-rate stats.
- **Open items register:** CRM-owner items 1–4 (API vs host-platform, webhooks, historical exports, stable IDs — *Integration Patterns* section); business items (salon isolation, role access, consent model, revocation, operator/registry — risk rows 7–8); escalation vehicle: the letter to the owner (`letter-to-owner-clarifying-questions-ru.md`).

---

## Technical Research Conclusion

The stage-1 reference architecture is a compliance-aware pipeline: deterministic engines over a CRM mirror, a DB-backed scheduling backbone with two-way degradation, an insert-only config system that makes every message reproducible, and a single depersonalized egress for LLM rephrasing. The decisive risks are external (CRM surface, provider access, consent model) and each is hedged by an architectural seam rather than a hope. Next step: send the owner letter with the CRM and business open items, and start M0 — nothing in weeks 1–4 waits on any answer.

---

**Technical Research Completion Date:** 2026-08-18
**Research Period:** 2026-08-16 – 2026-08-18 (live web research, verified sources)
**Source Verification:** all load-bearing claims cited; confidence levels marked
**Technical Confidence Level:** High on patterns and stack; Low on CRM surface facts (owner-dependent, carried as open items)
