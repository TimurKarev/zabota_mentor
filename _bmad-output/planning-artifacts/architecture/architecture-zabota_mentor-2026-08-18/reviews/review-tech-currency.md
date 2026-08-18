# Review — Tech Currency Lens

**Reviewer gate:** architecture spine, Zabot AI Mentor Stage 1
**Reviewed file:** `/Users/timurkarev/Projects/zabota_mentor/_bmad-output/planning-artifacts/architecture/architecture-zabota_mentor-2026-08-18/ARCHITECTURE-SPINE.md`
**Date of review:** 2026-08-18 (web spot-checks performed this date)
**Lens:** every committed technology decision is web-researched/reality-checked rather than asserted from training data; versions current; named services still exist and fit.

---

## Verdict

**PASS with conditions.** Every load-bearing technology named in the spine still exists, is maintained, and fits the stated role. No row of the Stack table names a dead or deprecated technology. The conditions: (1) pin the "current stable" rows at a defined moment (M0) rather than leaving them perpetually floating; (2) correct the PostgreSQL row — Yandex Managed PostgreSQL now offers 14–18, so "16/17" both understates the menu and leaves the actual pick ambiguous; (3) soften the spine's "Versions verified by research 2026-08-16/17" claim, which is only partially true (see MEDIUM-1).

---

## BLOCKING

None. Nothing in the stack is dead, unmaintained, or unfit for its role.

---

## HIGH

None rise to HIGH. The closest candidates (ProxyAPI ToS exposure, unpinned versions) are hedged by design in the spine (LlmPort abstraction, Q4 open, "owned by the code once it exists") and are filed as MEDIUM.

---

## MEDIUM

### MEDIUM-1 — Stack preamble overstates what the research verified

The Stack section says *"Versions verified by research 2026-08-16/17."* Checking the cited research doc (`_bmad-output/planning-artifacts/research/technical-stage1-reference-architecture-zabot-ai-mentor-research-2026-08-16.md`): it web-verifies **existence, fit, and provider availability** (with inline sources for FastAPI, aiogram 3, Yandex Managed PostgreSQL, ProxyAPI, promptfoo, GitLab CE), but it pins **no exact versions** for FastAPI or Redis anywhere. "aiogram 3" and "PostgreSQL 16/17" are the only near-pins. The claim should read "technologies verified by research 2026-08-16/17; exact versions to be pinned at M0" — otherwise a future reader assumes a version audit that never happened.

**Fix:** one-line edit to the Stack preamble.

### MEDIUM-2 — PostgreSQL row is stale/ambiguous: Yandex offers 14–18, so "16/17" should become a decision

Verified against Yandex Cloud's official docs: Managed Service for PostgreSQL supports **14, 15, 16, 17, and 18** (source: [Yandex Managed PostgreSQL docs](https://yandex.cloud/en/docs/managed-postgresql/), [release notes](https://yandex.cloud/en/docs/managed-postgresql/release-notes)). The spine's "16/17" is not wrong but (a) omits that 18 is available, and (b) leaves the actual production version unpicked — and the Yandex upgrade path is one-major-version-at-a-time, so the starting version is a real decision, not a detail. Note PG 16 reaches EOL upstream in Nov 2028; a service started in 2026 should start on 17 or 18.

**Fix:** change the row to `PostgreSQL 17 or 18 (managed, Yandex Cloud)` — or pin 17 explicitly — and note the one-major-per-upgrade constraint next to it.

### MEDIUM-3 — ProxyAPI: operating, but the ToS/reseller risk is not carried into the spine

