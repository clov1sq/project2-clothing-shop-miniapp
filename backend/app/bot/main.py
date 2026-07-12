import asyncio
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)


async def run_bot() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    if not settings.telegram_bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is empty; bot process exits cleanly")
        return

    from aiogram import Bot, Dispatcher, Router
    from aiogram.filters import Command
    from aiogram.types import (
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        MenuButtonWebApp,
        Message,
        WebAppInfo,
    )

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    router = Router()
    web_app = WebAppInfo(url=settings.mini_app_url)

    async def send_shop(message: Message) -> None:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text="Відкрити магазин", web_app=web_app)]]
        )
        await message.answer(
            f"{settings.shop_name} — сучасний fashion-каталог у Telegram.",
            reply_markup=keyboard,
        )

    @router.message(Command("start"))
    async def start(message: Message) -> None:
        await send_shop(message)

    @router.message(Command("shop"))
    async def shop(message: Message) -> None:
        await send_shop(message)

    @router.message(Command("admin"))
    async def admin(message: Message) -> None:
        if not message.from_user or message.from_user.id not in settings.admin_telegram_ids:
            await message.answer("Адмін-доступ для цього акаунта не налаштований.")
            return
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Відкрити керування каталогом",
                        web_app=WebAppInfo(url=f"{settings.mini_app_url.rstrip('/')}/#/admin"),
                    )
                ]
            ]
        )
        await message.answer("Керування каталогом", reply_markup=keyboard)

    dispatcher.include_router(router)
    await bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="Магазин", web_app=web_app))
    logger.info("Bot polling started", extra={"event": "bot_started"})
    await dispatcher.start_polling(bot)


def main() -> None:
    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
