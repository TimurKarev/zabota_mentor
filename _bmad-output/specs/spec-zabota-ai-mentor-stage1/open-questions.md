# Open Questions — Zabot AI Mentor, Stage 1

> The 8 architecture-spine open questions (OQ-1, OQ-3, OQ-6, OQ-10, OQ-11, OQ-12, OQ-13, OQ-14) plus 2 PRD-level open questions (OQ-7, OQ-9). `[уточнить]` markers and owners preserved verbatim from the spine memlog and the Team Q&A v2.1. These are gaps a human must close before the named downstream gate; the spec does not invent answers.

## Launch gates

| ID | Question | Gate | Owner |
| --- | --- | --- | --- |
| **OQ-1** | **[narrowed 23.08]** Sync mechanism decided (AD-3: Zabot webhooks + REST polling + nightly full reconcile, read-only). Remaining: verify the Zabot API field surface — plans, checks, bookings, webhooks (team item 1). Webhook availability is **unverified, marked as such** until confirmed. | **M1** (real CRM adapter); FR-11 | Zabot owner |
| **OQ-3** | **[partially resolved 23.08]** 4-consent model + revocation + aggregated-profile definition confirmed (AD-17). Remaining: PDn retention periods (interact with 152-ФЗ retention duties). | **Launch gate** (Roskomnadzor notification); FR-1, FR-12.2 | Owner + counsel |
| **OQ-11** | **[уточнить]** PDn operator legal entity name (AD-17, C-1). The service's legal entity is the PDn operator; the salon is an independent PDn operator of its clients; the agent processes client data on commission (ч.3 ст.6 152-ФЗ). | **Launch gate** (Roskomnadzor notification) | Owner + counsel |
| **OQ-6** | Egress mechanism: own foreign VM vs ruble-billed intermediary (intermediaries are unauthorized resellers outside OpenAI ToS — volatility/ToS risk) + priced model selection. The `LlmPort` hides the choice. | C-1 implementation + cost | Owner + tech |

## Engine-implementation gates

| ID | Question | Gate | Owner |
| --- | --- | --- | --- |
| **OQ-10** | **[уточнить]** Method for computing the ~60–70% attainment probability that defines the calculated adaptive bar (FR-7.6, AD-6 corridor). Candidate: linear projection of current trend + historical dispersion band. The corridor **shape** is fixed (±15% / +10% / −15%); only the probability **method** is open. | Bar-engine implementation detail (not the corridor shape) | Owner + tech |
| **OQ-14** | **[уточнить]** Two-salon master traffic-light CRM-signal aggregation. The traffic light is master-level (AD-7/AD-13) but the CRM-signal stream is per-work-context (salon-scoped). For a two-salon master the composite score must aggregate CRM signals across both work contexts — aggregation method open (per-salon normalization then combine? weighted by load share?). | Traffic-light engine detail, **two-salon case only** | Tech |

## Document gates

| ID | Question | Gate | Owner |
| --- | --- | --- | --- |
| **OQ-12** | **[уточнить]** BRD §11.3 and §11.5 corrections pending scheme-constructor removal (FR-7.2). Content to be defined for BRD v2.2. | BRD v2.2 release (not architecture) | Owner + PM |
| **OQ-13** | Telegram has no read receipts — engagement KPIs must be answered/ignored-based (GM-8); "share read" is explicitly **not** measurable in Stage 1. Flag to BRD owner. | GM-8 metric definition | BRD owner |

## PRD-level (not from the spine)

| ID | Question | Gate | Owner |
| --- | --- | --- | --- |
| **OQ-7** | Monetization / pricing / sales motion — out of PRD scope, must be decided before launch. | Go-to-market | Owner |
| **OQ-9** | Confidentiality aggregation rule specifics for owner-visible conclusions (FR-10.3) — the aggregate-vs-detail boundary, threshold-defined aggregation. `[ASSUMPTION]` a config-defined deliverable at pilot. | FR-10.3 | PM + counsel |
