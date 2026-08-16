---
stepsCompleted: [1, 2, 3, 4, 5, 6]
inputDocuments:
  - "_bmad-output/planning-artifacts/letter-to-owner-clarifying-questions-ru.md"
  - "docs/zabot_ai.md"
workflowType: 'research'
lastStep: 6
status: 'complete'
research_type: 'technical'
research_topic: '152-FZ PDn compliance, LLM provider selection, and RU-localized hosting/tech stack for Zabot AI'
research_goals: 'Unblock the tech-stack decision (Block 1, Q4 of the clarifying letter): determine a 152-FZ-compliant LLM provider, RU localization/hosting posture, profiling/mood-data consent model, and architectural rules so development can start.'
user_name: 'Timurkarev'
date: '2026-08-11'
web_research_enabled: true
source_verification: true
---

# Research Report: technical

**Date:** 2026-08-11
**Author:** Timurkarev
**Research Type:** technical

---

## Research Overview

This research unblocks the technology-stack decision for Zabot AI (the "ИИ-помощник мастера Zabot" product), specifically the clarifying-letter question block on 152-FZ localization, LLM provider choice, and the consent model for psychological profiling and mood data. It produces a grounded recommendation that lets development begin on a compliant footing.

---

## Technical Research Scope Confirmation

**Research Topic:** 152-FZ PDn compliance, LLM provider selection, and RU-localized hosting/tech stack for Zabot AI
**Research Goals:** Unblock the tech-stack decision (Block 1, Q4 of the clarifying letter): determine a 152-FZ-compliant LLM provider, RU localization/hosting posture, profiling/mood-data consent model, and architectural rules so development can start.

**Technical Research Scope:**

- Architecture Analysis — PDn residency boundaries, deterministic-vs-LLM boundary, ports/adapters (CRM mappers deferred)
- Implementation Approaches — consent capture & withdrawal, Art. 16 profiling safeguards, LLM depersonalization patterns
- Technology Stack — RU-hosted infra + Russian LLM providers vs. foreign-via-proxy
- Integration Patterns — LLM API contracts, CRM data port abstraction, audit/consent logging
- Performance Considerations — RU LLM API latency/SLA, deterministic-compute caching, timezone/quiet-hours

**Research Methodology:**

- Current web data with rigorous source verification (law texts, provider docs, 2025–2026 amendments)
- Multi-source validation for every legal claim
- Confidence-level framework (engineering-grounded; legal conclusions flagged for counsel)
- Comprehensive technical coverage with architecture-specific insights

**Scope Confirmed:** 2026-08-11

---

## Technology Stack Analysis

> The topic is compliance-driven, so the conventional "languages/frameworks" categories are mapped to the stack surfaces that actually carry the decision: the LLM provider layer, the orchestration layer, the PDn storage layer, and the RU cloud/hosting layer.

### LLM Provider Layer (core decision)

