import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


async def run_bot() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)

    if not settings.telegram_bot_token:
        logger.warning(
            "TELEGRAM_BOT_TOKEN is empty. Bot shell is not started. "
            "Set TELEGRAM_BOT_TOKEN in .env to run polling."
        )
        return

    try:
        from aiogram import Bot, Dispatcher, Router
        from aiogram.filters import CommandStart
        from aiogram.types import Message
    except ImportError as exc:  # pragma: no cover - handled by Docker dependencies
        raise RuntimeError("aiogram is required to run the bot process") from exc

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await message.answer(
            f"{settings.shop_name} foundation is running. "
            "Telegram auth and Mini App menu will be added in v2."
        )

    dispatcher.include_router(router)
    logger.info("Bot polling started", extra={"event": "bot_started"})
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
