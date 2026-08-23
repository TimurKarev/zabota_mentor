# Structural Editorial Review — PRD Zabot AI Mentor (Stage 1)

**Reviewer:** bmad-editorial-review-structure
**Date:** 2026-08-23
**Scope:** prd.md + addendum.md — structural cuts, reorganization, simplification. No requirement meaning or content changed.

---

## Verdict

**Approve with structural revisions.** The PRD is comprehensive and well-sourced, but the 23.08 update introduced significant redundancy (the same rule restated 4–8× across sections) and placement friction (F13 orphaned from F3, F9 referenced before it appears). A focused consolidation pass would cut ~15–20% of body text without losing any requirement.

---

## 1. Redundancy — same rule stated in multiple sections

### 1.1 "Read-only sync / no two-way sync" — 5 locations

Stated in: §2.3 (non-goals), FR-7.2, FR-11.5, A.7, A.8. The BRD §11.1 correction is also repeated in FR-7.2, FR-11.5, and A.8.

**Recommendation:** State the rule once in FR-11.5 (its natural home — CRM Integration). Replace all other occurrences with a single cross-reference: `(read-only — FR-11.5)`. Remove the BRD-correction note from FR-7.2; keep it only in A.10.1.

### 1.2 "2 Zabot plan types only, constructor → backlog" — 8 locations

Stated in: §2.3, FR-7.1, FR-7.2, FR-7.4, A.6, A.8, A.10.1, Glossary (Motivation plan + Tier rows).

**Recommendation:** FR-7.4 is the canonical statement. FR-7.1 and FR-7.2 should reference it rather than re-explain. §2.3 can keep a one-line non-goal. A.6 and A.8 are addendum context — acceptable, but A.8's second bullet repeats A.6 almost verbatim; merge into one. Glossary entries are fine as-is (that is their purpose).

### 1.3 FR-2.7 progress definition restated in FR-5.5 and FR-7.6

FR-2.7 defines progress (+5% or ≥95% retention, 2-week window, ≥80% load). FR-5.5 restates the full threshold inline. FR-7.6 restates it again as "sustained progress per FR-2.7 (≥ +5% or ≥95% retention over 2-week window at ≥80% load)."

**Recommendation:** FR-5.5 and FR-7.6 should say `(sustained progress per FR-2.7)` without re-quoting the thresholds. FR-2.7 is the single source of truth.

### 1.4 Cold start — FR-2.8 and FR-11.4

FR-2.8 defines cold-start behavior for a new master (observation mode period 1, bar from period 2, incomplete profiling fallback). FR-11.4 restates the same new-master rule and adds a cross-reference. FR-1.3 also touches onboarding cold start.

**Recommendation:** FR-2.8 is the canonical master-cold-start requirement. FR-11.4 should cover only the general entity-cold-start (new salon, new client) and cross-reference FR-2.8 for the master case instead of restating it. FR-1.3's cold-start sentence can be trimmed to `(cold start handling — FR-2.8)`.

### 1.5 "No correspondence quotes to owner" — 4 locations

Stated in: E-6 (§9.3), FR-6.5, FR-10.3, UJ-3 step 1.

**Recommendation:** FR-10.3 is the canonical requirement. E-6 is the ethics principle — keep but shorten to a cross-ref. FR-6.5 and UJ-3 can say `(no quotes — FR-10.3)`.

### 1.6 Telegram channel constraints — 3 locations

"No read receipts → engagement by answers/reactions" and "quiet hours guaranteed on send side" and "inline keyboards for screenings" each appear in GM-8, NFR-D, and C-2.

**Recommendation:** NFR-D is the canonical NFR. C-2 should state the channel choice and cross-reference NFR-D for the constraints. GM-8 can keep its one-line metric definition and cross-reference NFR-D.

### 1.7 Determinism / zero figure incidents — 5 locations

FR-9.1, FR-9.3, FR-9.4, NFR-A, CM-4, E-5 all restate "all figures deterministic, zero incidents."

**Recommendation:** FR-9.1–9.4 are the functional requirements (keep). NFR-A should be a one-line cross-reference to FR-9 rather than restating. CM-4 and E-5 are fine as metric/ethics anchors but can drop the parenthetical detail.

### 1.8 FR-7.2 and FR-7.4 near-duplicate