Verified operating as of 2026-08-18: proxyapi.ru is live, ruble-billed, actively maintained (recent models listed, current integration docs; listed among working RU aggregators in 2026 RU-press roundups — [proxyapi.ru](https://proxyapi.ru/), [VC.ru OpenAI API в России 2026](https://vc.ru/provod/2962649-openai-api-v-rossii-kak-rabotat-bez-vpn)). However, the search also surfaced what the research doc mentions only in passing: these intermediaries operate **outside OpenAI/Anthropic ToS** (unauthorized resellers, unsupported region) — no provider endorsement, no independent verification of reliability, and precedent of provider-side crackdowns on proxies. The research doc carries this as "most volatile layer"; the spine's Q4 row does not.

**Fix:** add one clause to Q4 (egress mechanism): "intermediary route carries provider-ToS availability risk; own egress VM is the ToS-clean option; `LlmPort` must keep the switch to a one-adapter change." No architecture change needed — the hedge already exists structurally.

### MEDIUM-4 — "current stable" rows: acceptable only with a defined pinning moment

Rows affected: **FastAPI "current stable"**, **Redis "current stable"**. Spot-checked reality (2026-08-18):

- FastAPI **0.141.1** (2026-07-29; [PyPI](https://pypi.org/project/fastapi/), [release notes](https://fastapi.tiangolo.com/release-notes/)) — actively maintained, still pre-1.0 so minor bumps can break.
- Redis **8.10** (2026-07-29; [endoflife.date/redis](https://endoflife.date/redis), [GitHub releases](https://github.com/redis/redis/releases)) — Redis 8 is AGPLv3-era licensing; self-hosted/managed use is unaffected for this project, and the spine's "Redis holds no durable state" (AD-4) keeps it swappable regardless.

The spine's framing — *"Seed — true at cold-start, owned by the code once it exists"* — makes "current stable" defensible for an altitude-initiative spine: pinning FastAPI 0.x in an architecture document would go stale within weeks. **But the convention has a hole: no pinning moment is named.** "Owned by the code once it exists" only works if "when code exists" is a milestone.

**Fix:** add to the Stack preamble: "exact versions pinned in `pyproject.toml` / `docker-compose.yml` at M0 and thereafter owned by the repo; this table records the floor, not the lock." Also record Python floor semantics explicitly (see LOW-1).

---

## LOW

### LOW-1 — Python floor "3.12+" is safe but conservative

Current stable branches (2026-08-18): 3.14.7 (2026-08-12), 3.13.15, 3.12.14 ([python.org downloads](https://www.python.org/downloads/), [endoflife.date/python](https://endoflife.date/python)). "3.12+" is a floor, not a pin — fine. 3.12 is supported into late 2028 and all chosen libs (aiogram 3.30 needs 3.10+, FastAPI 0.141 needs 3.10+) work on it. Consider 3.13 as the actual floor for a greenfield 2026 service (mature library support per current guidance); not required.

### LOW-2 — aiogram 3: confirmed as the maintained Python Telegram standard

aiogram **3.30.0** current on [PyPI](https://pypi.org/project/aiogram/); repo active ([GitHub](https://github.com/aiogram/aiogram)); still the recommended async Python Telegram framework in 2026 comparisons (grammY leads in TS, aiogram in Python — consistent with the research doc's claim). The spine's "3.x" is correctly loose. No action.

### LOW-3 — promptfoo: maintained; an acquisition rumor exists and is unverified

Verified directly: promptfoo **0.122.0** released 2026-08-04, regular release cadence, no stewardship change in the release notes ([GitHub releases](https://github.com/promptfoo/promptfoo/releases)). One blog ([dev.to "After Promptfoo's Exit"](https://dev.to/thedailyagent/top-5-ai-agent-eval-tools-after-promptfoos-exit-576i)) claims an OpenAI acquisition — **contradicted by the release evidence; treat as unverified rumor**, but worth a periodic glance since AD-1's CI enforcement leans on promptfoo. Its position as the standard LLM-output test tool is confirmed by 2026 comparisons ([promptfoo docs](https://www.promptfoo.dev/docs/intro/)). No action beyond awareness; the golden-test concept is tool-agnostic anyway (assertllm named as Python-native alternative in the research).

### LOW-4 — GitLab CE fallback: confirmed viable

GitLab CE remains open source (MIT) and free to self-host in 2026 ([pricing page](https://about.gitlab.com/pricing/), [gitlab.com/install](https://gitlab.com/install)); the August 2026 user-limit enforcement hits only the hosted GitLab.com Free tier, not self-hosted CE. The fallback row is sound. Note the research already observed that the market momentum is pushing toward self-hosted — if GitHub account risk materializes, the `git push --mirror` migration path claimed in the research is real.

### LOW-5 — Sentry cross-border: covered by design, worth one explicit word

Sentry SaaS is hosted outside the RU zone. The spine's AD-5 says "logs everywhere are PII-scrubbed," which covers error telemetry as long as scrubbing happens before egress. The research doc says "Sentry (self-hosted option if strict)" — that caveat did not make it into the spine's Observability row. One word ("Sentry (self-hosted if strict)") would carry it.

### LOW-6 — Not independently re-verified this pass (accepted from research citations)

Yandex Lockbox, Yandex Container Registry, docker compose on 2 VMs, pytest/pytest-asyncio, Grafana/Yandex Cloud Monitoring, Telegram webhook `secret_token` and rate limits (~1 msg/s per chat). All are cited with sources in the research doc (2026-08-16) and are low-volatility infrastructure facts; no staleness signal. Risk of these being wrong: negligible.

---

## Summary table

| Item | Severity | Status (2026-08-18) | Source |
| --- | --- | --- | --- |
| Stack preamble "versions verified" claim | MEDIUM | Overstated — research verified fit, not versions | research doc inspection |
| PostgreSQL "16/17" on Yandex | MEDIUM | Stale/ambiguous — 14–18 offered; pick 17/18 | [Yandex docs](https://yandex.cloud/en/docs/managed-postgresql/) |
| ProxyAPI as LLM hop | MEDIUM | Operating; ToS/reseller risk not carried into spine | [proxyapi.ru](https://proxyapi.ru/), [VC.ru](https://vc.ru/provod/2962649-openai-api-v-rossii-kak-rabotat-bez-vpn) |
| FastAPI / Redis "current stable" rows | MEDIUM | Acceptable as floor, needs named pinning moment (M0) | [PyPI](https://pypi.org/project/fastapi/), [endoflife.date/redis](https://endoflife.date/redis) |
| Python 3.12+ floor | LOW | Safe; consider 3.13 floor | [python.org](https://www.python.org/downloads/) |
| aiogram 3 | LOW | Confirmed maintained, 3.30.0 | [PyPI](https://pypi.org/project/aiogram/) |
| promptfoo | LOW | Confirmed maintained, 0.122.0; acquisition rumor unverified | [GitHub releases](https://github.com/promptfoo/promptfoo/releases) |
| GitLab CE | LOW | Confirmed viable self-hosted | [about.gitlab.com](https://about.gitlab.com/pricing/) |
| Sentry | LOW | Fine; carry "self-hosted if strict" caveat | research doc |
| Lockbox, Registry, pytest, compose, TG limits | LOW | Accepted from research citations, low volatility | research doc |
