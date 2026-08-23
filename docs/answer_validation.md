
These are pandoc list-break artifacts and render as literal text in GitHub/standard CommonMark. They also break the numbered-list continuity (the second `1.` should be `2.`). **Action:** remove all `{=html}` blocks and renumber list items sequentially in «Сводка открытых пунктов» and in Ответ на вопрос 5.

---

## P1 — Should fix (clarity & actionability)

### P1-1. Access matrix uses pandoc grid-table syntax (lines 100–135)

The matrix is rendered with column-rule dashes — pandoc `grid` format, not CommonMark. It will not render as a table in GitHub, most IDE markdown previewers, or `glow`/`mdcat`. Given this is the single most important artifact for the dev team, it must render everywhere. **Action:** convert to a pipe-table (`| Данные | Мастер | Собственник |`) or ship it as a separate file referenced here.

### P1-2. «Сводка открытых пунктов за нами» mixes owners

«За нами» is ambiguous (PO? team? joint?). The three items have three different owners:
1. `[уточнить]` юрлицо-оператор ПДн → **product owner**
2. Калибровка порогов по итогам пилота → **joint, post-pilot**
3. Проверить API Zabot / подтвердить архитектуру расчётной БД → **dev team**

**Action:** split into «За собственником», «За командой», «Совместно после пилота».

### P1-3. Webhook channel is stated as primary but unverified

Ответ на вопрос 2 names *"вебхуки Zabot по событиям"* as the **основной канал**, but Сводка item 3 admits the team must still *"проверить по API Zabot фактический состав доступных полей (… вебхуки)"*. So the primary integration path is contingent on an unverified assumption. **Action:** mark the webhook statement as «предполагаемый основной канал, подтверждается проверкой API (см. Сводку п. 3)» so the dev team treats it as a hypothesis, not a given.

### P1-4. Расчётная планка algorithm is underspecified

Ответ на вопрос 10 defines the corridor (±15%, +10%/period, −15% floor) clearly, but the **расчётная планка** itself is defined only as *"прогноз по фактической динамике мастера в логике «сложно-но-достижимо» (вероятность достижения ~60–70%)"*. An engineer cannot implement «вероятность достижения ~60–70%» without a method. **Action:** either point to a concrete algorithm (e.g. linear projection of current trend + historical variance band) or mark as `[уточнить: метод расчёта вероятности достижения]`.

### P1-5. Question numbering in Часть 1 is unexplained

«Вопрос 1-2», «Вопрос 2-4», «Вопрос 4-1», «Вопрос 6», «Вопрос 7-1» — the hyphenated scheme is not decoded. Presumably «letter-question.subquestion», but a reader without the original letter cannot tell. **Action:** add one line in the preamble explaining the numbering, or relabel as «Письмо, вопрос N (подтверждение решений команды)».

### P1-6. Document lacks its own version/date/status header

The БТ carries «Версия 2.1 · 13.08.2026». This Q&A doc has no header, date, author, or status field. Given that its decisions **supersede** БТ v2.1 in several places (and will produce БТ v2.2), the reader needs to know which doc is newer and whether it's draft or final. **Action:** add a one-line header (version, date, status: «draft / awaiting team confirmation»).

---

## P2 — Nice to have (precision & polish)

### P2-1. БТ cross-references are all valid — good

Every cited section was verified against `zabot_ai.md`:

| Ref in Q&A | БТ section | Exists |
|---|---|---|
| §3 | УЧАСТНИКИ | ✅ |
| §5.2 | Из CRM (через Zabot) | ✅ |
| §6.5 | Динамическое профилирование | ✅ |
| §8.4 | Петля обратной связи | ✅ |
| §9.2 | Сценарии в течение смены | ✅ |
| §9.4 | Форсирование и сброс темпа | ✅ |
| §10 / §10.1 / §10.2 / §10.3 | Эмоциональный мониторинг | ✅ |
| §11.1 / §11.2 / §11.4 / §11.5 | Цели, планки и премирование | ✅ |
| §13.1 | LLM-провайдер и ПДн | ✅ |
| §14 | Эскалация и отчёт | ✅ |

