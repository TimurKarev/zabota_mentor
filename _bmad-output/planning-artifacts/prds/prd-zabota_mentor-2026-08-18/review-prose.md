# Prose Editorial Review — PRD & Addendum (Zabot AI Mentor, Stage 1)

**Reviewer:** bmad-editorial-review-prose
**Date:** 2026-08-23
**Scope:** prd.md (339 lines) + addendum.md (103 lines)
**Mode:** Prose only — clarity, consistency, phrasing, voice, RU/EN mixing. No requirement meanings were changed.

---

## Verdict

**Approve with prose revisions.** The document is well-structured and mostly clear, but the 23.08 update introduced several dense, hard-to-parse paragraphs and a handful of terminology drifts that will slow first-read comprehension for engineers and reviewers. None of the issues affect requirement semantics; all are fixable with rewording, sentence splitting, or term standardization.

---

## 1. Inconsistent Terminology (highest priority)

### 1.1 "scheme" vs "plan" vs "goal" vs "motivation plan"

FR-7.1 (line 197) carefully defines **Goal (цель)** = owner-set plan in Zabot, and the glossary (line 331) defines **Motivation plan (план мотивации)** as the Stage-1 plan types. Despite this, the word **"scheme"** appears as a synonym in several places, creating ambiguity about whether "scheme" means the same thing as "plan" or refers to the deferred constructor:

| Location | Text | Issue |
|---|---|---|
| Line 66 | "The 5-type **motivation-scheme** constructor" | Introduces "scheme" as a compound term |
| Line 182 (FR-5.4) | "nearest money lever of the salon's **scheme**" | Should be "plan" per FR-7.1; "scheme" is not a defined term |
| Line 198 (FR-7.2) | "5-type **scheme** constructor" | Drops "motivation-" prefix |
| Line 200 (FR-7.4) | "No **scheme** constructor" | Same |
| Line 280 (OQ-5) | "5-type **scheme** constructor" | Same |
| Addendum A.6 (line 52) | "supersedes BRD §11.2 **constructor**" | Uses bare "constructor" |
| Addendum A.8 (line 70) | "Generic **motivation-scheme** rule engine" | Yet another variant |

**Recommendation:** Pick one term for the deferred feature — "motivation-plan constructor" (matching the glossary) — and use it everywhere. Replace "salon's scheme" in FR-5.4 with "salon's motivation plan." The BRD's original "схема мотивации" can be noted once in FR-7.1 as the BRD's term, then the PRD's chosen term used consistently.

### 1.2 "avg check" / "average check" / "avg-check"

Three orthographic variants for the same metric:

- "average check" — line 31, line 39 (first occurrence in GM-1)
- "avg check" — line 39 (GM-1, same bullet as "average check"), line 142
- "avg-check" — line 85, line 199, line 331 (glossary, hyphenated as adjective)

**Recommendation:** Use "average check" as the noun, "avg-check" as a compound adjective ("avg-check plan"). Standardize GM-1 (line 39) which currently uses both forms in the same line.

### 1.3 "psychotype" vs "motivational type" vs "psychological profile"

FR-2.1 (line 148) defines the term as **"motivational type"**. The glossary does not list "psychotype." Yet:

- Line 159 (FR-3.1): "psychotype tone"
- Line 171 (FR-4.4): "master's psychotype"
- Line 179 (FR-5.1): "psychotype tone"

"Psychological profile" (line 97, line 144, line 155) is used to mean the *whole* profile (type + scales), which is correct and distinct. But "psychotype" as a shorthand for "motivational type" is undefined and could be read as a different concept.

**Recommendation:** Either add "psychotype" to the glossary as an informal synonym for "motivational type," or replace all three occurrences with "motivational type."

### 1.4 "CRM/Zabot" vs "Zabot/CRM" — order inconsistency

- "Zabot/CRM" — lines 66, 200, 258
- "CRM/Zabot" — lines 213, 231

Both mean the same source system. **Recommendation:** Pick one order and use it throughout. Since the direction is always "CRM/Zabot → agent," leading with "CRM/Zabot" reads more naturally with the arrow.

### 1.5 "owner-confirmed 23.08" date format

Mostly "23.08" but occasionally "23.08.2026" (lines 80, 94, 144). Minor, but in a document this dense, consistency reduces cognitive load. **Recommendation:** Use "23.08.2026" on first occurrence per section, "23.08" thereafter — or just pick one.

---

## 2. Hard-to-Parse Sentences (23.08 update density)

### 2.1 FR-1.5 (line 144) — single 12-line paragraph

This FR packs consent definitions, revocation logic, the aggregated-profile definition, the PDn operator clause, and the Roskomnadzor filing into one unbroken paragraph with six parenthetical insertions. The final two sentences are the densest:

> "PDn operator = the service's legal entity **[уточнить: наименование юрлица-оператора ПДн]**; the salon is an independent PDn operator of its clients — the agent processes client data on commission (ч. 3 ст. 6 152-ФЗ) per a commission-processing clause in the salon contract. Roskomnadzor notification filed before pilot launch."

**Recommendation:** Split FR-1.5 into sub-items (FR-1.5a consent model, FR-1.5b revocation, FR-1.5c operator/legal). The legal-entity clause is duplicated verbatim in C-1 (line 256) — consider defining it once and cross-referencing.

### 2.2 FR-6.3 (line 191) — threshold sentence

A single sentence encodes yellow entry, yellow exit, red entry, red exit, minimum stays, and calibration guidance, all separated by semicolons and parentheticals:

> "yellow entry < 60 three days running (or tone < 0.4 at ≥ 0.7 confidence), exit ≥ 70 held 3 days; red entry < 40 for 7 days (or burnout markers at ≥ 0.8 confidence + output drop > 20% at same booking over 2 weeks), exit ≥ 55 held 7 days; min stay 3 / 7 days."

**Recommendation:** Convert to a compact table (status | entry condition | exit condition | min stay) or split into two sentences (one per color). The calibration guidance is already a separate sentence and is fine.

### 2.3 FR-7.6 (line 202) — corridor rules paragraph

This FR is 8 lines of continuous text covering: attainment probability, corridor deviation, raise step, tactical lowering floor, the Zabot-plan ceiling, the plan-below-actual case, and movement rules. Each rule is clear individually, but the paragraph has no visual breaks.

**Recommendation:** Split into labeled sub-clauses (corridor, ceiling, movement rules) or use a short bullet list within the FR. No semantic change needed.

### 2.4 FR-11.3 (line 229) — degradation ladder with retroactive-praise exception

The Level 2 + Recovery section chains four em-dash clauses:

> "missed event messages are never sent retroactively — folded into shift/period totals — with one exception (owner-confirmed 23.08): praise for a successful recommendation may be sent late, within 60 min but no later than the end of the same shift; this is the most valuable reinforcing message, better late than never."

**Recommendation:** Break after "folded into shift/period totals." Start a new sentence: "One exception (owner-confirmed 23.08): praise for a successful recommendation may be sent late — within 60 min and no later than the end of the same shift — because this is the most valuable reinforcing message; better late than never."

### 2.5 FR-11.5 (line 231) — sync mechanism

Another long paragraph with three parentheticals and two em-dash asides. The phrase "unverified, marked as such" is compact but requires a double-take.

**Recommendation:** Split into: (1) primary channel, (2) polling fallback, (3) nightly reconcile, (4) direction constraint. The "unverified" caveat can stay inline if the sentence is shorter.

---

## 3. Awkward Phrasing

### 3.1 UJ-1, step 2 (line 110) — contradictory "because"

> "full script because Марина's sales-confidence scale allows thesis-only, but this cross-sell is new to her."

On first read this says "full script **because** she allows thesis-only," which is contradictory. The intended logic is: her scale *would normally* allow thesis-only, **but** because the cross-sell is new, a full script is given.

**Recommendation:** "a full script — even though Марина's sales-confidence scale would normally allow thesis-only — because this cross-sell is new to her."

### 3.2 Line 97 — "disclosed to no owner"

> "Because the psychological profile is disclosed to no owner, its shared nature creates no conflict of interest."

"Disclosed to no owner" is grammatically valid but reads awkwardly. **Recommendation:** "Because the psychological profile is not disclosed to any owner…"

### 3.3 Line 97 — abrupt parenthetical

> "two independent work contexts (goals, bar, metrics, recommendations, reports — separate)."

The trailing "— separate" after a list inside parentheses is redundant and abrupt. **Recommendation:** "two independent work contexts — goals, bar, metrics, recommendations, and reports are all separate."

### 3.4 Line 50 (GM-8) — "inverse ignore-rate"

> "share of messages answered / conversational engagement rate, and inverse ignore-rate"

"Inverse ignore-rate" is technically clear but reads as jargon. Since ignore-rate is itself a derived metric, "inverse" layers derivation on derivation. **Recommendation:** "share of messages answered, conversational engagement rate, and ignore-rate (lower is better)."

### 3.5 Line 246 (FR-13.4) — subtle distinction

> "not 'communication never stops' but 'communication never stops on the AI's initiative' — only the master can stop it."

The distinction between "communication never stops" and "communication never stops on the AI's initiative" is subtle and easy to misread. **Recommendation:** "the AI never stops communicating on its own initiative — only the master can stop it. (This corrects BRD §2's 'communication never stops.')" This makes the directionality explicit.