FR-7.2 and FR-7.4 both state: read plans from Zabot, no two-way sync, constructor deferred, agent computes derived values in calculation DB.

**Recommendation:** Merge into one requirement. FR-7.2 keeps the terminology + read-only + BRD-correction note; FR-7.4's "Stage 1 supports only 2 types" detail folds into FR-7.2 as a sub-point. Eliminates a full paragraph.

### 1.9 PDn operator [уточнить] — 4 locations

FR-1.5, C-1, OQ-3, OQ-11 all carry the `[уточнить: наименование юрлица-оператора ПДн]` placeholder plus the commission-processing clause.

**Recommendation:** State the PDn-operator + commission-processing detail once in C-1 (Compliance). FR-1.5 cross-references C-1. OQ-11 is the open question — keep. OQ-3 drops the duplicate text and cross-refs OQ-11.

---

## 2. Section ordering

### 2.1 F13 (Communication Floor / Pause / Opt-out) is orphaned from F3

F13 is logically a continuation of the Communication Engine (F3): FR-13.1 references FR-3.4 (disable ladder), FR-13.4 restates the communication-continuity principle. Currently F13 sits after F12 (Memory), separated from F3 by 9 feature groups.

**Recommendation:** Move F13 immediately after F3 (Communication Engine), or merge as F3.2 sub-section. This groups all communication-lifecycle rules together.

### 2.2 F9 (Determinism) is referenced before it appears

FR-9 is first referenced in FR-5.3 (shift totals — "computed deterministically (FR-9)"), FR-5.5, FR-7.6, FR-7.7 — all before F9 appears in document order. The reader encounters the determinism boundary concept 4 times before its definition.

**Recommendation:** Move F9 (Deterministic Money Math & LLM Roles) to immediately after F4 (Recommendation Engine) and before F5 (Coaching Cycles). This places the determinism boundary before the coaching features that depend on it.

### 2.3 F14 (Config) could be an appendix reference

F14 is referenced by nearly every feature group but sits at the end of the feature list. It is more of a cross-cutting concern than a feature.

**Recommendation:** Keep F14 in place but add a forward-reference in the F1–F14 section header: *"Behavioral parameters throughout are config-managed per F14."* This prevents the reader from assuming hard-coded values.

---

## 3. Verbose passages — tighten without information loss

### 3.1 FR-7.6 — 180-word single requirement

FR-7.6 packs corridor rules, movement rules, framing rules, and the [уточнить] note into one block. It is the longest single FR in the document.

**Recommendation:** Split into FR-7.6a (corridor: ±15%, +10%, −15%, cannot exceed plan), FR-7.6b (movement: raise on progress+consent, hold on stagnation, never raise on decline), FR-7.6c (framing: income terms, never punishment). The [уточнить] note stays on 7.6a. No content lost; readability improves sharply.

### 3.2 FR-1.5 — 160-word consent + legal block

FR-1.5 combines consent withdrawal mechanics, the aggregated-profile definition, and the PDn-operator / commission-processing legal detail.

**Recommendation:** Split consent-withdrawal mechanics (keep in FR-1.5) from the PDn-operator legal detail (move to C-1, cross-ref from FR-1.5). The aggregated-profile definition is already referenced from A.10.1 — does not need full restatement here.

### 3.3 FR-11.5 — 150-word sync mechanism

Combines webhook decision, REST polling, nightly reconcile, read-only direction, BRD correction, API verification status, and fixture-CRM mode.

**Recommendation:** Keep the mechanism decision (webhooks + REST + reconcile, read-only) in FR-11.5. Move the BRD-correction note to A.10.1. Move the fixture-CRM mention to §7 (Milestones) where it already appears. Trim the OQ-1 cross-reference to `(OQ-1)`.

### 3.4 FR-11.3 — 140-word degradation ladder + praise exception

The retroactive-praise exception (owner-confirmed 23.08) is buried inside the recovery paragraph.

**Recommendation:** Extract the praise exception into FR-11.3a (degradation ladder) and FR-11.3b (retroactive praise exception). One sentence each for the exception; it is currently 3 clauses packed into a parenthetical.

### 3.5 "(owner-confirmed 23.08)" tag — ~30 occurrences

The tag appears inline in nearly every FR and NFR, creating visual noise and breaking sentence flow.