This is the heart of the tech-stack choice. Three viable postures, evaluated against the localization rule (ч. 5 ст. 18, in force since 01.07.2025 — direct ban on primary collection/storage of RF citizens' PDn via foreign databases/infrastructure).

**Option A — GigaChat (Sber), B2B API ✅ recommended primary candidate**
- Access: legal entity / ИП, contract-based via the Sber developer portal.
- Billing: prepaid token packages **or** pay-as-you-go. In Feb 2026 Sber cut business pricing roughly **3×**, covering both package and pay-as-you-go plans.
- SDK: **GigaChain** — Sber's framework for building LLM apps/agents on GigaChat.
- Fit: strong at structuring/analysis; mature corporate API; processed in Russia → satisfies localization.
- _Sources:_ [Sber — legal tariffs](https://developers.sber.ru/docs/ru/gigachat/tariffs/legal-tariffs) · [Habr — 3× price cut (Feb 2026)](https://habr.com/ru/companies/sberbank/news/991878/) · [GigaChat API for business](https://developers.sber.ru/portal/products/gigachat-api)

**Option B — YandexGPT (Yandex Foundation Models) ✅ recommended primary candidate**
- Access: via Yandex Cloud / Yandex AI Studio.
- Models & indicative pricing: YandexGPT Lite ≈ **0.20 ₽/1k tokens**, YandexGPT Pro 5.1 ≈ **0.80 ₽/1k tokens**, Alice AI LLM Flash cheaper (sync mode ≈ 0.5 ₸). Billed on total tokens (prompt + response).
- Grant: **Yandex Cloud Boost AI** — up to **1,000,000 ₽** for tech companies; ideal to fund the pilot.
- Fit: strong generation/tone; native RU hosting inside Yandex Cloud (4 availability zones) with IAM, logging, KMS, security services; processed in Russia → satisfies localization.
- _Sources:_ [YandexGPT API pricing walkthrough (2026)](https://vc.ru/provod/3035416-yandexgpt-api-pervyj-zapros-i-raschet-stoimosti) · [Yandex AI Studio pricing](https://aistudio.yandex.ru/docs/ru/ai-studio/pricing) · [Boost AI grant](https://yandex.cloud/ru/blog/posts/2023/12/yandexgpt-api-and-yandex-cloud-boost-ai)

**Option C — Foreign models via RU-hosted channels ✅ compliant (three pathways)**

> **Key finding:** the original analysis was overly conservative. US and Chinese models **can** be used compliantly through three distinct legal pathways.

**Pathway C1 — RU-cloud-hosted foreign open-weight models (strongest option)**
- Yandex Cloud AI Studio now hosts **24 models natively on RU infrastructure**, including **Qwen 3 235B** (Alibaba/China), **DeepSeek** (China), and **Gemma** (Google/US).
- Data never leaves Russia — the model runs locally within the RU cloud, not via an API call to a foreign endpoint.
- Same contract, billing, and compliance posture as YandexGPT. Single vendor, zero legal ambiguity.
- _Sources:_ [Yandex Cloud — Qwen 3 235B available (Apr 2026)](https://yandex.cloud/ru-kz/blog/qwen3-235b) · [Yandex AI Studio quickstart](https://aistudio.yandex.ru/docs/en/ai-studio/quickstart/)

**Pathway C2 — Self-hosted open-weight models on RU bare-metal/GPU**
- DeepSeek, Qwen, Llama, Mistral all have open-weight versions deployable on RU-hosted GPUs (Yandex Cloud GPU instances, Cloud.ru, Selectel, or bare-metal in a Russian DC).
- Data stays entirely in your hands on RU soil. Zero legal ambiguity.
- Trade-off: higher ops cost (GPU provisioning, model serving, scaling).
- _Sources:_ [Self-hosting DeepSeek guide](https://workos.com/blog/how-to-run-deepseek-r1-locally) · [DeepSeek on Northflank](https://northflank.com/blog/deploy-self-host-deep-seek-v3-1-on-northflank)

**Pathway C3 — Transborder transfer with consent + Roskomnadzor notification (limited use)**
- ст. 12 permits transborder transfer if: (1) the subject gives **explicit consent**, and (2) the operator **notifies Roskomnadzor** before starting.
- Crucially, the July 2025 amendment to ч. 5 ст. 18 bans *primary collection via foreign infrastructure* but **does not ban transborder transfer of data already collected in RU**. All PDn is first collected and stored on RU soil; only then does a depersonalized payload cross the border.
- **Caveat:** pseudonymization ≠ anonymization under 152-FZ. If the recipient could re-identify the person, it's still PDn. True anonymization strips the personalization that makes coaching effective — so this pathway is best suited for **aggregated analytics, model evaluation, and non-PDn tasks** (code gen, internal tools), not the live coaching narrative.
- _Sources:_ [Comply.ru — localization vs transborder transfer](https://comply.ru/tpost/c43ezsout1-lokalizatsiya-i-transgranichnaya-peredac) · [IC-TECH — transborder transfer compliance](https://ic-tech.ru/blog/knowledge-base/transgranichnaya-peredacha-personalnyh-dannyh-kak-soblyudat-152-fz/)

**Revised decision heuristic — multi-tier LLM strategy:**

| Tier | Models | Use Case | Data Residency | Risk |
|---|---|---|---|---|
| **Tier 1 (Primary)** | GigaChat, YandexGPT | Empathetic coaching narrative — the "voice" of Zabot | 100% RF | Zero |
| **Tier 2 (Augmentation)** | Qwen 3, DeepSeek, Gemma via Yandex Cloud AI Studio | Structuring, analysis, reasoning-heavy tasks | 100% RF (RU-hosted) | Zero |
| **Tier 3 (Optional)** | OpenAI, Anthropic, Google via direct API | Anonymized analytics, non-PDn tasks | Transborder (requires consent) | Low, gated |

Recommended action: pilot Tiers 1 and 2 on depersonalized data (~2 weeks), funded by the Yandex Cloud Boost AI grant (1M ₽). Tier 3 activated only if Tier 1+2 quality is insufficient for specific tasks, gated behind separate user consent and Roskomnadzor notification.

_Provider landscape (2026):_ the market has consolidated around **GigaChat** and **YandexGPT** as the two enterprise-grade RU LLMs, both with active price competition and grant programs. _Confidence: high._

### Orchestration & Implementation Layer

- **GigaChain (Sber)** — purpose-built SDK for GigaChat apps/agents; lowest-friction if GigaChat is chosen.
- **LangChain / LlamaIndex** — generic orchestration; usable with RU providers via custom LLM-client wrappers. **Caveat:** must guarantee no telemetry/data egress; some libs default to foreign endpoints — pin to RU endpoints.
- **Implementation language for the AI/backend layer:** **Python** (dominant for LLM orchestration, best provider SDK support) or **Node/TypeScript**. The consumer app is **Flutter (mobile)**, so the LLM + persistence + profiling engine sits behind a backend service the app calls.
- _Confidence: high._

### Database & PDn Storage Layer

All datastores **must be RU-hosted** (same localization rule).

- **Relational — PostgreSQL** (managed in Yandex Cloud / Cloud.ru): masters, salons, visits, motivation schemes, **consent records**, **audit log**.
- **Events / time-series:** mood screenings (WHO-5), behavioral signals, traffic-light state transitions — needed because Art. 16 requires being able to show *how* an automated decision was reached.
- **Vector store (RAG over coaching content / glossary):** `pgvector` on the same Postgres, or a RU-hosted vector DB.
- **Consent & audit log:** append-only / immutable. Art. 16 puts the burden of *proving consent* on the operator; Art. 19 requires security measures — an immutable consent-and-decision audit log covers both.
- _Confidence: high (architecture); medium (exact retention rules — confirm with counsel)._

### Cloud Infrastructure & Hosting (152-FZ posture)

- **RU providers with 152-FZ / FSTEC posture:** Yandex Cloud, Cloud.ru (Sber), VK Cloud, Selectel, Timeweb Cloud, MTS Web Services — all guarantee in-country storage and publish their 152-FZ/FSTEC certifications.
- **Recommendation:** **Yandex Cloud or Cloud.ru** — both provide IAM, KMS (key management), logging, and explicit PDn-protection service sets that map onto Art. 19 obligations. Yandex Cloud additionally co-locates the YandexGPT endpoint (lower latency, single trust boundary).
- **Compute:** Managed Kubernetes (available in both) for the backend service; containerized deployment.
- _Sources:_ [CloudIndex — RU cloud comparison incl. 152-FZ/FSTEC certs](https://cloudindex.ru/providers/) · [Yandex Cloud — PDn protection services](https://yandex.cloud/ru/blog/posts/2024/11/personal-data-protection) · [VK Cloud — cloud solutions 2025–2026](https://cloud.vk.com/blog/luchshie-oblachnie-resheniya-dlya-biznesa-v-2025-2026/)
- _Confidence: high._

### Depersonalization Patterns for the LLM Call Path

- Strip direct identifiers from prompts before they reach any LLM; send only what the coaching narrative needs (a depersonalization gateway in front of the LLM client).
- Know the legal distinction: **anonymization** (data ceases to be PDn) vs **pseudonymization** (still PDn, just tokenized) — only the former unlocks foreign processing, and it's rarely compatible with live personalization.
- Минцифры has updated depersonalization requirements (notably for ML model development without exposing PDn) — relevant if models are ever fine-tuned.
- _Sources:_ [Depersonalization under new Минцифры requirements](https://vc.ru/legal/960919-depersonalizaciya-po-novym-trebovaniyam-mincifry-est-reshenie) · [Decosystems — обезличивание ПДн](https://www.decosystems.ru/obezlichivanie-personalnykh-dannykh/)
- _Confidence: medium-high._

### Technology Adoption Trends

- **Price competition & grants:** Sber cut GigaChat business prices ~3× (Feb 2026); Yandex offers a 1M ₽ grant — RU LLMs are now cost-competitive for production.
- **Consolidation:** enterprise RU LLM space narrowing to GigaChat + YandexGPT.
- **Tightening law:** the 01.07.2025 localization amendment removes ambiguity — foreign-primary processing is now expressly banned, making the RU-infra choice effectively mandatory rather than preferential.
- _Confidence: high._

### Quality Assessment

- **High confidence:** provider capabilities, pricing, SDK availability, RU cloud 152-FZ posture (all from current 2026 sources).
- **Medium confidence (flag for data-protection counsel):** the classification of mood/WHO-5 data as Art. 10 *special category*, the exact Roskomnadzor register obligations under Art. 22, and whether the traffic-light's effect on KPI crosses the Art. 16 "legally or similarly significant consequences" threshold. The engineering posture (written consent + audit log + RU hosting) is sound under any of these interpretations, but the final legal sign-off must come from a Russian ПДн lawyer.

---

## Integration Patterns Analysis

> Integration patterns are mapped to the Zabot AI domain specifically — not a generic catalog. Each pattern addresses a real interface in the system.

### Hexagonal (Ports & Adapters) Architecture — the structural backbone

Zabot AI's domain (coaching engine, profiling, traffic-light, motivation-scheme calculator) is **entirely decoupled** from infrastructure via ports and adapters. This is critical for three reasons:

1. **CRM adapter is deferred** — the domain defines what it needs (`CrmPort`); the real CRM adapter is plugged in later. A `FakeCrmAdapter` with test data enables full development now.
2. **LLM adapter is multi-provider** — the domain calls a single `LlmPort`; adapters for GigaChat, YandexGPT, Qwen, DeepSeek, and (optionally) OpenAI are interchangeable. The routing tier logic lives in the adapter layer, not the domain.
3. **Channel adapter is pluggable** — Telegram today, potentially a web widget or mobile native channel later.

```
┌──────────────────────────────────────────────────────────┐
│                    Channels (Adapters)                    │
│  Telegram Bot API  ·  Future: Web Widget / Flutter InApp│
└────────────┬─────────────────────────────────────────────┘
             │
┌────────────▼─────────────────────────────────────────────┐
│              Application Layer (Use Cases)                │
│  CoachingSession · ProfilingEngine · TrafficLight        │
│  MotivationCalculator · ConsentManager · Scheduler        │
└────┬─────────┬──────────┬──────────┬────────────────────┘
     │         │          │          │
┌────▼───┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼──────────────┐
│ Ports  │ │ Ports  │ │ Ports  │ │ Ports            │
│ LlmPort│ │CrmPort │ │PdnPort │ │NotifPort         │
└────┬───┘ └──┬─────┘ └──┬─────┘ └──┬──────────────┘
     │        │          │          │
┌────▼───┐ ┌──▼─────┐ ┌──▼─────┐ ┌──▼──────────────┐
│Adapters│ │Adapters│ │Adapters│ │Adapters           │
│GigaChat│ │FakeCRM │ │Pg+Audit│ │Telegram API       │
│YaGPT   │ │RealCRM │ │Consent │ │QuietHours Guard  │
│Qwen3   │ │(later) │ │Log     │ │Inline Keyboard   │
│DeepSeek│ │        │ │        │ │                   │
│OpenAI* │ │        │ │        │ │                   │
└────────┘ └────────┘ └────────┘ └──────────────────┘
  (* Tier 3 only, with consent)
```

This pattern is specifically recommended for AI integrations because it isolates the LLM from business logic — the domain decides *what* to ask the LLM, the adapter handles *how* (which provider, which API format, depersonalization).
_Source:_ [Ableneo — Hexagonal Architecture for AI Integration](https://www.ableneo.com/insight/hexagonal-architecture-for-ai-integration/) · [LinkedIn — Ports & Adapters for AI](https://www.linkedin.com/pulse/ports-adapters-ai-why-hexagonal-architecture-still-wins-varun-singh-l9owe) · [Medium — Ports & Adapters on example](https://wkrzywiec.medium.com/ports-adapters-architecture-on-example-19cab9e93be7)

### LLM API Integration — Unified Multi-Provider Client

**Critical finding:** there is already an open-source **Multi-LLM Orchestrator** library (Python) that provides a unified interface across GigaChat, YandexGPT, and local models (Ollama), with smart routing and automatic fallback.

**Provider API formats:**

| Provider | Auth | API Format | SDK |
|---|---|---|---|
| **GigaChat** | OAuth2 (client_credentials) | Proprietary REST | `gigachat` Python SDK (part of GigaChain); `langchain-gigachat` |
| **YandexGPT** | IAM token / API key | OpenAI-compatible (Yandex AI Studio) | `yandexgpt-python` SDK; also works via standard `openai` Python lib with custom base URL |
| **Qwen 3 / DeepSeek / Gemma** (via Yandex Cloud) | Yandex IAM | OpenAI-compatible (Yandex AI Studio) | Same `openai` lib with Yandex base URL |
| **OpenAI / Anthropic** | API key | OpenAI / Anthropic format | Standard `openai` / `anthropic` SDKs |

**Key insight:** Yandex AI Studio exposes foreign models (Qwen, DeepSeek, Gemma) through an **OpenAI-compatible API** — meaning the same `openai` Python client works for YandexGPT, Qwen, and DeepSeek by just changing the `base_url`. This dramatically simplifies the adapter layer.

**The universal client (Multi-LLM Orchestrator, v0.5.0)** handles:
- Provider-specific OAuth2/IAM auth
- Streaming support
- Smart routing (send to cheapest/fastest provider based on task)
- Automatic fallback if a provider is down
- Supports GigaChat, YandexGPT, and Ollama (local models)

**Recommended architecture:**
```
Domain ──→ LlmPort (unified interface)
              │
              ▼
         LlmRouter (tier logic, cost, latency)
          ├── Tier 1: GigaChat adapter (OAuth2)
          ├── Tier 1: YandexGPT adapter (IAM / OpenAI-compat)
          ├── Tier 2: Qwen3/DeepSeek via Yandex Cloud (OpenAI-compat)
          └── Tier 3: OpenAI/Anthropic adapter (gated)
```

The router can be configured per-task: coaching narrative → Tier 1 only; analysis/structuring → Tier 2 preferred; non-PDn analytics → Tier 3 allowed.

_Sources:_ [Habr — Multi-LLM Orchestrator universal Python client](https://habr.com/ru/articles/972740/) · [GitHub — ai-forever/gigachat SDK](https://github.com/ai-forever/gigachat) · [PyPI — yandexgpt-python](https://pypi.org/project/yandexgpt-python/) · [CodeGraph — Yandex AI Studio OpenAI-compatible API](https://codegraph.ru/docs/en/integrations/YANDEX_AI_STUDIO.html) · [Sber Developer — GigaChat Python SDK](https://developers.sber.ru/docs/ru/gigachain/tools/python/gigachat) · [Slatech — YandexGPT vs GigaChat deep comparison](https://www.slatech.co.il/ru/Compare-YandexGPT-vs-GigaChat-Deep)

### Telegram Bot Integration — Channel Adapter

Zabot's primary channel is Telegram. Key architectural decisions:

**Communication mode: Webhooks (not long-polling)**
- Webhooks scale better under load and are the standard for production bots.
- Pattern: parse the incoming `Update`, acknowledge fast (HTTP 200), hand heavier work (LLM calls, CRM lookups) to a background queue.
- Hosting: webhook handler on RU infrastructure (Yandex Cloud / Cloud.ru) behind an API gateway or ingress.

**Best practices (production-grade):**
- Own the Telegram API directly — avoid heavy wrapper libraries.
- Treat the bot as a backend system, not a script.
- Separate content (message templates) from code.
- Use `reply_markup` / `inline_keyboard` for structured check-ins (WHO-5 scale, mood emoji picker) — these are the "widget substitutes" for Telegram's lack of native widgets.

**Constraints acknowledged (from clarifying letter Q12):**
- Telegram doesn't guarantee delivery/read receipts — design for idempotent message handling.
- Quiet hours (21:00–09:00 local) are best-effort — the bot schedules messages within the window but can't enforce the user actually seeing them at that time.
- Timezone handling: store master's timezone in profile; calculate quiet hours dynamically.

_Sources:_ [Formamind — Telegram Bots Done Right](https://www.formamind.com/en/blog/telegram-bots-best-practices) · [Medium — Scalable Telegram Bot with BullMQ and Webhooks](https://medium.com/@pushpesh0/building-a-scalable-telegram-bot-with-node-js-bullmq-and-webhooks-6b0070fcbdfc) · [MessengerBot.app — Telegram Bot API in 2026](https://messengerbot.app/telegram-bot-api-in-2026-how-to-create-link-and-deploy-telegram-bots-step/)

### CRM Data Port — Deferred Adapter with Defined Contract

The CRM is the single source of truth for money, visit outcomes, and behavioral signals. Integration is deferred but the **port contract is defined now:**

```
abstract class CrmPort {
  /// Fetch receipt/transaction data for a master within a date range.
  Future<List<Receipt>> getReceipts({
    required String masterId,
    required DateTime from,
    required DateTime to,
  });

  /// Fetch schedule: upcoming visits, cancellations, no-shows.
  Future<List<Visit>> getSchedule({
    required String masterId,
    required DateTime from,
    required DateTime to,
  });

  /// Fetch master profile (role, salon(s), timezone, employment dates).
  Future<MasterProfile> getMasterProfile(String masterId);

  /// Sync goals (bidirectional — see BT §11.1).
  Future<void> syncGoals({
    required String masterId,
    required List<Goal> goals,
  });
}
```

**Adapter implementations:**
- **Phase 1:** `FakeCrmAdapter` — returns mock data matching the Zabot BT schema. Enables full development and testing of the coaching engine, profiling, and motivation calculator.
- **Phase 2:** `RealCrmAdapter` — implements the actual CRM API (REST/webhook/SFTP, to be determined). Plugged in when the CRM contract is available.

**Data freshness assumption (for Phase 1):** the `FakeCrmAdapter` simulates "near-real-time" data (< 5 min lag). When the real adapter arrives, the freshness SLA is configured per entity type (receipts: minutes; schedule: minutes; profile: hours).

### Consent & Audit Integration — PDn Compliance Port

Art. 16 puts the burden of proving consent on the operator. Art. 19 requires security measures. The architecture addresses both through an immutable **Consent & Decision Audit Log**:

**Consent data model:**
```
ConsentRecord {
  id: UUID (immutable)
  masterId: String
  consentType: 'base_pdn' | 'profiling_art16' | 'special_category_art10' | 'transborder_art12'
  granted: bool
  timestamp: DateTime (server-side, not client-reported)
  ipAddress: String (of the consent UI)
  channel: 'telegram' | 'web' | ...
  version: String (consent form version — for auditing which text they agreed to)
  withdrawnAt: DateTime? (null if active; set on revocation)
  metadata: Map<String, dynamic> (free-form, e.g. Telegram chat ID)
}
```

**Automated decision audit trail (Art. 16 proof):**
Every time the system makes a decision based on profiling (e.g., traffic-light escalation, motivation-scheme adjustment, proactive trigger), a `DecisionRecord` is appended:
```
DecisionRecord {
  id: UUID
  masterId: String
  decisionType: 'traffic_light_change' | 'motivation_adjustment' | 'proactive_outreach' | ...
  inputSummary: Map (which data factors contributed — without full PDn in the log)
  output: Map (the decision taken)
  modelVersion: String (which profiling model/rules version)
  timestamp: DateTime
  consentRef: UUID (links to the active ConsentRecord — proving consent was in place)
}
```

**Storage:** append-only table in PostgreSQL (no UPDATE/DELETE). For immutable proof, consider write-once with cryptographic chaining (hash of previous record) — but for Phase 1, a simple append-only table with restricted database grants (INSERT-only for the audit service role) is sufficient.

**Revocation flow:** when a master withdraws consent (profiling or special-category):
1. `ConsentRecord.withdrawnAt` is set.
2. The coaching engine stops using profiling-based personalization; degrades to generic advice.
3. The traffic-light and motivation-scheme calculations stop; switch to CRM-only (non-profiling) metrics.
4. Historical data is retained (Art. 11 requires storage accuracy) but is no longer actively processed for profiling.
5. A notification is sent to the salon owner (aggregated, no PDn exposed).

_Sources:_ [SecurePrivacy — GDPR Consent Audit Evidence](https://secureprivacy.ai/blog/gdpr-consent-audit-evidence-requirements) · [Event-Driven.io — GDPR in Event-Driven systems](https://event-driven.io/en/gdpr_in_event_driven_architecture/) · [AESIRX — Immutable Audit Trails](https://aesirx.io/blog/compliance-one/immutable-audit-trails-when-your-audit-log-becomes-cryptographic-proof)

### Communication Patterns Summary

| Integration Point | Protocol | Pattern | Phase |
|---|---|---|---|
| Flutter app → Backend | HTTPS REST / WebSocket | API Gateway | 1 |
| Telegram → Backend | Webhooks (inbound), Bot API (outbound) | Async queue | 1 |
| Backend → LLM providers | HTTPS REST (OpenAI-compatible where possible) | Adapter + Router | 1 |
| Backend → CRM | TBD (REST / webhooks / SFTP) | Port + Adapter (fake → real) | 1 (fake), 2 (real) |
| Backend → PostgreSQL | TCP (PgBouncer pool) | Repository pattern | 1 |
| Consent/Audit events | In-process event → append-only DB | Immutable log | 1 |
| Future: CRM → Backend (push) | Webhooks / message queue | Event-driven (outbox pattern) | 2+ |

## Architectural Patterns and Design

> Architecture is mapped to the obligations the Zabot AI business requirements actually impose. Each pattern resolves a concrete constraint from [zabot_ai.md](docs/zabot_ai.md) or an open question in the clarifying letter — this is not a generic catalog.

### System Architecture Patterns

**The Deterministic Control Plane + LLM Narrative Layer — the core architectural rule (resolves clarifying-letter Q3).**

This is the most consequential design decision in the system. The BT (§11.2, §11.5, §15) and clarifying-letter Q3 demand that *all monetary calculations, income forecasts, motivation-scheme position, and "next %" values are computed deterministically from CRM data by formula*, and the LLM is only permitted to paraphrase values already computed — never to generate or round figures. The 2025–2026 industry consensus validates this as a **hybrid layered architecture**:

| Layer | Responsibility | Implementation in Zabot |
|---|---|---|
| **Narrative layer** | Understand free-text chat; generate empathetic, psychotype-tuned coaching messages | LLM (GigaChat / YandexGPT, Tier 1) |
| **Deterministic engine** | Money, planка, next-%, motivation-scheme calculator, traffic-light, recommendation ranking | Pure-code domain core (formulas over CRM data) |
| **Guardrail layer** | Validate every LLM output against the deterministic truth; enforce §15 ethics rules | Post-generation validator |
| **Orchestration** | Route between deterministic and probabilistic paths | Use-case (application) layer |

The decisive principle: **LLMs are probabilistic; business runs on determinism.** A layered design where a rule engine owns the money and the LLM only clothes it in words eliminates the "LLM invents a revenue figure" failure class. The validator rejects any generated message whose numbers do not byte-match the engine's output; on mismatch, the message is regenerated or templated.

```
┌─────────────────────────────────────────────────────────────┐
│                     Telegram / Flutter                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                   Application (Use Cases)                     │
│   CoachingSession · ProfilingEngine · TrafficLightFSM        │
│   MotivationCalculator · RecommendationEngine · Scheduler    │
└────┬───────────────────────┬────────────────────────────────┘
     │ (deterministic)       │ (narrative only)
┌────▼──────────────┐   ┌────▼───────────────────────────────┐
│ Deterministic     │   │ LLM Adapter (via LlmRouter/Port)   │
│ Engine (pure)     │   │  "paraphrase these EXACT numbers"  │
│ money, planка, %  │   │  depersonalization gateway ▶ LLM   │
└────┬──────────────┘   └────┬───────────────────────────────┘
     │                        │
     └──────► ┌───────────────▼────────────────┐ ◄──────────┘
              │  Guardrail / Output Validator    │
              │  numbers match engine? ethics?   │
              └────────────┬────────────────────┘
                           │ ✓ pass → send
```

_Source:_ [The Deterministic Control Plane for AI-Era Rules (Medium)](https://medium.com/@adnanmasood/under-the-conversational-ui-the-deterministic-control-plane-for-ai-era-rules-8b0cd3ad99cf) · [LLMs vs Deterministic Logic (GoPenAI)](https://blog.gopenai.com/llms-vs-deterministic-logic-overcoming-rule-based-evaluation-challenges-8c5fb7e8fe46) · [Deterministic AI Architecture: 5 Layers (KongHQ)](https://konghq.com/blog/engineering/deterministic-ai-architecture-enterprise-reliability) · [The Architecture of LLM-Powered Applications (Craig Risi)](https://www.craigrisi.com/post/the-architecture-of-llm-powered-applications-how-it-differs-from-conventional-software-architecture)

**Hexagonal (Ports & Adapters) — structural backbone (carried from Step 3).**

The domain (coaching engine, profiling, traffic-light, motivation calculator) is fully decoupled from infrastructure via ports. This is what makes the deferred-CRM and multi-LLM strategies possible: the domain calls `LlmPort`, `CrmPort`, `PdnPort`, `NotifPort`; adapters are plugged in per phase and per provider. The deterministic engine above sits *inside* the domain core — it never crosses a port boundary, so it is never at the mercy of an external probabilistic service.
_Source:_ [Hexagonal Architecture for AI Integration (Ableneo)](https://www.ableneo.com/insight/hexagonal-architecture-for-ai-integration/)

**Hierarchical Finite State Machine for the traffic-light (resolves clarifying-letter Q6).**

The светофор (🟢/🟡/🔴) is a state machine aggregate, but a flat FSM suffers **state/transition explosion** once hysteresis, "форсирование forbidden" guards, and escalation sub-states are added. The recommended pattern is a **Hierarchical FSM (HFSM)**: each status owns nested sub-states (e.g. 🔴 → *awaiting-owner-contact* → *owner-engaged* → *resolved*), and **guarded transitions** encode the hysteresis (exit-from-red requires N consecutive green signals, preventing "мигание"). Two non-negotiable rules: (1) transition logic lives in code, never in prompts — the LLM never decides the status; (2) every transition is appended to the decision audit log with its contributing factors.
_Source:_ [Introduction to Hierarchical State Machines (Barr Group)](https://barrgroup.com/blog/introduction-hierarchical-state-machines) · [State — Design Patterns Revisited](https://gameprogrammingpatterns.com/state.html) · [Hierarchical FSM (Medium)](https://medium.com/dotcrossdot/hierarchical-finite-state-machine-c9e3f4ce0d9e)

### Design Principles and Best Practices

- **Determinism where it matters, probability where it helps.** Money/status/scheme → deterministic; empathy/tone/phrasing → LLM. The boundary is the contract: the LLM receives *pre-computed* numbers and a *fixed* intent, never an open "how much did they earn?" question.
- **Explainability by construction (§6.5).** Every meaningful profile change is logged with rationale. This is realized as an event on the audit log, not a doc comment — the system can answer "why did the planка move?" by replay.
- **Single source of truth for money.** The CRM is the master for money/visits (clarifying-letter Q2); the motivation-scheme module is the master for planка/goals (BT §11.1). Conflicts resolved by ownership rules, not by the LLM guessing.
- **SOLID at the adapter seam.** Each provider is a single adapter implementing `LlmPort`; routing/fallback live in the adapter layer (Step 3). The domain has zero knowledge of GigaChat vs YandexGPT.
- **Consent is a precondition, not an afterthought.** No profiling use-case executes without checking the active `ConsentRecord` first — enforced in the application layer, fail-closed.
_Source:_ [Design Patterns for Long-Term Memory in LLM Architectures (Serokell)](https://serokell.io/blog/design-patterns-for-long-term-memory-in-llm-powered-architectures)

### Scalability and Performance Patterns

- **Timezone-aware scheduler with priority arbitration (resolves Q11 & BT §12).** Russia spans 11 time zones; quiet hours are 21:00–09:00 *local*; BT §12 mandates that **competing triggers send only the single most revenue-valuable** message. Pattern: store all timestamps in **UTC**; resolve the master's local window at dispatch using a DST-safe TZ library; make every job **idempotent**; route all proactive messages through a **priority queue** that enforces the §7.3 caps (≤5 initiatives/shift) and picks the highest-value trigger, deferring or merging the rest.
- **Deterministic-compute caching.** Motivation-scheme and planка recomputation is cheap and cacheable per (master, period); only invalidate on CRM receipt events. The LLM call (the expensive part) is cached by prompt-hash only when the inputs are identical.
- **Horizontal scaling of stateless workers.** The webhook ingress acknowledges fast (HTTP 200) and hands LLM/CRM work to background queue workers — the standard scalable-bot pattern (Step 3). Workers are stateless and horizontally scalable; state lives in PostgreSQL + the queue.
- **LLM tier routing for cost/latency.** The router (Step 3) routes empathy → Tier 1, analysis/structuring → Tier 2 (cheaper/faster), keeping p95 latency and token cost bounded per task type.
_Source:_ [How to Handle CronJob Timezone Scheduling (OneUptime, 2026)](https://oneuptime.com/blog/post/2026-02-09-cronjob-timezone-scheduling/view) · [Timezone-aware cron (Stack Overflow)](https://stackoverflow.com/questions/42986386/timezone-aware-cron-jobs-adjust-for-dst)

### Integration and Communication Patterns

- **Transactional Outbox (resolves reliable trigger emission + audit atomicity).** When a coaching decision is made, the `DecisionRecord` and the outgoing message are written in the *same* DB transaction; a separate worker publishes to Telegram. This eliminates the dual-write problem — no proactive trigger is lost and no audit gap opens. Consumers must be idempotent (at-least-once delivery).
- **CQRS-lite for audit.** Writes go through the use-cases; reads for owner reports (§14) and decision replay come from read models projected from the event log. Keeps the write side simple and the read side flexible for aggregated, PDn-safe reporting.
- **Outbox → future CRM push.** The same outbox infrastructure supports BT §11.1 bidirectional goal sync and Phase 2 CRM push (webhooks/MQ) — the pattern is forward-compatible without re-architecture.
_Source:_ [Pattern: Transactional Outbox (microservices.io)](https://microservices.io/patterns/data/transactional-outbox.html) · [Reliable Event Notifications with Transactional Outbox (Medium)](https://medium.com/event-driven-utopia/sending-reliable-event-notifications-with-transactional-outbox-pattern-7a7c69158d1b)

### Security Architecture Patterns

- **Multi-tenant salon isolation via PostgreSQL Row-Level Security (resolves clarifying-letter Q1).** Every PDn table carries a `salon_id`; RLS policies enforce isolation at the *engine level*, removing reliance on application `WHERE` clauses. A master spanning two salons is handled via a master↔salon membership table + union of permitted tenant contexts. Owner/manager read scope (Q1: does the owner see profile scales?) is enforced as a separate RLS policy on the same tables.
- **Depersonalization gateway at the LLM seam.** Direct identifiers are stripped from prompts before they reach any LLM adapter; only what the coaching narrative needs crosses the boundary (Step 2).
- **Immutable consent & decision log (Art. 16 / Art. 19 proof).** Append-only table with an INSERT-only DB role for the audit service. The **"Consent Shield"** technique — each consent record hashed and digitally signed — produces tamper-evident, legally defensible proof that consent was in place when a profiling decision was made.
- **Right-to-erasure vs immutability.** The append-only audit log conflicts with deletion obligations. Resolution: **crypto-shredding + tombstones** — events are encrypted with a per-subject key; "erasure" destroys the key, rendering the payload unreadable while preserving the audit chain shape. *(Engineering-sound; final legal sign-off required.)*
- **Secrets & key management.** Per-provider OAuth2/IAM credentials in Yandex Cloud KMS / Cloud.ru KMS; encryption at rest and in transit throughout.
_Source:_ [Multi-tenant data isolation with PostgreSQL RLS (AWS)](https://aws.amazon.com/blogs/database/multi-tenant-data-isolation-with-postgresql-row-level-security/) · [Row Level Security for Tenants (Crunchy Data)](https://www.crunchydata.com/blog/row-level-security-for-tenants-in-postgres) · [GDPR in Event-Driven systems (event-driven.io)](https://event-driven.io/en/gdpr_in_event_driven_architecture/) · [Consent Shield concept (Dilger, LinkedIn)](https://www.linkedin.com/posts/martindilger_gdpr-in-event-sourcing-is-far-more-difficult-activity-7425425970897092608-loIO)

### Data Architecture Patterns

**Three-tier LLM memory (resolves BT §13 — "Память и данные").** The 2026 consensus for personalization agents is a multi-tier memory that maps almost 1:1 onto Zabot's stated model. A critical design rule from the research: **user/personalization memory must be architecturally distinct from the knowledge base** — profile scales are structured and auditable, not buried in a vector blob.

| Tier | Zabot concept (§13) | Store | Privacy |
|---|---|---|---|
| **Short-term session cache** | "Краткосрочный фокус" — current period, open agreements | In-process / Redis (RU-hosted) | PDn, TTL-bounded |
| **Mid-term vector memory (RAG)** | Client histories, glossary, scientific basis (§4) | `pgvector` on the RU Postgres | PDn, RLS-scoped |
| **Long-term structured** | "Долгосрочная память" — профиль (тип, шкалы, барьеры), client recommendation profiles | PostgreSQL relational, versioned | PDn, RLS + consent-gated |

**Storage surfaces (all RU-hosted, FSTEC/152-ФЗ posture):**
- **PostgreSQL (multi-tenant, RLS)** — masters, salons, visits, motivation schemes, planка history, consent records, decision audit log.
- **Events / time-series** — mood screenings (WHO-5), behavioral signals, traffic-light transitions, recommendation outcomes (the feedback loop of §8.4).
- **`pgvector`** — embeddings over client visit history (for next-best-offer retrieval, §8.2), the glossary (Appendix В), and the scientific-basis reference (§4) used to ground prompts.
- **Append-only audit** — consent + decision records (see Security section).
_Source:_ [Multi-Tier Persistent Memory for LLMs (HealthArk)](https://healthark.ai/persistent-memory-for-llms-designing-a-multi-tier-context-system/) · [Long-Term Memory Architectures for AI Agents (Redis)](https://redis.io/blog/long-term-memory-architectures-ai-agents/) · [Should "User Memory" Be Distinct from the KB? (r/Rag)](https://www.reddit.com/r/Rag/comments/1pljhel/should_user_memory_be_architecturally_distinct/) · [Long-Term Memory: Foundation of AI Self-Evolution (arXiv)](https://arxiv.org/html/2410.15665v1)

### Deployment and Operations Architecture

- **LLM observability — every call traced.** Each LLM call is recorded with prompt version, token usage, cost, latency, and outcome — for cost control (per master/salon) and for **auditability** ("which prompt version produced this decision?"). **Langfuse** (open-source, self-hostable on RU infra) is the standard fit and integrates with the OpenAI-compatible endpoints chosen in Step 3; it gives prompt management + A/B + evaluation alongside tracing.
- **Containerized backend on Managed Kubernetes** (Yandex Cloud / Cloud.ru), webhook ingress + background worker pool, behind the RU residency boundary. PgBouncer for connection pooling.
- **Infrastructure as Code** — Terraform (Yandex Cloud / Cloud.ru providers) for reproducible, auditable infra provisioning.
- **PDn residency enforced at deployment boundary** — no infra component, log sink, or observability backend may leave RF soil; this is a deployment-time invariant, not a code convention.
_Source:_ [LLM Observability & Application Tracing (Langfuse)](https://langfuse.com/docs/observability/overview) · [Token & Cost Tracking (Langfuse)](https://langfuse.com/docs/observability/features/token-and-cost-tracking) · [AI Agent Observability with Langfuse](https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse)

### Architectural Patterns — Confidence Summary

- **High confidence:** deterministic-vs-LLM boundary, HFSM for the traffic-light, transactional-outbox + append-only audit, RLS multi-tenant isolation, three-tier memory, observability tooling — all grounded in current sources and mapping cleanly onto the BT.
- **Medium (flag for counsel / owner decision):** exact HFSM hysteresis thresholds (clarifying-letter Q6 still open), and whether crypto-shredding satisfies the RF data-destruction obligation (engineering-sound; requires legal sign-off).

## Implementation Approaches and Technology Adoption

> Implementation is mapped to the constraints Zabot AI actually carries: a Russian-language coaching product, a 152-FZ residency boundary, a deferred CRM, a Flutter client, and the non-negotiable "deterministic engine owns the money" rule. Generic best-practice is adapted, not transcribed.

### Technology Adoption Strategies

**The phasing that the BT and clarifying letter already imply is the correct adoption strategy.** The 2026 industry consensus for GenAI rollout is a strict staged path — Discovery → Prototype → PoC → MVP → Pilot → Production hardening → Full rollout — and crucially, *most AI pilots fail to scale* when they skip the optimization phase. Zabot's risk profile (PDn + money + psychological profiling) makes a disciplined phase gate mandatory, not optional.

**Recommended phased adoption for Zabot AI:**

| Phase | Goal | LLM posture | CRM | Data |
|---|---|---|---|---|
| **0. Prototype (≤2 wk)** | Validate the deterministic-engine + LLM-narrative pattern on synthetic data | Tier 1 (GigaChat/YandexGPT), depersonalized test prompts | `FakeCrmAdapter` | Synthetic, no real PDn |
| **1. MVP (1–2 mo)** | Coaching loop + traffic-light + consent capture, single salon, internal testers | Tier 1 only, RU-hosted | `FakeCrmAdapter` (near-real-time simulation) | Real PDn, full consent + audit |
| **2. Pilot (2–3 mo)** | 1–3 salons, real masters, Yandex Boost AI grant funding the LLM spend | Tier 1 + Tier 2 (Qwen/DeepSeek via Yandex Cloud) for analysis tasks | `RealCrmAdapter` (read-only first) | Real PDn, full observability |
| **3. Production hardening** | Guardrails, eval regression suite, cost caps, RLS tenant isolation proven | Full multi-tier router + fallback | Bidirectional CRM sync (BT §11.1) | Full scale |
| **4. Rollout** | Multi-salon, all timezones, quiet-hours scheduler at scale | Tier 3 (foreign) only if Tier 1+2 quality gap proven, consent-gated | Full | Full |

**Two adoption rules that are specific to Zabot (not from the generic literature):**

1. **The deterministic engine is built and unit-tested *before* any LLM is wired.** The money/planка/traffic-light calculations must pass formula tests on synthetic CRM data independently of GigaChat/YandexGPT. The LLM is then added only as a paraphraser of values the engine has already computed. This inverts the usual "wire the LLM first" MVP failure.
2. **Adopt the Yandex Cloud Boost AI grant (up to 1M ₽) to fund Phase 0–2 LLM spend.** This removes cost as the reason to rush provider selection and lets the pilot prove Tier 1+2 quality before any Tier 3 (foreign/consent-gated) path is considered.

_Source:_ [Microsoft — GenAI deployment strategy: PoC to MVP](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/the-evolution-of-genai-application-deployment-strategy-from-poc-to-mvp/4149652) · [NextPage IT — Generative AI implementation timeline 2026](https://nextpageit.com/blog/generative-ai-implementation-timeline) · [Concord — why most AI pilots fail to scale](https://www.concordusa.com/blog/navigating-ai-implementation-planning-and-piloting-for-success-phases-0-1) · [Michigan Online — the Pilot-Optimize-Rollout process](https://online.umich.edu/collections/artificial-intelligence/short/the-pilot-optimize-rollout-por-process/)

### Development Workflows and Tooling

**Language & framework stack (backend/AI layer):** **Python** is the correct choice for the orchestration and deterministic-engine layer — it has the deepest provider SDK support (GigaChat Python SDK, `langchain-gigachat`, `yandexgpt-python`, and the standard `openai` lib pointed at Yandex AI Studio's OpenAI-compatible endpoint). The consumer app is Flutter (mobile). The deterministic engine is a pure-Python domain core (no LLM calls) so it is trivially unit-testable.

**GigaChain is Sber's official framework** for building GigaChat apps and multi-agent systems, integrating GigaChat with LangChain/LangGraph and oriented toward Russian-language applications. Two viable workflow shapes:

| Workflow | Pros | Cons | When |
|---|---|---|---|
| **GigaChain / LangChain** on top of GigaChat | Fastest start with GigaChat; agent primitives; RU-tuned | Heavier; must verify no foreign telemetry egress | If GigaChat is primary Tier 1 |
| **Thin `LlmPort` adapters + standard `openai` lib** (Step 3 unified client) | Provider-agnostic; YandexGPT/Qwen/DeepSeek all speak OpenAI-compat; minimal lock-in | More bespoke routing code | Recommended — matches the hexagonal architecture |

**The hexagonal `LlmPort` (Step 3) is the workflow invariant:** the domain and the deterministic engine never import a provider SDK. All provider specifics (OAuth2 for GigaChat, IAM for Yandex) live in adapter modules. This keeps the deterministic-vs-probabilistic boundary (Step 4) enforceable in CI: a lint rule can forbid `import gigachat` outside the `adapters/llm/` directory.

**Version control, CI/CD, and IaC — all on RU soil:**
- **Git:** Yandex Cloud Managed Service for GitLab (or self-hosted GitLab on the same cluster) keeps source and pipelines inside the residency boundary.
- **CI/CD:** GitLab Runner on Managed Kubernetes; pipeline = lint → unit tests (deterministic engine) → **eval regression suite** (LLM) → guardrail checks → build → deploy.
- **IaC:** Terraform with the official Yandex Cloud provider (and/or Cloud.ru provider) — clusters, DBs, KMS keys, RLS policies, and the residency boundary are all declarative and auditable.

_Source:_ [ai-forever/langchain-gigachat (GitHub)](https://github.com/ai-forever/langchain-gigachat) · [GigaChain — official Sber docs](https://developers.sber.ru/docs/ru/gigachain/overview) · [Context7 — GigaChain overview (LangChain/LangGraph)](https://context7.com/ai-forever/gigachain) · [TrueTech — GigaChat OAuth + token caching in production](https://truetech.dev/ai-development/services/llm/gigachat-sber-api-integration.html) · [Yandex Cloud — Managed Kubernetes](https://yandex.cloud/en/services/managed-kubernetes) · [Yandex Cloud — Managed GitLab concepts](https://yandex.cloud/en/docs/managed-gitlab/concepts/)

### Testing and Quality Assurance

Zabot needs **three distinct testing strata**, because the deterministic engine, the LLM narrative, and the guardrails each fail differently.

**Stratum 1 — Deterministic engine (traditional unit/property tests, high coverage).**
The money, planка, next-%, motivation-scheme calculator, and traffic-light HFSM transitions are pure functions over CRM data. These get standard pytest with property-based testing (e.g. Hypothesis) and 100% deterministic assertions — "given these receipts, planка must equal X." This is where the highest coverage belongs. The HFSM hysteresis (exit-from-red needs N green signals) is exhaustively state-transition-tested here, never delegated to the LLM.

**Stratum 2 — LLM narrative (eval/regression testing, non-deterministic).**
LLM outputs can't be byte-asserted, so the 2026 standard is **LLM-as-a-judge** plus golden-dataset regression. A curated golden set of coaching scenarios is run through the full pipeline on every change; a judge model scores outputs against rubrics (empathy, RU-language quality, **numbers-must-match-engine**, ethics/§15 compliance). Critically for Zabot, the **strongest eval is not subjective — it is the guardrail validator itself**: any LLM output whose numbers do not byte-match the deterministic engine is an automatic test failure, regardless of how good the prose sounds.

- **Tooling:** DeepEval (pytest-native, integrates into the existing CI) for the rubric/judge layer; the deterministic-engine byte-match as the hard gate.
- **Regression discipline:** prompt/model changes are versioned in Langfuse prompt management; a regression run diffs the new outputs against the golden baseline so quality drift is visible before merge.

**Stratum 3 — Guardrails & security (adversarial).**
Separate tests for prompt-injection resistance (a master tries to make the bot reveal another master's data or compute a different planка), PII-leakage through the depersonalization gateway, and §15 ethics-rule violations. These are red-team tests, not happy-path.

_Source:_ [DeepEval — LLM-as-a-Judge in 2026](https://deepeval.com/blog/llm-as-a-judge) · [Confident AI — LLM testing methods 2026](https://www.confident-ai.com/blog/llm-testing-in-2024-top-methods-and-strategies) · [Evidently AI — what is an LLM evaluation framework](https://www.evidentlyai.com/blog/llm-evaluation-framework) · [Braintrust — LLM evaluation & regression guide](https://www.braintrust.dev/articles/llm-evaluation-guide) · [NVIDIA NeMo Guardrails — fact-checking rails](https://docs.nvidia.com/nemo/guardrails/configure-guardrails/guardrail-catalog/fact-checking) · [NHIMG — programmatic output validation + state-machine guardrails](https://nhimg.org/articles/guardrails-for-llm-output-validation-now-shape-ai-safety/)

### Deployment and Operations Practices

**Observability — Langfuse, self-hosted on RU infra (carried from Step 4, now operationally specified).** Self-hosted Langfuse runs the *same codebase* as its cloud — full tracing, token/cost tracking, prompt versioning, and eval are free and unlimited in the OSS self-hosted edition, and all data stays on RF soil (satisfying the residency invariant). Every LLM call is traced with: prompt version, provider, token usage, cost, latency, depersonalization-gateway pass/fail, and guardrail pass/fail. This doubles as audit evidence ("which prompt version produced this profiling decision?").

**LLM gateway — operational resilience.** Behind the `LlmPort` adapters, a gateway provides retries, cooldowns, and provider fallback (Tier 1 GigaChat → YandexGPT → Tier 2 Qwen) plus per-master/per-salon cost attribution and caps. Two open-source options fit the RU self-hosted requirement: the Multi-LLM Orchestrator (Step 3, RU-provider-native) or **LiteLLM** (Rust-core proxy, 100+ providers behind one OpenAI-compatible API, built-in cost tracking and per-user attribution). Either runs as a sidecar/service in the same cluster.

**Deployment topology (all RU-hosted):**
- **Managed Kubernetes** (Yandex Cloud / Cloud.ru) — control plane is free; cost is the underlying compute (VMs/disks/egress). Use preemptible VMs + autoscaling node groups for the stateless background workers; fix-size the DB tier.
- **PgBouncer** connection pooling in front of PostgreSQL.
- **Transactional outbox** (Step 4) decouples message emission from the webhook ingress — the Telegram webhook returns HTTP 200 fast, workers process LLM/CRM work idempotently.
- **IaC:** Terraform provisions the whole residency boundary; CI deploys via GitOps (GitLab Agent for Kubernetes).

**Incident & DR posture:** PostgreSQL Point-in-Time-Recovery + cross-availability-zone managed DB (Yandex Cloud has 4 AZs); the append-only audit log is backed up with the same immutability guarantee. LLM provider outage is handled by gateway fallback, not by human paging — Tier 2 (Qwen/DeepSeek) can carry the coaching narrative at slightly lower quality while Tier 1 recovers.

_Source:_ [Langfuse — self-hosting](https://langfuse.com/self-hosting) · [Langfuse — token & cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking) · [Langfuse — self-hosted pricing (free, unlimited OSS)](https://langfuse.com/pricing-self-host) · [LiteLLM — Router load balancing & fallback](https://docs.litellm.ai/docs/routing) · [BerriAI/litellm (GitHub)](https://github.com/BerriAI/litellm) · [TrueFoundry — LiteLLM alternatives 2026](https://www.truefoundry.com/blog/litellm-alternatives)

### Team Organization and Skills

Zabot is a small team, so the question is **which hats exist, not how many people**. The 2026 LLM-product role map maps onto ~3 core hats, with the "prompt engineer" deliberately absorbed into the AI engineer role (standalone prompt-engineer titles are being retired industry-wide in favor of AI engineers with prompt + eval depth).

| Hat | Owns | Key skills |
|---|---|---|
| **AI Engineer** (Python, LLM + eval depth) | `LlmPort` adapters, depersonalization gateway, prompt management, eval/regression suite, Langfuse | RAG, LLMOps, prompt engineering as a discipline, eval/judge design |
| **Backend / Domain Engineer** | Deterministic engine, HFSM, motivation calculator, CRM port, RLS, outbox, consent/audit | Pure-domain design, Postgres/RLS, transactional integrity, hexagonal architecture |
| **Mobile Engineer (Flutter)** | Consumer app, Telegram channel adapter, consent UI, quiet-hours handling | Flutter, Telegram Bot API, mobile security |

**Two skills gaps to flag early:**
1. **Russian data-protection (152-FZ) literacy** is not an engineering skill but is project-critical — either train one engineer to a working level or retain a ПДн counsel for sign-off on the open legal questions (Art. 10 special-category classification of mood data; Art. 16 "significant consequences" threshold; crypto-shredding vs RF destruction obligation — all flagged medium-confidence in Steps 2/4).
2. **LLMOps discipline** (eval pipelines, cost tracking, prompt versioning) is the difference between a pilot that scales and one that stalls — the literature is emphatic that this is where pilots fail.

_Source:_ [Acceler8 Talent — in-demand ML roles 2026](https://www.acceler8talent.com/resources/blog/the-most-in-demand-machine-learning-roles-in-2026--managing-the-ai-talent-frontier/) · [Kore1 — how to hire a prompt engineer 2026 (role is being absorbed)](https://www.kore1.com/how-to-hire-prompt-engineer-2026/) · [Ivan Turkovic — AI job-title reference guide 2026](https://www.ivanturkovic.com/the-ai-job-title-reference-guide-2026/)

### Cost Optimization and Resource Management

**LLM cost — the dominant variable cost — is bounded by the deterministic-engine architecture itself.** Because the LLM only paraphrases pre-computed numbers (never computes), prompts are short and deterministic; the expensive "open-ended reasoning" calls are confined to Tier 2 analysis tasks. Concrete levers:

- **Tier routing:** empathy/narrative → Tier 1 (GigaChat / YandexGPT Lite ≈ 0.20 ₽/1k tok); structuring/analysis → Tier 2 (Qwen 3 / DeepSeek via Yandex Cloud). YandexGPT Pro 5.1 ≈ 0.80 ₽/1k tok reserved for the few cases needing it.
- **Grant funding:** Yandex Cloud Boost AI (up to 1,000,000 ₽) covers Phase 0–2 LLM spend entirely; Sber's Feb-2026 ~3× GigaChat price cut further lowers Tier 1 baseline cost.
- **Caching:** deterministic-engine outputs cached per (master, period), invalidated only on CRM receipt events; LLM responses cached by prompt-hash only when inputs are byte-identical (rare for empathetic narrative, common for structured analysis — cache the latter aggressively).
- **Gateway cost caps:** per-master and per-salon token/cost ceilings via the LiteLLM/orchestrator gateway; alerts in Langfuse when a salon approaches its cap.

**Infrastructure cost:**
- Managed Kubernetes control plane is free; optimize with preemptible VMs for stateless workers, autoscaling node groups, and right-sized DB tier.
- `pgvector` on the existing Postgres avoids a separate vector DB (one fewer paid service, one fewer data-residency surface).
- Self-hosted Langfuse (OSS) is free and unlimited vs. paying per-trace on a SaaS observability plan.

_Source:_ [Yandex Cloud — Managed Kubernetes (free control plane, up to 60% savings)](https://yandex.cloud/en/services/managed-kubernetes) · [Langfuse — self-hosted pricing](https://langfuse.com/pricing-self-host) · [LiteLLM — per-user cost attribution](https://docs.litellm.ai/docs/proxy/load_balancing) · [vc.ru — YandexGPT API pricing walkthrough](https://vc.ru/provod/3035416-yandexgpt-api-pervyj-zapros-i-raschet-stoimosti)

### Risk Assessment and Mitigation

| Risk | Likelihood | Impact | Mitigation (already designed in) |
|---|---|---|---|
| **LLM invents/hallucinates a money figure or planка** | Medium | Critical | Deterministic engine computes all numbers; guardrail validator byte-matches LLM output → engine; mismatch = regenerate/templatize. LLM never sees an open "how much?" question. |
| **Prompt injection extracts another master's PDn** | Medium | Critical | Depersonalization gateway strips identifiers pre-LLM; RLS enforces tenant isolation at DB engine level (not app `WHERE`); red-team tests in Stratum 3. |
| **152-FZ residency breach (data leaves RF)** | Low (if architected) | Critical | Residency enforced at deployment boundary (Step 4); Tier 3 foreign path consent-gated + Roskomnadzor-notified; Langfuse + gateway logs prove no egress. |
| **Consent gap — profiling runs without valid consent** | Medium | High | Consent is a fail-closed precondition in the application layer; `DecisionRecord` links to active `ConsentRecord`; withdrawal degrades to non-profiling mode automatically. |
| **Traffic-light "мигание" (status flicker)** | Medium | Medium | HFSM hysteresis (N consecutive signals to exit red); transition logic in code, never in prompts; every transition audited. |
| **Provider outage (GigaChat/YandexGPT down)** | Low-Medium | Medium | Gateway fallback across Tier 1 providers → Tier 2; idempotent workers survive retries. |
| **Pilot fails to scale** | High (industry baseline) | High | Disciplined PoC→MVP→Pilot→Hardening phases; LLMOps eval pipeline from Phase 0; deterministic engine de-risks the money path early. |
| **Legal mis-classification (mood data as Art. 10 special category)** | Medium | High | Engineering posture (written consent + audit + RU hosting) is sound under any interpretation; final sign-off deferred to ПДн counsel — does not block Phase 0–1. |

_Source:_ [NVIDIA — hallucination prevention with guardrails](https://developer.nvidia.com/blog/prevent-llm-hallucinations-with-the-cleanlab-trustworthy-language-model-in-nvidia-nemo-guardrails/) · [Guardrails AI — provenance validators](https://guardrailsai.com/blog/reduce-ai-hallucinations-provenance-guardrails) · [Arthur AI — input/output checks + RAG grounding](https://www.arthur.ai/column/ai-guardrails-reduce-hallucinations) · [Concord — why AI pilots fail to scale](https://www.concordusa.com/blog/navigating-ai-implementation-planning-and-piloting-for-success-phases-0-1)

## Technical Research Recommendations

### Implementation Roadmap

1. **Phase 0 (≤2 wk):** Build + unit-test the deterministic engine and HFSM on synthetic data. Stand up `LlmPort` + one GigaChat adapter behind the depersonalization gateway. Prove the "engine computes, LLM paraphrases, guardrail validates" loop end-to-end. *No real PDn.*
2. **Phase 1 (1–2 mo):** Consent capture, audit log, RLS multi-tenancy, `FakeCrmAdapter`. Single salon, internal testers. Full Langfuse tracing. Funded by Yandex Boost AI grant.
3. **Phase 2 (2–3 mo):** 1–3 pilot salons, real masters, `RealCrmAdapter` read-only. Add Tier 2 (Qwen/DeepSeek) for analysis. Build the eval golden-set + regression CI gate.
4. **Phase 3:** Guardrail hardening, cost caps, bidirectional CRM sync (BT §11.1), quiet-hours multi-TZ scheduler at scale.
5. **Phase 4:** Multi-salon rollout; activate Tier 3 only if a documented Tier 1+2 quality gap requires it, behind separate consent.

### Technology Stack Recommendations

- **Backend/AI:** Python, hexagonal `LlmPort`, deterministic pure-domain core. GigaChain/LangChain only if GigaChat is sole Tier 1; otherwise thin adapters + `openai` lib at Yandex base URL.
- **LLM gateway:** LiteLLM or Multi-LLM Orchestrator (self-hosted, RU infra) for routing/fallback/cost-caps.
- **Observability + prompt mgmt + eval:** self-hosted Langfuse (OSS).
- **Eval framework:** DeepEval (pytest-native) + deterministic-engine byte-match hard gate.
- **Data:** PostgreSQL + `pgvector` + RLS, append-only consent/audit, Redis (RU) for session cache.
- **Infra:** Yandex Cloud (or Cloud.ru) Managed Kubernetes, Managed PostgreSQL, KMS, Managed GitLab, Terraform IaC.
- **Client:** Flutter (mobile) + Telegram Bot API (webhooks).

### Skill Development Requirements

- Train/retain **LLMOps discipline** (eval pipelines, prompt versioning, cost tracking) — the single biggest predictor of scaling past pilot.
- Develop **152-FZ working literacy** in one engineer; retain ПДн counsel for the medium-confidence legal sign-offs (Art. 10/16/22 classification, crypto-shredding).
- Strengthen **deterministic-domain-design** skill (hexagonal, pure core, RLS) — this is the architectural backbone and must not be eroded by LLM-centric shortcuts.

### Success Metrics and KPIs

- **Engine integrity:** 100% guardrail byte-match pass rate in CI; zero "LLM-generated figure ≠ engine figure" incidents in production.
- **Compliance:** 100% of profiling `DecisionRecords` linked to a valid `ConsentRecord`; zero PDn egress outside RF (verified in gateway/Langfuse logs); consent withdrawal → profiling stop < 1 event.
- **Eval health:** golden-set regression pass rate ≥ threshold on every merge; judge-rubric scores stable or improving release-over-release.
- **Cost:** LLM ₽/active-master/month within grant budget through Phase 2; per-salon cost caps respected.
- **Reliability:** webhook p99 acknowledgement < target; provider-failover covers Tier 1 outages without user-visible failure.
- **Product:** pilot NPS / coaching-session engagement; traffic-light escalation precision (few false reds).

## Executive Summary

Zabot AI is a Russian-language coaching assistant for salon beauty-industry masters that processes money, motivational psychology, and mood data under Russian Federal Law 152-FZ. This research unblocks the technology-stack decision (Block 1, Q4 of the clarifying letter) so development can begin on a compliant footing. The central finding is that the three hardest constraints — **money integrity**, **psychological-profiling consent**, and **PDn residency** — are not three separate problems but resolve into a single architectural rule: a **deterministic control plane owns all money, status, and profiling decisions; the LLM only clothes pre-computed truth in empathetic Russian-language narrative, and every component lives on RF soil.**

On that foundation, the stack decision becomes low-risk: a **multi-tier RU-LLM strategy** — GigaChat and YandexGPT as Tier 1 for the coaching "voice," Qwen 3 / DeepSeek / Gemma via Yandex Cloud AI Studio as Tier 2 for analysis (all OpenAI-compatible, 100% RF residency), with foreign models only as an optional, consent-gated Tier 3. The pilot is fundable entirely by the **Yandex Cloud Boost AI grant (up to 1M ₽)**, against a backdrop of Sber's ~3× GigaChat price cut (Feb 2026) — RU LLMs are now cost-competitive for production. The 01.07.2025 localization amendment (fines up to RUB 6M for a first offense) makes the RU-infra choice effectively mandatory, removing the last reason to hedge.

**Key Technical Findings:**

- **Determinism where it matters, probability where it helps** — the LLM receives pre-computed numbers and a fixed intent, never an open financial question; a guardrail validator byte-matches every LLM output against the deterministic engine. This eliminates the "LLM invents a revenue figure" failure class by construction.
- **Hexagonal ports de-risk schedule and vendor lock-in** — a defined `CrmPort` (with a `FakeCrmAdapter`) lets the full coaching engine, profiling, and motivation calculator be built *now*, before the real CRM contract exists; a unified `LlmPort` makes providers interchangeable.
- **Consent and audit are first-class infrastructure** — an append-only consent-and-decision log (Art. 16 proof), RLS-enforced multi-tenant isolation, and a depersonalization gateway at the LLM seam satisfy the profiling, security, and explainability obligations together.
- **The deterministic-control-plane + guardrail-stack pattern is the emerging 2026–2027 industry standard** for agentic systems — Zabot's architecture is aligned with the direction of travel, not a bet against it.

**Strategic Recommendations:**

1. Adopt the multi-tier RU-LLM strategy; pilot Tiers 1+2 on depersonalized data funded by the Yandex grant.
2. Build and unit-test the deterministic engine before wiring any LLM — invert the usual MVP failure.
3. Stand up consent capture, the audit log, and RLS in Phase 1 (MVP), not later.
4. Make LLMOps (eval golden-set, Langfuse tracing, cost caps) a Phase-0 discipline — it is the single biggest predictor of scaling past pilot.
5. Retain ПДн counsel for the three medium-confidence legal sign-offs (Art. 10/16/22 classification, crypto-shredding) — these do not block Phase 0–1.

## Detailed Table of Contents

> Sections marked ✅ are written in this document (Steps 2–5); sections marked 🆕 are added in this synthesis.

1. Research Overview & Scope ✅ *(top of document)*
2. Technology Stack Analysis ✅ — LLM Provider Layer · Orchestration · Database/PDn Storage · Cloud/Hosting · Depersonalization Patterns · Trends · Quality Assessment
3. Integration Patterns Analysis ✅ — Hexagonal backbone · Multi-LLM unified client · Telegram webhooks · CRM port (deferred) · Consent & audit port
4. Architectural Patterns and Design ✅ — Deterministic control plane + LLM narrative · HFSM traffic-light · Transactional outbox · RLS multi-tenancy · Three-tier memory · LLM observability
5. Implementation Approaches and Technology Adoption ✅ — Adoption strategy · Dev workflows/tooling · Testing (3 strata) · Deployment/ops · Team/skills · Cost optimization · Risk register
6. Technical Research Recommendations ✅ — Roadmap · Stack · Skills · KPIs
7. Cross-Cutting Technical Synthesis 🆕
8. Future Technical Outlook 🆕
9. Technical Research Methodology & Source Verification 🆕
10. Technical Appendices & Reference Materials 🆕
11. Technical Research Conclusion & Next Steps 🆕

## Cross-Cutting Technical Synthesis

Three insights emerge only when the steps are read together — each is a load-bearing conclusion for the project:

**Synthesis 1 — The constraints converge on one rule, not three.** Money integrity (BT §11), profiling consent (Art. 16), and PDn residency (Art. 18 ч.5) each look like independent compliance burdens. In fact they share a single resolution: keep all computation that has *legal or financial consequence* inside a deterministic, RF-resident domain core, and let the LLM only paraphrase. The same append-only audit log that proves money-calculation correctness also proves profiling consent (via `consentRef`) and residency (via deployment-boundary enforcement). One architectural decision discharges three obligations.

**Synthesis 2 — The deferred CRM is an opportunity, not a blocker.** The clarifying letter frames the unknown CRM contract as a dependency. The hexagonal `CrmPort` + `FakeCrmAdapter` turns it into an enabler: the entire coaching engine, traffic-light HFSM, motivation calculator, and consent flow can be built, tested, and demoed against synthetic data — including the deterministic-vs-LLM guardrail loop — on a Phase-0 timeline. The real adapter is a *plug-in* for Phase 2, not a prerequisite for Phase 1.

**Synthesis 3 — Compliance is a continuous engineering invariant, not a legal checkbox.** Residency, consent-preconditioning, and depersonalization are enforced as *deployment-time and code-time invariants* (RLS policies, INSERT-only audit roles, a depersonalization gateway, lint rules forbidding provider imports outside `adapters/llm/`). The eval regression suite's hard gate — "LLM numbers must byte-match the engine" — is simultaneously a quality test and a financial-integrity safeguard. This makes compliance something CI verifies on every commit, not something a lawyer signs off once.

## Future Technical Outlook

**Near-term (1–2 years): the deterministic-control-plane consensus hardens.** The 2026 literature is converging on exactly the architecture Step 4 prescribes: hard-coded deterministic logic gates ("the agent control plane") with fast pre-LLM guardrails and post-LLM validation, treating the guardrail stack as "the new firewall" of the agentic era. Zabot's design is therefore aligned with where the industry is going, not a bespoke bet. Expect guardrail tooling (NeMo Guardrails, Guardrails AI) and eval platforms (DeepEval, Langfuse eval) to commoditize further, lowering the LLMOps cost over the pilot window.
_Source:_ [AI Agents in 2026 — Tools, Memory, Evals, Guardrails](https://andriifurmanets.com/blogs/ai-agents-2026-practical-architecture-tools-memory-evals-guardrails) · [CIO — The Agent Control Plane](https://www.cio.com/article/4130922/the-agent-control-plane-architecting-guardrails-for-a-new-digital-workforce.html) · [Arthur AI — Pre-LLM & Post-LLM guardrails](https://www.arthur.ai/blog/best-practices-for-building-agents-guardrails) · [7 Agentic AI Trends to Watch in 2026](https://machinelearningmastery.com/7-agentic-ai-trends-to-watch-in-2026/)

**Regulatory near-term: enforcement continues to tighten.** The 01.07.2025 localization amendment (fines up to RUB 6M for a first offense) is part of a clear trajectory of expanding 152-FZ enforcement. The strategic implication: building *on* the RU-resident boundary now (rather than retrofitting later) is the lower-regret choice under any future tightening. The engineering posture in this document is robust to stricter enforcement without re-architecture.
_Source:_ [Lidings — tightened localization requirements from 01.07.2025 (fines up to RUB 6M)](https://www.lidings.com/media/legalupdates/localization_pd_update/) · [DLA Piper — Data Protection Laws in Russia](https://www.dlapiperdataprotection.com/index.html?t=about&c=RU) · [Securiti.ai — Russian Federal Law 152-FZ](https://securiti.ai/russian-federal-law-no-152-fz/)

**Medium-term (2–3 years): RU LLM capability and price competition.** The RU LLM market is consolidating around GigaChat + YandexGPT with active price competition (Sber's 3× cut) and grant programs. Tier-2 open-weight models (Qwen, DeepSeek) hosted on RU cloud are closing the quality gap with foreign frontier models for Russian-language tasks. The multi-tier `LlmPort` design means Zabot captures these gains by swapping adapters — no domain rework.

**Long-term option: fine-tuning and agentic expansion.** If coaching-quality data accumulates and Минцифры depersonalization rules permit, a RU-hosted fine-tune of an open-weight model (Tier 2 self-hosted) is a forward-compatible path — the hexagonal seam keeps it isolated. Agentic expansion (the bot taking structured actions, not just conversing) is the natural product evolution, and the deterministic control plane is precisely the safety substrate that makes agent fleets auditable at scale.

## Technical Research Methodology and Source Verification

**Research scope:** LLM provider selection, RU localization/hosting posture, profiling/mood-data consent model, and architectural rules — mapped to the Zabot AI BT and the clarifying letter's open questions (Q1–Q12).

**Data sources & verification approach:**

- **Primary legal/regulatory:** 152-FZ text (ч.5 ст.18, ст.10, ст.11, ст.12, ст.16, ст.19, ст.22), the 01.07.2025 amendment, and RU law-firm analyses (Lidings, Comply.ru, IC-TECH) — multi-source validation for every legal claim.
- **Provider/technical:** official Sber and Yandex developer docs, pricing pages, SDK repositories (ai-forever/gigachat, langchain-gigachat, yandexgpt-python), and current (2025–2026) RU tech journalism (Habr, vc.ru).
- **Architecture/engineering:** current practitioner and vendor sources on deterministic AI architecture, hexagonal/ports-and-adapters, HFSMs, transactional outbox, RLS, LLM memory tiers, guardrails, eval/LLM-as-judge, and LLMOps (Langfuse, LiteLLM, DeepEval, NeMo Guardrails).

**Confidence framework:**

- **High confidence:** provider capabilities/pricing/SDK availability, RU-cloud 152-FZ posture, the deterministic-vs-LLM boundary, hexagonal/HFSM/outbox/RLS/three-tier-memory patterns, observability tooling.
- **Medium confidence (flagged for ПДн counsel):** classification of mood/WHO-5 data as Art. 10 *special category*; Roskomnadzor register obligations under Art. 22; whether the traffic-light's effect on KPI crosses the Art. 16 "legally or similarly significant consequences" threshold; whether crypto-shredding satisfies the RF data-destruction obligation. _The engineering posture is sound under any interpretation; these do not block Phase 0–1._

**Limitations:** RU LLM pricing and model availability are moving fast (verified current as of research date, 2026-08-11); exact HFSM hysteresis thresholds (clarifying-letter Q6) remain an open product decision; final legal sign-offs require Russian data-protection counsel.

## Technical Appendices and Reference Materials

### Appendix A — Provider decision summary

| Tier | Models | Use case | Residency | Risk |
|---|---|---|---|---|
| 1 (Primary) | GigaChat, YandexGPT | Coaching narrative / "voice" | 100% RF | Zero |
| 2 (Augmentation) | Qwen 3, DeepSeek, Gemma (Yandex Cloud) | Structuring, analysis, reasoning | 100% RF (RU-hosted) | Zero |
| 3 (Optional) | OpenAI, Anthropic, Google direct | Anonymized analytics, non-PDn | Transborder (consent-gated) | Low, gated |

### Appendix B — Key open-source projects

- [ai-forever/gigachat](https://github.com/ai-forever/gigachat) & [langchain-gigachat](https://github.com/ai-forever/langchain-gigachat) — GigaChat SDK + LangChain integration
- [BerriAI/litellm](https://github.com/BerriAI/litellm) — multi-provider LLM gateway (routing/fallback/cost)
- [Langfuse](https://langfuse.com/self-hosting) — LLM observability, prompt mgmt, eval (self-hostable)
- [DeepEval](https://github.com/confident-ai/deepeval) — pytest-native LLM eval / LLM-as-judge
- [NeMo Guardrails](https://docs.nvidia.com/nemo/guardrails/) — input/output guardrails

### Appendix C — RU cloud/hosting options (152-FZ/FSTEC posture)

Yandex Cloud · Cloud.ru (Sber) · VK Cloud · Selectel · Timeweb Cloud · MTS Web Services — all publish in-country storage and 152-FZ/FSTEC certifications. Recommendation: Yandex Cloud or Cloud.ru (IAM, KMS, logging, explicit PDn-protection services; Yandex co-locates the YandexGPT endpoint).

## Technical Research Conclusion

The technology-stack decision for Zabot AI can be made now, on a compliant footing, with high engineering confidence. The multi-tier RU-LLM strategy behind a deterministic control plane and hexagonal ports resolves the clarifying-letter questions on localization, provider choice, and the profiling/mood-data consent model simultaneously — and is fundable through the Yandex Boost AI grant for the entire pilot window. The remaining open items (HFSM thresholds; three medium-confidence legal sign-offs) are scoped, non-blocking, and assigned to the right deciders (product owner; ПДн counsel).

**Next steps:**

1. Approve the multi-tier RU-LLM + deterministic-engine stack as the project's technical direction.
2. Apply for the Yandex Cloud Boost AI grant.
3. Kick off **Phase 0** (≤2 wk): build and unit-test the deterministic engine + HFSM on synthetic data; stand up one `LlmPort` adapter behind the depersonalization gateway; prove the compute→paraphrase→validate loop.
4. Engage ПДн counsel in parallel on the three flagged legal questions.

---

**Technical Research Completion Date:** 2026-08-11
**Research Period:** current comprehensive technical analysis (2025–2026 sources)
**Source Verification:** All facts cited with current sources; every legal claim multi-source validated.
**Technical Confidence Level:** High for engineering/stack; medium (flagged, counsel-bound) for the three legal classifications.

_This comprehensive technical research document serves as the authoritative reference for the Zabot AI technology-stack decision and provides strategic insights for compliant implementation under 152-FZ._
