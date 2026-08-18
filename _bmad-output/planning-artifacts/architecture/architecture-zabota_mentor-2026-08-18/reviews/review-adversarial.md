# Adversarial Review — Architecture Spine (Zabot AI Mentor, Stage 1)

- **Reviewer lens:** adversarial two-team construction. For each finding, two units one level down are hypothesized, each obeying every AD to the letter, yet producing incompatible systems.
- **Target:** `ARCHITECTURE-SPINE.md` (2026-08-18, status: draft)
- **Date:** 2026-08-18
- **Verdict:** **BLOCKED — not ready to descend.** Three blocking contradictions/gaps (B1–B3) must be closed with new or tightened ADs before any module team starts. Four HIGH findings should be closed in the same pass since they are one-sentence-to-one-paragraph AD amendments.

Severity tiers: **BLOCKING** (two compliant teams cannot integrate at all, or a legal gate is violated), **HIGH** (silent data/correctness divergence discovered only in production), **MEDIUM** (drift that costs rework or causes bounded incidents), **LOW** (ambiguity worth a sentence, no near-term failure).

---

## BLOCKING

### B1 — The spine itself violates AD-11: `llm` "(uses `messaging` rows)" vs "zero shared-table access"

- **Pair:** the `llm` module team and the `messaging` module team.
- **Rules each followed:**
  - `llm` team: the module table says `llm` owns "prompt assembly, LlmPort calls, template fallback — (uses `messaging` rows)". They read `messaging.outbox` rows directly to assemble prompts. Perfectly literal compliance with the spine's own ownership table.
  - `messaging` team: AD-11 — "zero shared-table access across modules; cross-module calls only through each module's published interface." They expose a published interface (`MessagingFacade.get_due_payloads()`) and consider direct table reads from any other module a build-breaking violation.
- **Divergence:** these two rules cannot both be satisfied. Either `llm` reads `messaging` tables (violating AD-11) or it goes through an interface that AD-11 mandates but the ownership table never names. Worse, AD-1 says the LLM-only-rephrases rule is "enforced structurally (payload shape)" — but no AD assigns ownership of that payload shape. `messaging` will define `outbox.payload JSONB` as template name + render vars; `llm` will expect a typed `facts` dict of bound variables for prompt slots. Both shapes are "the payload," neither team is wrong, and the structural enforcement of the honesty contract (AD-1) has no owner.
- **Failure mode:** integration deadlock at first joint milestone; or, if papered over by "just read the table," a permanent AD-11 breach in the module whose entire job is the riskiest external egress.
- **Fix (tighten AD-11 / new AD):** state that `llm` consumes `messaging` only via its published interface; define a single owned `RenderFacts` Pydantic model (the AD-1 "payload shape") — owned by `messaging` (the producer), versioned alongside config — containing exactly the pre-computed bound variables, message class, and fallback template. The `llm` module may not invent, derive, or round any field absent from `RenderFacts`.

### B2 — Two identity anchors, no owner of the join: `chat_id` (Identity convention) vs CRM entity IDs (AD-3)

- **Pair:** the `crm_sync` module team and the `profile` + `messaging` teams.
- **Rules each followed:**
  - `crm_sync` team: AD-3 — "The Mentor owns a canonical model (`Master`, `Client`, `Appointment`, `Visit`, `CheckLine`)"; they upsert mirror rows keyed by CRM master/client IDs, salon-scoped per AD-7.
  - `profile`/`messaging` teams: Consistency convention — "`chat_id` is the single user identity anchor." Profile rows, consent state, dialogue state, and Redis token buckets (AD-10, per-`chat_id`) are all keyed by `chat_id`.
- **Divergence:** nothing in the spine owns the mapping between a CRM `master_id` and a Telegram `chat_id`, or its lifecycle. Engines compute per CRM master; the dispatcher paces, caps, and arbitrates "per master per decision window" (AD-10) while sending to a `chat_id`. When a master changes Telegram account, links a second account, or a salon re-creates the master record in the CRM (Q1 explicitly leaves "stable entity IDs" open), the two keyspaces diverge silently.
- **Failure mode:** caps and arbitration counted against one key, sends executed against another: double sends, caps bypassed (5/shift becomes 10/shift across two chat_ids), consent recorded for one anchor and messaging executed under the other — a direct 152-ФЗ consent-integrity failure.
- **Fix (new AD):** name one canonical internal master ID; assign ownership of the `chat_id ↔ master_id` mapping table to exactly one module (`profile`); require every cross-module reference (outbox rows, engine scores, dedup keys, Redis keys) to carry the canonical ID; define merge/split behavior on anchor change.