**Recommendation:** Add a document-level note in the header: *"Requirements marked with ▸ were owner-confirmed 23.08.2026 (Team Q&A v2.1)."* Replace inline `(owner-confirmed 23.08)` with a `▸` marker. Alternatively, since the front matter already says `updated: 2026-08-23`, consolidate all 23.08 confirmations into A.10.1 (which already lists them) and drop inline tags entirely, keeping only cross-refs where a specific decision is surprising.

---

## 4. Structural issues from the 23.08 update

### 4.1 A.10.1 duplicates the PRD body

A.10.1 is a 20-line reconciliation log that re-lists every 23.08 change — but each change is already integrated into the PRD body (FR-1.5, FR-2.7, FR-2.8, FR-7.4, FR-7.6, FR-9.4, FR-9.5, FR-11.5, FR-13, NFR-F, C-1, C-2). The reader encounters the same information twice.

**Recommendation:** Rename A.10.1 to "Change log — 23.08.2026 update" and reduce to a table of `OQ/Item → FR reference → Status (resolved/obsolete/narrowed)`. Remove the prose explanations — they live in the FRs now.

### 4.2 OQ table mixes resolved and open items

The OQ table has 4 strikethrough (resolved/obsolete) items interleaved with 5 open items. This makes the open-question scan difficult.

**Recommendation:** Split into two sub-tables: "Open questions" (OQ-1, OQ-3, OQ-6, OQ-7, OQ-9, OQ-10, OQ-11, OQ-12) and "Resolved/obsolete (23.08)" (OQ-2, OQ-4, OQ-5, OQ-8). Or move resolved items to A.10.1 change log and keep only open items in §8.

### 4.3 FR-9.4 / FR-9.5 ruble-gate overlap

FR-9.4 (output validator) and FR-9.5 (ruble calculation gate) both describe the condition "no ruble figures without owner-entered remuneration rules." FR-7.7 also restates this.

**Recommendation:** FR-9.5 is the canonical ruble-gate requirement. FR-9.4 should cover only the output-validator mechanism (number matching, fail → not sent). FR-7.7 should cross-reference FR-9.5 for the ruble condition rather than restating it.

---

## 5. Minor structural notes

- **UJ-4 onboarding** references FR-1.1 and Addendum A.4 but is placed before the F1 feature group. Consider a forward-reference note in §4 header: *"User journeys reference feature groups defined in §5."*
- **Glossary (§11)** repeats the bar-corridor values (±15%, +10%, −15%) from FR-7.6. Glossary should define the term, not restate the parameter values — cross-ref FR-7.6.
- **E-7** lists all scientific models inline; A.1 has the full table. E-7 can be shortened to a cross-reference.
- **FR-3.2 and NFR-F** both define quiet-hours timezone. FR-3.2 says "master TZ (NFR-F)"; NFR-F has the full rule. FR-3.2 can drop the parenthetical and just say `(NFR-F)`.

---

## Summary of proposed cuts

| Area | Action | Est. words saved |
|---|---|---|
| Read-only sync (5→1) | Consolidate to FR-11.5 | ~80 |
| 2-plan-types (8→3) | Consolidate to FR-7.4 + §2.3 + A.6 | ~120 |
| FR-2.7 restated (3→1) | Cross-ref from FR-5.5, FR-7.6 | ~60 |
| Cold start (3→1) | Cross-ref from FR-11.4, FR-1.3 | ~70 |
| No-quotes (4→1) | Cross-ref from E-6, FR-6.5, UJ-3 | ~50 |
| Telegram constraints (3→1) | Cross-ref from C-2, GM-8 | ~60 |
| FR-7.2/FR-7.4 merge | Single requirement | ~80 |
| PDn operator (4→1) | Consolidate to C-1 | ~70 |
| FR-7.6 split | Reorganize (no cut, but readability) | 0 |
| FR-1.5 split | Move legal to C-1 | ~40 |
| FR-11.5 trim | Move BRD note + fixture to A.10.1/§7 | ~40 |
| A.10.1 → change-log table | Remove prose | ~150 |
| OQ table split | Move resolved to A.10.1 | ~40 |
| Inline 23.08 tags (30→header note) | Replace with marker | ~60 |
| E-7, Glossary, FR-3.2 minor | Cross-refs | ~40 |
| **Total** | | **~960 words (~15% of body)** |

---

*End of review. No edits made to prd.md or addendum.md.*
