---
title: 'Polling-bot self-healing via Docker healthcheck (Story 1.2 review fix)'
type: 'bugfix'
created: 2026-09-05
status: 'in-review'
baseline_commit: 'e41de5ca872b8a6066f833bad33c6aaa18572a8f'
review_loop_iteration: 1
context:
  - '{project-root}/docs/ops-staging.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** In polling mode, a single failure of the background `start_polling` task (e.g. a network timeout to `api.telegram.org` at container start — incident 2026-09-05) kills the bot silently: the task's done-callback logs the error but nothing restarts it, while `/health` stays 200, so Docker never notices and the bot stays dead until a manual restart.

**Approach:** Track polling-task liveness via a flag on `app.state` set/cleared by the task's done-callback, and make `GET /health` (and `/`) return 503 when the bot was expected to run (BOT_TOKEN set, polling mode) and its polling task has terminated. Docker's existing `unless-stopped` restart policy + the existing compose healthcheck then restart the container and the bot comes back on its own.

## Boundaries & Constraints

**Always:**
- 503 is returned ONLY when the polling task was started and has terminated. All other states — no BOT_TOKEN, webhook mode, injected test deps, healthy polling — return 200.
- The "no BOT_TOKEN → /health 200" regression guard must keep passing (CI starts the app with no external deps).
- Compose files unchanged; no deploy, no commit — changes stay in the working tree.

**Ask First:**
- If a real fix turns out to require compose changes (e.g. healthcheck tuning) rather than app code alone.
- If a retry/backoff supervisor inside the app seems needed instead of container-restart-based recovery.

**Never:**
- Do not touch the webhook mode path (its D2 fix is separate).
- Do not restart/supervise the polling task in-process — recovery is Docker's job.
- Do not deploy to staging or commit to main.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Polling alive | BOT_TOKEN set, polling mode, task running | `/health` 200 `{"status":"ok"}` | N/A |
| Polling died | BOT_TOKEN set, polling task raised/exited | `/health` 503 with diagnostic detail | done-callback logs the exception |
| No bot configured | BOT_TOKEN absent | `/health` 200 | existing warning log stays |
| Webhook mode | BOT_MODE=webhook | `/health` 200 (no polling liveness tracked) | N/A |
| Clean shutdown | app shutting down, poll task cancelled | flag flips but process is exiting — no impact | cancellation not logged as error |

</frozen-after-approval>

## Code Map

- `src/app/main.py` — add liveness flag wiring: `_log_polling_failure` becomes an app-aware done-callback that clears the flag; `/health` handler reads the flag.
- `tests/unit/test_telegram_webhook.py` — home of the no-token /health regression test; polling-health tests fit here.
- `docker-compose.staging.yml` — read-only reference: healthcheck curls `/health`; restart policy `unless-stopped`.
- `docs/ops-staging.md` — incident log; the open code-fix note this spec closes.

## Tasks & Acceptance

**Execution:**
- [x] `src/app/main.py` -- in the polling branch set `app.state.polling_alive = True` when the task is created; replace `_log_polling_failure` with a done-callback (closure over `app`) that sets it to `False` before logging; `/health` and `/` return 503 when `polling_alive` is `False` (absent flag = healthy) -- single source of truth for liveness, no env re-reading in the handler.
- [x] `tests/unit/test_telegram_webhook.py` -- add tests: (a) polling dead → `/health` 503; (b) no BOT_TOKEN → `/health` 200; (c) polling alive → `/health` 200; (d) the done-callback flips the flag on a failed task (real `asyncio` task in `asyncio.run`, exception consumed).

**Acceptance Criteria:**
- Given the polling task terminated with an exception, when any client calls `GET /health`, then the response is 503 and the exception was logged once.
- Given no BOT_TOKEN, when the app starts, then `/health` stays 200 (CI regression guard intact).
- Given the fix is applied, when the incident scenario recurs on staging, then the container turns unhealthy and Docker restarts it automatically.

## Spec Change Log

## Design Notes

The flag (not the `asyncio.Task` object) is stored on `app.state` deliberately: tests can simulate any state without touching the TestClient's event loop, and webhook/no-token paths need no sentinel values. Default-missing-attribute = healthy keeps the injected-deps test path and webhook mode untouched.

```python
# done-callback sketch
def _on_polling_done(task: asyncio.Task[None]) -> None:
    app.state.polling_alive = False
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error("Telegram polling stopped with an error", exc_info=exc)
```

## Verification

**Commands:**
- `ruff check .` -- expected: no findings — **result: "All checks passed!"**
- `mypy src` -- expected: no errors (this is the CI gate; `mypy .` on the whole repo has 16 pre-existing errors in test/_bmad files, identical at baseline commit `e41de5c`) — **result: Success, 39 files**
- `pytest` -- expected: all pass — **result: 56 passed, 13 skipped (4 new tests)**
- `ruff format --check .` -- 13 files flagged, all pre-existing at baseline (repo wraps narrower than width 100); not a CI gate, new lines add no violations