### B3 — Depersonalization has no named owner: "stripped inside the RU zone" vs "GW → sanitized context only"

- **Pair:** the `llm` module team and the gateway/egress infrastructure team.
- **Rules each followed:**
  - `llm` team: AD-1 + AD-2 — they assemble the richest useful prompt from domain data behind ports and hand it to `LlmPort`, which routes through "the depersonalization gateway" per AD-5. Their reading: the gateway depersonalizes — that is what it is named for.
  - Gateway team: AD-5 — "direct identifiers stripped **inside** the RU zone, then forwarded via the egress point"; the structural diagram shows `GW →|"sanitized context only"| EP`. Their reading: the gateway *receives* already-sanitized context and merely forwards it; stripping is the caller's job, "inside the RU zone" means upstream of the gateway.
- **Divergence:** both interpretations satisfy the text. Neither team's audit convention covers the sanitization event: the Mutation convention's audit list is "config changes, consent events, export/delete requests, sync runs" — no LLM egress event, no record of what payload left, no proof it was clean.
- **Failure mode:** a salon master's name or a client's phone crosses the border to OpenAI; the launch gates (art. 12 consent + Roskomnadzor notification, AD-5) are violated on day one and nobody can even prove otherwise after the fact, because no audit record exists.
- **Fix (tighten AD-5):** name the component that strips (recommend: an explicit depersonalization step inside the `llm` adapter, *before* the gateway, with a domain-side allowlist of egressible fields); make every egress call an audit event recording payload hash + applied allowlist version; add a contract test asserting no direct identifier appears past the strip point (analogous to the fixture-CRM contract suite in AD-3).

---

## HIGH

### H1 — Mixed config versions inside one message: AD-6 stamps both the score row and the message row, and never says which one explains the text

- **Pair:** the `engines` team and the `messaging` dispatcher team.
- **Rules each followed:** engines compute a score/recommendation at time T under config V1 and stamp the score row with V1 (AD-6: "every score row stores the `config_version` used; engines read config by version at decision time"). The dispatcher sweeps the outbox at T+6h under config V2 and stamps the message row with V2 (AD-6: "every outbound message row ... stores the `config_version` used" — at *its* decision time).
- **Divergence:** the delivered message embeds numbers computed under V1 but is recorded as "computed under V2" (see the ER edge `CONFIG_VERSION ||--o{ MESSAGE_LOG : "computed under"` — false in this scenario). "Why did the bot say that" (the exact thing AD-6 exists to prevent) is unanswerable; replaying the message under the recorded version produces different figures.
- **Fix (tighten AD-6):** the message row's `config_version` must be the version under which every embedded figure was computed. Either the dispatcher passes a config_version *into* the engine call and the engine must use it, or the message row stores the referenced score/recommendation row IDs (provenance chain) rather than a bare version.

### H2 — Two clocks of freshness: `synced_at` vs source-event time; AD-9's ladder and backdated-suppression read different ones

