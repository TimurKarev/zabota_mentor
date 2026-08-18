# Reconcile Review — Architecture Spine vs. Stage-1 Technical Research

**Reviewer role:** reconcile reviewer (research → spine fidelity)
**Date:** 2026-08-18
**Source research:** `_bmad-output/planning-artifacts/research/technical-stage1-reference-architecture-zabot-ai-mentor-research-2026-08-16.md`
**Subject:** `_bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md`
**Severity tiers:** BLOCKING (must fix before the spine is used) / HIGH (load-bearing distortion) / MEDIUM (dropped or untagged decision; fix in next pass) / LOW (minor omission or polish)

---

## Verdict

**PASS WITH FINDINGS — no BLOCKING issues.** The spine is a faithful distillation of the research on every headline decision: modular monolith with hexagonal boundaries, pipeline-not-agent, CRM ACL + watermark polling, Postgres-as-durability-backbone with outbox + SKIP LOCKED, two-zone 152-ФЗ residency, insert-only versioned config, freshness tiers and the two-way degradation ladder, dispatcher-owned arbitration/floors/pacing, salon-scoped tenancy, and the consolidated stack. One research invariant is weakened (HIGH-1), a handful of specifics appear beyond the research without `[ASSUMPTION]` tags (MEDIUM-1), and several ops-envelope items were dropped without trace (MEDIUM-2/3).

---

## Detailed findings

### HIGH

**HIGH-1 — Reproducibility invariant weakened: `prompt_version` dropped from message rows.**
Research (Data Architecture / Success Metrics / Appendix "Key tables"): every message reproducible from **(facts, config_version, prompt_version)** — stated as a 100%-coverage KPI, and the message log is explicitly specified to carry `config_version`/`prompt_version`. The spine's AD-6 states only: "Every outbound message row and every score row stores the `config_version` used," and the ER diagram (`CONFIG_VERSION ||--o{ MESSAGE_LOG`) carries no prompt-version relationship. Since the prompt library (psychotype fragments) is a versioned artifact per the research and the promptfoo golden set is a CI gate, reproducibility without `prompt_version` is incomplete — the owner's "why did the bot say that" query cannot reconstruct the wording.
**Fix:** extend AD-6 (and the ER fragment) to require `prompt_version` alongside `config_version` on every outbound message row.

### MEDIUM

**MEDIUM-1 — Beyond-research specifics without `[ASSUMPTION]` tags (AD-6, AD-8, AD-10).**
The following spine rules do not appear anywhere in the research document:
- AD-6: trigger offset "**pre-visit 30–60 min**" (research has only T-24h/T-2h);
- AD-8: quiet-hours "**default 21:00–9:00**";
- AD-10: caps "**≤2 on days off, lower on yellow/red**" (research states only ≤5 initiative messages/shift);
- AD-10: "master's explicit request ('write less often') **applies immediately and overrides model inferences**" (research has the ignore-detection loop and the intrusiveness KPI, not this override rule).

These may all be BRD §7.3/§5-derived (BRD is a declared spine source and AD-10 cites §7.3), but the research is the declared distillation source and these numbers/rules are not traceable to it. Either verify each against the BRD and cite the section, or tag `[ASSUMPTION]`.

**MEDIUM-2 — Canonical model diverges from the research: `Payment` dropped, `CheckLine` added.**
Research (ACL design): canonical model = `Master`, `Client`, `Appointment`, `Visit`, **`Payment`**. Spine (AD-3, Consistency Conventions, ER): `Master`, `Client`, `Appointment`, `Visit`, **`CheckLine`** — `Payment` is gone and `CheckLine` appears without note or tag. `CheckLine` is a sensible entity for the §8.4 check-reconciliation loop, but the income/forecast engine (a research-quoted §11 core) needs payment records; whether CheckLine subsumes Payment in Zabot's data is exactly the kind of CRM-surface assumption (Q1) that should be tagged.
**Fix:** tag the canonical entity set `[ASSUMPTION]` pending Q1, or restore `Payment` alongside `CheckLine`.

**MEDIUM-3 — DR/backup envelope dropped entirely.**
Research (Deployment and Operations Practices): managed backups + **PITR**, **RPO ≤ 15 min, RTO ≤ 4 h**, quarterly DR restore drill, runbooks per degradation mode and recovery path, degradation drills in M3. The spine's stack table and conventions carry none of this — no RPO/RTO, no backup posture, no DR drill anywhere (Deferred doesn't cover it either). For a system whose research pitches "PostgreSQL as the durability backbone," the recovery envelope is load-bearing.
**Fix:** one line in Stack or Consistency Conventions (e.g., "Backups: managed PITR; DR objective RPO ≤ 15 min / RTO ≤ 4 h, tested quarterly").

