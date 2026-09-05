"""aiogram wiring for the /start command (Story 1.2, AD-10, AD-12).

The handler is transport only: dedup gate -> domain ``handle_start`` -> reply
via ``TelegramPort``. All decisions live in ``src.domain.profile``. The
repository is injected per update through an async context-manager factory,
so tests substitute fakes and prod opens one psycopg connection + transaction
per update. Replies are deferred until AFTER that transaction commits: a send
failure cannot strand a half-committed update, and a DB failure cannot turn
an already-sent reply into a duplicate on retry.
"""

from collections.abc import Awaitable, Callable
from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Any

from aiogram import BaseMiddleware, Bot, Dispatcher, F, Router
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message, TelegramObject, Update

from src.domain.ports.telegram import TelegramPort
from src.domain.profile import ProfileRepository, handle_start, record_update_id_gate

RepositoryFactory = Callable[[], AbstractAsyncContextManager[ProfileRepository]]
Handler = Callable[..., Awaitable[Any]]


@dataclass(frozen=True)
class BotDependencies:
    """What the bot wiring needs from the composition root.

    ``open_repository`` yields one repository per Telegram update (a psycopg
    connection + stores in prod; a fake in tests). ``telegram`` is the send
    port the replies go through.
    """

    open_repository: RepositoryFactory
    telegram: TelegramPort


class UpdateDedupMiddleware(BaseMiddleware):
    """Durable update_id dedup, checked BEFORE any work (AD-12, AC #7).

    Runs as an outer middleware on the update observer, so a repeated update
    (Telegram retries non-200/timeout deliveries) never reaches a handler.
    The repository stays open for the whole update and is handed to handlers
    via the middleware ``data`` — one connection per update.
    """

    def __init__(self, deps: BotDependencies) -> None:
        self._deps = deps

    async def __call__(
        self,
        handler: Handler,
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        update = event if isinstance(event, Update) else None
        if update is None:
            # Not an update-level event (should not happen with the outer
            # registration below) — pass through untouched.
            return await handler(event, data)
        replies: list[tuple[int, str]] = []
        data["pending_replies"] = replies
        async with self._deps.open_repository() as repository:
            data["repository"] = repository
            if not await record_update_id_gate(repository, update.update_id):
                return None  # already processed — a retry must be a no-op
            response = await handler(event, data)
        # The update's transaction has committed — only now talk to Telegram.
        for chat_id, text in replies:
            await self._deps.telegram.send_message(chat_id=chat_id, text=text)
        return response


def create_start_router(deps: BotDependencies) -> Router:
    """Router with the /start handler; all decisions delegated to the domain."""

    router = Router(name="start")

    # Private chats only (AD-13): a group chat_id is a shared identity —
    # /start there must not create a canonical master for the whole group.
    @router.message(CommandStart(), F.chat.type == "private")
    async def on_start(
        message: Message,
        command: CommandObject,
        repository: ProfileRepository,
        pending_replies: list[tuple[int, str]],
    ) -> None:
        result = await handle_start(
            repository,
            chat_id=message.chat.id,
            start_payload=command.args,
        )
        pending_replies.append((message.chat.id, result.reply_text))

    return router


def build_bot(token: str, proxy: str | None = None) -> Bot:
    """Build the aiogram Bot. Plain text only — no parse_mode (deterministic templates).

    ``proxy`` (``TG_PROXY_URL``, e.g. ``socks5://warp:1080``) routes Bot API
    traffic through a proxy — required on RU-hosted environments where
    ``api.telegram.org`` is network-blocked. SOCKS needs the ``aiohttp-socks``
    dependency; plain HTTP(S) proxies work without it.
    """
    session = AiohttpSession(proxy=proxy) if proxy else None
    return Bot(token=token, session=session)


def build_dispatcher(deps: BotDependencies) -> Dispatcher:
    """Build the Dispatcher: update-level dedup outer middleware + start router."""
    dp = Dispatcher()
    dp.update.outer_middleware(UpdateDedupMiddleware(deps))
    dp.include_router(create_start_router(deps))
    return dp