---

## 4. Russian / English Mixing

### 4.1 Placeholder tags — inconsistent language

The `[уточнить]` tag is Russian throughout (lines 144, 198, 202, 256, 285, 286, 287), but one placeholder is in English:

- Line 198: "[уточнить: **content of §11.3/§11.5 corrections pending scheme-constructor removal**]"

**Recommendation:** Standardize placeholder language. Either keep all `[уточнить]` content in Russian (matching the tag) or all in English. Given the document is English, English content inside the tag is more readable: "[уточнить: §11.3/§11.5 correction content, pending constructor removal]".

### 4.2 Inline Russian terms — mostly fine, two cases worth glossing

The pattern of giving the Russian term in parentheses on first use (цель, планка, светофор состояния) is consistent and helpful. Two cases lack a first-use gloss:

- Line 66: "средний чек, общая выручка" — appears without English equivalents. The English forms ("average check," "total revenue") are used elsewhere. **Recommendation:** "(average check, total revenue)" on first use.
- Line 256 / line 144: "ч. 3 ст. 6 152-ФЗ" and "ч. 5 ст. 18" — statutory references are fine as-is for a Russian legal context, but "ч. 3 ст. 6" could get a one-time gloss: "(Part 3, Art. 6)" for non-Russian-readers on the team.

### 4.3 Product name (line 10)

> "ИИ-помощник мастера Zabot — proactive personal AI coach…"

The Russian product name followed by an English gloss is a reasonable bilingual convention. No change needed, but if the team works in English, consider leading with the English and parenthesizing the Russian.

---

## 5. Passive Voice (minor, selective)

The document is mostly active, which is good. A few passive constructions reduce directness:

| Line | Text | Suggestion |
|---|---|---|
| 92 | "honest screening answers are not possible" | "honest screening answers become impossible" |
| 140 | "consent capture is a first-class step" | "the system treats consent capture as a first-class step" |
| 144 | "Without consent (1) the service is not activated" | "Without consent (1), the service does not activate" |
| 229 | "missed event messages are never sent retroactively" | Acceptable — the passive emphasizes the messages, which is the point |

These are minor; none impede comprehension.

---

## 6. Jargon Stacking

Two cases where config/legal jargon is stacked into a single noun phrase:

- Line 61: "config-defined pilot-calibration deliverable" — three modifiers on one noun. **Recommendation:** "a deliverable: numeric targets calibrated with the owner at pilot start and reviewed at pilot end."
- Line 252 (FR-14.3): "Config-seed deliverables at pilot start" — fine in context (FR list), but the body could say "At pilot start, the following config seeds are delivered:" for readability.

The architecture jargon in Addendum A.8/A.9 (Policy Enforcement Point, anti-corruption layer, SKIP LOCKED, transactional outbox) is appropriate for that section's audience and needs no change.

---

## 7. Minor Consistency Items

- "Traffic light" capitalization: section header "Traffic Light" (line 187), mid-sentence "Traffic light" (line 190), glossary "Traffic light" (line 335). **Recommendation:** lowercase "traffic light" everywhere except the section header.
- "pay period" vs "period": "pay period" on first use per section, "period" thereafter is acceptable. No change needed, but a one-line note in the glossary ("period = pay period unless otherwise stated") would help.
- Line 109: "3–4 touches per shift" vs line 159 "touch frequency" vs line 27 "touches per shift" — "touch" and "touches" for message interactions is consistent internally but could be glossed once: "touch (initiative message)."

---

## Summary of Recommended Edits (by priority)

| # | Priority | Type | Locations |
|---|---|---|---|
| 1.1 | High | Terminology: scheme→plan | Lines 66, 182, 198, 200, 280; Addendum A.6, A.8 |
| 1.2 | Medium | Terminology: avg check forms | Lines 39, 85, 142, 199, 331 |
| 1.3 | Medium | Terminology: psychotype | Lines 159, 171, 179 |
| 2.1 | High | Split FR-1.5 | Line 144 |
| 2.2 | High | Split FR-6.3 thresholds | Line 191 |
| 2.3 | Medium | Split FR-7.6 corridor | Line 202 |
| 2.4 | Medium | Split FR-11.3 recovery | Line 229 |
| 3.1 | High | Fix contradictory "because" | Line 110 |
| 4.1 | Medium | Standardize placeholder language | Lines 144, 198, 202, 256, 285–287 |
| 1.4 | Low | CRM/Zabot order | Lines 66, 200, 213, 231, 258 |
| 1.5 | Low | Date format consistency | Throughout |

**No requirement meanings were changed or are proposed to change.** All recommendations are rewording, splitting, or standardization.