No broken references. **Suggestion:** use a consistent style — the doc mixes «раздел 3», «раздел 11.2», «8.4», «§11.1» (only in your prompt, not in the doc). Pick one («раздел N» or «§N») and apply throughout.

### P2-2. БТ §3 and §13.1 open items — fully covered

БТ §3 flags «Модель доступа ролей к данным и изоляция» as open → covered by Ответ на вопрос 1 (matrix + isolation). БТ §13.1 flags «модель согласий / отзыв / оператор ПДн» as open → covered by Ответ на вопрос 4. Good completeness on the БТ's own open list.

### P2-3. Action items on БТ are scattered — consider a consolidated list

The doc issues several implicit БТ-edit instructions that are easy to lose:
- §2 Принцип 4: rephrase to «коммуникация не прекращается по инициативе ИИ» (Ответ 9)
- §8.4: add cross-reference to §10 (Ответ 8)
- §11.1: strike «двусторонняя синхронизация» (Ответ 2)
- §11.2: move конструктор to backlog (Ответ 5)
- §11.3, §11.5: **need correction** (see P0-1 — currently missing)

**Action:** add a short «Требуемые правки БТ» checklist at the end so the БТ editor has a single worklist.

### P2-4. «Похвала за сработавшую рекомендацию» exception (Ответ 2-4) needs a freshness bound

The exception allows sending delayed praise «до конца той же смены», but the freshness table says чеки/продажи ≤ 60 min. If the shift ended >60 min ago but «до конца смены» hasn't passed (long shift), the two rules can conflict. **Action:** clarify whether the shift-end exception overrides the 60-min freshness rule, or tighten to «в течение 60 мин, но не позднее конца смены».

### P2-5. «Отзыв (3) переводит память в режим „только агрегированный профиль"» — undefined term

Ответ на вопрос 4 introduces «агрегированный профиль» as a memory mode, but neither БТ §13 nor this doc defines what fields survive aggregation. **Action:** add a one-line definition or cross-ref to the profile model in §6.1/§6.3.

---

## Open-items ledger (reconciliation)

| Item | Status in doc | Verdict |
|---|---|---|
| `[уточнить]` наименование юрлица-оператора ПДн | Listed in Сводка п. 1 | ✅ Tracked |
| Калибровка порогов (свежесть, светофор, α, коридор) | Listed in Сводка п. 2 | ✅ Tracked |
| Проверка API Zabot + подтверждение архитектуры расчётной БД | Listed in Сводка п. 3 | ✅ Tracked |
| Метод расчёта «вероятности достижения ~60–70%» для расчётной планки | **Not marked** | ⚠️ Add as `[уточнить]` (P1-4) |
| Правки БТ §11.3 и §11.5 | **Not listed** | ⚠️ Add (P0-1) |
| Подтверждение наличия вебхуков Zabot | Implicit in Сводка п. 3 | ✅ But see P1-3 |

---

## What's done well

- **Вводная** is excellent — states the principle (read-only Zabot, separate agent DB) once and lets each answer inherit it.
- **Ответ на вопрос 3** (детерминированные деньги ↔ LLM-нарратив) is the clearest architectural invariant in the doc — unambiguous, actionable, with a validator requirement.
- **Ответ на вопрос 1** (access matrix) correctly makes психологический слой opaque to собственник and ties it to the trust contract — this is the right call and well articulated.
- **Ответ на вопрос 10** (corridor ±15%/+10%/−15%) gives concrete numbers a dev can code to.
- Every question in Блоки 1–4 **does** get a substantive answer — no blanks.

---

**Bottom line:** Fix P0-1 (flag §11.3/§11.5 for БТ correction), P0-2 (close the Вопрос 6 gap), and P0-3 (strip pandoc artifacts), and this document is ready to drive both the dev team and the БТ v2.2 edit. The P1 items will materially improve engineer actionability but are not blockers.

You can invoke `bmad-help` anytime if you want me to hand this off to John (PM) to fold the БТ corrections into v2.2, or to Winston (Architect) to spec the расчётная БД.