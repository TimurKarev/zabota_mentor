"""Unit tests for the Telegram webhook endpoint + /start handler (Story 1.2).

No real Telegram API is touched (AC 5.4): the bot is a never-connected aiogram
Bot, the repository and send port are fakes, and updates are fed through the
FastAPI endpoint via TestClient — exactly the webhook path prod uses
(``feed_webhook_update``).
"""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from aiogram import Bot
from fastapi.testclient import TestClient

from src.adapters.telegram import BotDependencies, build_dispatcher
from src.app.main import create_app
from src.domain.ports.telegram import TelegramPort

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

from tests.unit.test_start_command import DEV_SALON_BY_CODE, FakeRepository

SECRET = "test-secret-token"
# Valid token shape for aiogram (never used against the real API).
FAKE_BOT_TOKEN = "1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"


class RecordingTelegramPort:
    """TelegramPort fake: records sends instead of calling the Bot API."""

    def __init__(self) -> None:
        self.sent: list[tuple[int, str]] = []

    async def send_message(self, chat_id: int, text: str) -> None:
        self.sent.append((chat_id, text))


def _make_update(update_id: int, text: str) -> dict[str, object]:
    """A minimal valid Telegram update dict for a private-chat /start."""
    return {
        "update_id": update_id,
        "message": {
            "message_id": 1,
            "date": 1750000000,
            "chat": {"id": 1001, "type": "private"},
            "from": {"id": 1001, "is_bot": False, "first_name": "Test"},
            "text": text,
        },
    }


Harness = tuple[TestClient, FakeRepository, RecordingTelegramPort]


@pytest.fixture
def harness(monkeypatch: pytest.MonkeyPatch) -> Harness:
    """App with fake deps: (client, repository, send port)."""
    monkeypatch.setenv("TELEGRAM_SECRET_TOKEN", SECRET)
    repository = FakeRepository(DEV_SALON_BY_CODE)
    port = RecordingTelegramPort()

    @asynccontextmanager
    async def open_repository() -> "AsyncIterator[FakeRepository]":
        yield repository

    bot = Bot(token=FAKE_BOT_TOKEN)
    dispatcher = build_dispatcher(
        BotDependencies(open_repository=open_repository, telegram=port)
    )
    client = TestClient(create_app(bot=bot, dispatcher=dispatcher))
    return client, repository, port


def _post(
    client: TestClient, payload: dict[str, object], secret: str | None = SECRET
) -> object:
    headers = {} if secret is None else {"X-Telegram-Bot-Api-Secret-Token": secret}
    return client.post("/telegram/webhook", json=payload, headers=headers)


def test_webhook_missing_secret_header_is_401(
    harness: Harness,
) -> None:
    client, _, port = harness
    with client:
        response = _post(client, _make_update(1, "/start salon1"), secret=None)
    assert response.status_code == 401
    assert port.sent == []


def test_webhook_wrong_secret_is_403(
    harness: Harness,
) -> None:
    client, _, port = harness
    with client:
        response = _post(client, _make_update(1, "/start salon1"), secret="wrong")
    assert response.status_code == 403
    assert port.sent == []


def test_webhook_without_configured_secret_is_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TELEGRAM_SECRET_TOKEN", raising=False)
    bot = Bot(token=FAKE_BOT_TOKEN)
    repository = FakeRepository(DEV_SALON_BY_CODE)
    port = RecordingTelegramPort()

    @asynccontextmanager
    async def open_repository() -> "AsyncIterator[FakeRepository]":
        yield repository

    dispatcher = build_dispatcher(
        BotDependencies(open_repository=open_repository, telegram=port)
    )
    with TestClient(create_app(bot=bot, dispatcher=dispatcher)) as client:
        response = client.post(
            "/telegram/webhook", json=_make_update(1, "/start salon1")
        )
    assert response.status_code == 503


def test_webhook_valid_signed_start_invokes_handler_and_replies(
    harness: Harness,
) -> None:
    client, repository, port = harness
    with client:
        response = _post(client, _make_update(7, "/start salon1"))
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    # Handler ran: welcome names the salon, rows were created.
    assert len(port.sent) == 1
    chat_id, text = port.sent[0]
    assert chat_id == 1001
    assert "Dev Salon" in text
    assert 1001 in repository._chat_to_master


def test_webhook_replayed_update_id_is_deduped(
    harness: Harness,
) -> None:
    """AC #7: a Telegram retry of the same update is a no-op (AD-12)."""
    client, _, port = harness
    payload = _make_update(42, "/start salon1")
    with client:
        first = _post(client, payload)
        second = _post(client, payload)
    assert first.status_code == 200
    assert second.status_code == 200
    assert len(port.sent) == 1


def test_webhook_plain_start_sends_fallback(
    harness: Harness,
) -> None:
    client, repository, port = harness
    with client:
        response = _post(client, _make_update(9, "/start"))
    assert response.status_code == 200
    assert len(port.sent) == 1
    assert "Dev Salon" not in port.sent[0][1]
    assert repository._chat_to_master == {}


def test_health_still_ok_and_webhook_503_without_bot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: the app degrades to /health only when no bot is configured."""
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    monkeypatch.setenv("TELEGRAM_SECRET_TOKEN", SECRET)
    with TestClient(create_app()) as client:
        assert client.get("/health").json() == {"status": "ok"}
        response = client.post(
            "/telegram/webhook",
            json=_make_update(1, "/start salon1"),
            headers={"X-Telegram-Bot-Api-Secret-Token": SECRET},
        )
    assert response.status_code == 503


def test_fake_port_satisfies_telegram_port_protocol() -> None:
    """Structural check: the recording fake matches TelegramPort."""
    assert isinstance(RecordingTelegramPort(), TelegramPort)


def test_group_chat_start_is_ignored(harness: Harness) -> None:
    """AD-13: a group chat_id is a shared identity — no master, no reply."""
    client, repository, port = harness
    payload = _make_update(11, "/start salon1")
    payload["message"]["chat"] = {"id": -1001234, "type": "group"}
    with client:
        response = _post(client, payload)
    assert response.status_code == 200
    assert port.sent == []
    assert repository._chat_to_master == {}


def test_handler_failure_sends_no_reply(harness: Harness) -> None:
    """A failed handler must not send anything — the reply goes out only
    after the update's transaction commits (review P1)."""

    class ExplodingRepository(FakeRepository):
        async def find_or_create_master_with_chat(self, chat_id: int) -> UUID:
            raise RuntimeError("simulated DB failure")

    repository = ExplodingRepository(DEV_SALON_BY_CODE)
    port = RecordingTelegramPort()

    @asynccontextmanager
    async def open_repository() -> "AsyncIterator[ExplodingRepository]":
        yield repository

    bot = Bot(token=FAKE_BOT_TOKEN)
    dispatcher = build_dispatcher(
        BotDependencies(open_repository=open_repository, telegram=port)
    )
    with (
        TestClient(create_app(bot=bot, dispatcher=dispatcher)) as client,
        pytest.raises(RuntimeError),
    ):
        _post(client, _make_update(21, "/start salon1"))
    assert port.sent == []
    assert repository._update_ids == {21}
