"""TelegramPort implementation over an aiogram ``Bot`` (Story 1.2, AD-10)."""

from aiogram import Bot


class AiogramTelegramPort:
    """Thin send adapter: delegates straight to the Bot API, no policy.

    The domain's replies go through ``TelegramPort`` so no domain or app code
    calls the raw aiogram ``Bot`` (AD-10: Telegram is transport, not state).
    """

    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    async def send_message(self, chat_id: int, text: str) -> None:
        await self._bot.send_message(chat_id=chat_id, text=text)
