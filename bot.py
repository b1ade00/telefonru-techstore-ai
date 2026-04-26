"""Точка входа: создаёт Bot, Dispatcher, регистрирует router и запускает поллинг."""
from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode

import config
from handlers import router


def _setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        stream=sys.stdout,
    )


async def main() -> None:
    _setup_logging()
    log = logging.getLogger("bot")

    session = AiohttpSession()
    bot = Bot(
        token=config.TELEGRAM_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.include_router(router)

    me = await bot.get_me()
    log.info(
        "Запущен @%s (id=%s). LM Studio: %s, модель: %s",
        me.username, me.id, config.LM_STUDIO_BASE_URL, config.LM_STUDIO_MODEL,
    )
    log.info(config.STARTUP_MESSAGE)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nОстановлено пользователем.")