**MEDIUM-4 — LLM cost controls dropped.**
Research (Cost Optimization): response length caps in the LLM port, template fallback when spend budget trips, per-master daily token meter — described as "cost controls built in," with LLM spend the dominant cost and intermediary markup model-dependent (up to ~×4.3, correctly landed in Q4). The spine's `llm` module row and Deferred section carry none of these. Given research recommendation that model choice is "a first-order cost lever," at least the length-cap/budget-trip rules belong in AD-1 or the conventions table.

### LOW

**LOW-1 — CRM CSV-import fallback adapter dropped.** Risk row 1 mitigation ("`CrmPort` + fixture CRM; **CSV-import fallback adapter**") is only half-landed: AD-3 has the fixture CRM, Q1 has "historical exports for seeding," but the CSV fallback as an adapter path is gone. Add to Q1 or Deferred.

**LOW-2 — Vendor exit options (VK Cloud/Selectel) dropped.** Risk row 6 mitigation names documented exit options and container portability; the spine keeps containers but never names the second sources. One clause in Stack ("portable containers; VK Cloud/Selectel as exit options") restores it.

**LOW-3 — Telegram IP allowlisting dropped.** Research integration-security pattern: `secret_token` **plus IP allowlisting of Telegram's published ranges** on the gateway. The spine carries `secret_token` only (diagram + conventions).

**LOW-4 — E2E smoke test layer dropped.** Research's three-layer test strategy includes end-to-end smoke against a test bot (full loop incl. rate-limit pacing); the spine's test tree has `unit/ contract/ golden/` only. The "Environments" conventions row could carry it.

**LOW-5 — Arbitration priority factors narrowed.** Research: priority computed from (message class, expected-income value, **trigger freshness**); spine AD-10 says "expected-income priority" only. Minor, but the freshness factor is what makes deferral-to-later-sweep sensible.

**LOW-6 — Module/schema bookkeeping diverges slightly.** Research says **five** modules (`crm_sync, engines, messaging, llm, config`) and five schemas (`crm_mirror, profile, messaging, config, audit`); the spine says **six** modules (adds `profile`) and six schemas (adds `engines`). The additions are coherent (research's bounded contexts do include Master Profile), but `engines` as a schema contradicts "engines are pure functions" in the research. Either note the delta or drop the `engines` schema.

**LOW-7 — Misc omissions, acceptable at spine altitude but listed for completeness:** LISTEN/NOTIFY accelerator (optional by design); ADRs-in-repo-from-day-one recommendation; red-status escalation path (M3); per-region quiet-hours windows ("per region" qualifier dropped in AD-6); hysteresis 3/7-day minimum-stay values; owner-letter escalation vehicle; `~30 msg/s` global Telegram pacing (per-chat pacing landed); M0–M3 roadmap (presumably lives in a planning artifact, not the spine).

---

## Coverage check (requested areas)

| Area | Landed? | Notes |
| --- | --- | --- |
| Freshness tiers | Yes | AD-9: 60 min / 15 min / 24 h, three SLOs, per-class alerting — verbatim |
| Degradation ladder | Yes | AD-9: Level 1 labeled data + forecast suppression, Level 2 no-figures, post-recovery fold-not-backdate with `suppress_backdated_events`; quiet-hours defer and LLM template fallback in conventions |
| Trigger arbitration | Yes | AD-10 dispatcher-owned, expected-income wins, defer-or-merge; freshness factor narrowed (LOW-5) |
| Frequency floors | Yes | AD-10 disable ladder, money-class last, ≥70%/2-week ignore loop; extra untagged caps (MEDIUM-1) |
| Recommendation-engine rules | Yes | Capability map §8 row (candidates/filters/rank/1–3 cap), check-reconciliation loop in AD-12, deterministic per AD-1; exclusion-filter specifics left to BRD — acceptable |
| Config inventory | Mostly | AD-6 matches the research list except the untagged "30–60 min" addition (MEDIUM-1) |
| Deployment/ops envelope | Partial | Stack + 2-VM topology + SLO alerting landed; DR/RPO/RTO and cost controls dropped (MEDIUM-3/4) |
| Risk register mitigations | Mostly | Risks 2–5, 7, 8 fully landed (AD-5, AD-1, AD-10, AD-7, Q2/Q3); risk 1 CSV fallback and risk 6 exit options partially dropped (LOW-1/2) |
| Untagged invention | Some | MEDIUM-1 items, CheckLine (MEDIUM-2), `engines` schema (LOW-6) |

---

## Recommended actions (in order)

1. Add `prompt_version` to AD-6 and the ER fragment (HIGH-1).
2. Verify-or-tag the four beyond-research specifics (MEDIUM-1) and the canonical entity set (MEDIUM-2).
3. Restore DR/RPO/RTO and LLM cost-control lines (MEDIUM-3/4).
4. Sweep the LOW items opportunistically.