- **Pair:** the `crm_sync` team and the `engines` team.
- **Rules each followed:** `crm_sync` upserts mirror rows and stamps them with its own poll timestamps (watermark per AD-3). Engines apply AD-9's tiers ("checks/sales ≤ 60 min...") and Level-2 `suppress_backdated_events` "on the trigger's source-data timestamp."
- **Divergence:** the spine never distinguishes *when the mentor fetched it* from *when the event happened in the CRM*. During a CRM outage a failed poll may still bump row timestamps; during recovery a backfilled poll writes old business events with new sync timestamps. One team computes data age from fetch time (data looks stale during outage, fresh after recovery — suppressing legitimate events); the other from event time (data looks fresh during a lagging mirror — praising a visit that didn't happen).
- **Fix (tighten AD-9):** mandate two explicit per-row timestamps — `source_event_at` (CRM-side truth) and `synced_at` (mentor-side) — and state which drives freshness tiers (recommend: `synced_at` for SLO/ladder) and which drives `suppress_backdated_events` (`source_event_at`).

### H3 — Traffic light has a scorer and a state owner but no assigned transition executor; the dispatcher reads a color nobody has committed

- **Pair:** the `engines` (scoring) team and the `profile` (state) team, with `messaging` as the victim.
- **Rules each followed:** the module table gives `profile` "traffic-light state" and the capability map gives §10 to "engines (scoring) + profile (state)". Hysteresis entry/exit thresholds live in config (AD-6). Engines, being "pure compute," emit raw scores and a *recommended* transition; `profile` stores the current color and — per its ownership of "state" — applies hysteresis on write. Alternatively (same compliance): engines apply hysteresis themselves and publish the committed color; `profile` merely persists what it is told.
- **Divergence:** both builds obey the spine; in one, hysteresis is applied twice (or zero times, each side assuming the other); in both, the cadence mismatch is unaddressed — engines recompute on their own schedule while the dispatcher's caps depend on "lower on yellow/red" (AD-10) at sweep time.
- **Failure mode:** dispatcher paces against a stale color — full-rate messaging to a red master, exactly the spam scenario AD-10 exists to prevent; or a double-applied hysteresis that never exits red, triggering the minimum-frequency path forever.
- **Fix (tighten AD-10/new sentence in AD-1 or a new AD on state mutation):** one rule — every stateful entity has exactly one owning module, and only the owner mutates it through one named path; specifically: engines publish score + recommended transition; `profile` owns hysteresis application and the committed color; the dispatcher must read the committed color via `profile`'s interface at decision time (never a cached engine inference).

### H4 — Erasure vs mirror reconciliation: delete requests vs periodic snapshot re-upsert — deleted PDn resurrects

- **Pair:** the `profile`/audit side (serving export/delete requests per the Mutation convention) and the `crm_sync` team.
- **Rules each followed:** profile records the delete request as an audit event (Mutation convention: "export/delete requests" are audit events) and erases PDn it owns. `crm_sync` runs "deletes reconciled by periodic snapshot" (AD-3) and upserts "idempotent by natural key" (AD-12) — its snapshot still contains the client's name, phone, visit history, because the CRM has not been told to erase anything.
- **Divergence:** no AD defines erasure propagation to the `crm_mirror` schema or to the CRM itself. The mirror is legally PDn in the RU zone (AD-5 lists "CRM mirror" among PDn), so 152-ФЗ erasure must reach it — but AD-3's snapshot reconciliation will resurrect every erased row on the next run unless the erasure writes a tombstone the sync respects.
- **Fix (new AD or amend AD-3/AD-5):** erasure requests produce tombstones in `crm_mirror` keyed by canonical ID (ties to B2) that survive snapshot reconciliation and suppress re-ingestion; erasure is an audit event that includes which schemas/rows were purged.

### H5 — Unstable CRM entity IDs (open Q1) silently void AD-12's idempotency for the reconciliation loop

- **Pair:** the `crm_sync` team and the `engines` (recommendation/outcome reconciliation) team.
- **Rules each followed:** `crm_sync`, told "idempotent by natural key" (AD-12) and facing a CRM without stable IDs (Q1 open), derives composite natural keys (client name hash + local time + amount). Engines reconcile recommendation outcomes to `Visit`/`CheckLine` "naturally idempotent per visit" (AD-12) — assuming the visit they saw yesterday is the same row today.
- **Divergence:** an edited appointment (time shifted, amount corrected) re-keys as a new visit. Reconciliation double-counts, praises the wrong outcome, or never closes a recommendation loop — corrupting the one feedback signal the product learns from, with no error anywhere.
- **Fix (tighten AD-12):** define the natural-key namespace per entity in the spine (owner: `crm_sync`, published as part of its interface), require reconciliation keys to reference `crm_sync`-published stable surrogate IDs assigned at first ingestion, and state that re-keyed source rows map to the same surrogate via the published key.

---

## MEDIUM

### M1 — Outbox natural key is undefined; engine trigger instances and outbox rows dedupe on different keys

- **Pair:** `engines` (trigger/recommendation emission) and `messaging` (dispatcher).
- **Rules followed:** engines make recommendation rows idempotent by their key (e.g. `appointment_id + trigger_type`); the dispatcher writes outbox rows idempotent "by natural key" (AD-12) — of the *message*, e.g. `master + message_class + local date`. AD-10's "losers deferred to a later sweep" re-evaluates triggers that already emitted.
- **Divergence/failure:** the same logical message sent twice (two engine instances → two outbox rows with distinct message-level keys) or two legitimately different messages deduped into one. Deferral also has no owner for attempt counts or max-defer lifetime: a quiet-hours + freshness-deferred row can ping-pong every sweep indefinitely; only the "oldest pending outbox" alert eventually notices.
- **Fix:** AD-12 should name the outbox natural key as derived from the originating decision row ID (1 decision row → ≤1 outbox row per channel), and AD-10/AD-4 should cap deferrals with a terminal state.

### M2 — "Write less often": explicit master preference has two plausible homes

- **Pair:** `messaging` (dialogue state, per module table) and `profile` (consent/preferences state).
- **Rules followed:** AD-10 says the explicit request "applies immediately and overrides model inferences"; the ignore-rate rule needs `message_log` (messaging) joined to preferences. Each team stores the preference in the schema it owns.
- **Divergence/failure:** the dispatcher reads one store, onboarding writes the other; the 2-week ignore-rate computation reads a third join nobody owns. Worst case: master says "write less," the cap applies, then a deploy/migration rebuilds dialogue state and the preference silently reverts — a trust-destroying, arguably consent-adjacent regression with no audit trail.
- **Fix:** one sentence in AD-10 assigning preference state to `profile` (it is consent-adjacent, thus auditable per the Mutation convention), with `messaging` consuming via interface.

### M3 — Shift boundaries for the ≤5/shift cap are derived by whoever needs them first

- **Pair:** `messaging` (cap enforcement, AD-10) and `crm_sync`/`engines` (schedule data owners).
- **Rules followed:** caps are "per shift"; shifts come from CRM schedule rows stored UTC (AD-8), rendered local at decision time. No module is assigned shift derivation, so the dispatcher invents its own (first-to-last appointment? calendar day? calendar day in salon timezone?) while engines' period totals use another.
- **Divergence/failure:** cap counted per calendar day by the dispatcher but per worked shift by reporting — 8 messages on a double shift with no violation visible in either place.
- **Fix:** assign shift-window derivation to one module (recommend `engines` as pure compute, consumed via interface) and pin the definition in the config schema (AD-6) rather than in code.

### M4 — Arbitration requires expected-income per candidate; no AD defines the candidate contract between engines and dispatcher

- **Pair:** `engines` and `messaging` (dispatcher).
- **Rules followed:** AD-10 — "competing triggers resolve by expected-income priority"; AD-1 — all figures computed by deterministic engines. The dispatcher needs, per candidate trigger in the decision window, an `expected_income` figure — but the spine defines no candidate object, so the dispatcher either calls engines for it (interface undefined) or computes its own priority heuristic, which would violate AD-1's "every figure computed by a deterministic engine" (is a ranking weight a "figure"?).
- **Fix:** extend the B1 payload-contract fix: engines publish a `TriggerCandidate` (message class, expected income, deadline, source-data timestamps) as the dispatcher's only ranking input.

---

## LOW

### L1 — Redis keys are outside the salon-scoping rule

AD-7 scopes "every domain row"; Redis dedup/token-bucket keys are not rows, and nothing requires a salon/master prefix. Two teams pick `dedup:{chat_id}` and `dedup:{salon}:{chat_id}`. Harmless until chat_id collisions across bot instances. One sentence in AD-4 or AD-7.

### L2 — Fallback events are not recorded anywhere

The Errors convention routes LLM failure → template fallback, but neither the audit taxonomy nor the outbox row records *which* path produced the sent text. Promptfoo golden coverage ("facts present, no invented numbers") cannot be measured in production, only in CI. Add a `rendered_by: llm|template` field to the message row.

### L3 — ER cardinality oddity

`RECOMMENDATION }o--|| APPOINTMENT : "pre-visit for"` makes every recommendation an appointment-tied pre-visit one, yet the cap and trigger model (AD-10, §12) clearly includes non-visit initiative messages. Cosmetic now, schema-shaping later.

---

## Summary of required AD changes

| Finding | Action |
| --- | --- |
| B1 | Tighten AD-11 + new payload-contract clause (owned `RenderFacts` model) |
| B2 | New AD: canonical master ID + owned `chat_id ↔ master_id` mapping |
| B3 | Tighten AD-5: named strip component, egress audit events, egress contract test |
| H1 | Tighten AD-6: provenance chain / config version flow into engine calls |
| H2 | Tighten AD-9: `source_event_at` vs `synced_at` semantics |
| H3 | New clause: one state owner per entity, named transition path for traffic light |
| H4 | New clause: erasure tombstones survive snapshot reconciliation |
| H5 | Tighten AD-12: natural-key namespaces + ingestion-assigned surrogate IDs |
| M1–M4 | One-sentence amendments to AD-12/AD-10/AD-4 and the shift definition in AD-6 |
