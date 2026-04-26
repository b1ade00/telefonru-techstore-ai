"""Хендлеры aiogram: команды и обработка обычных сообщений."""
from __future__ import annotations

import logging

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.enums import ChatAction
from aiogram.types import Message

import config
from services import llm_service, product_service

logger = logging.getLogger(__name__)
router = Router(name="messages")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(config.WELCOME_MESSAGE)


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(config.HELP_MESSAGE)


@router.message(Command("catalog"))
async def cmd_catalog(message: Message) -> None:
    text = product_service.render_catalog()
    # Telegram лимит 4096 символов — режем при необходимости
    chunks = _chunk(text, config.MAX_MESSAGE_LENGTH)
    for chunk in chunks:
        await message.answer(chunk)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_text = (message.text or "").strip()
    if not user_text:
        return

    user_id = message.from_user.id if message.from_user else "?"
    logger.info("[%s] %s", user_id, user_text[:200])

    # Показываем "печатает...", пока ждём LLM
    if message.bot:
        await message.bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    answer = await llm_service.ask(user_text)
    for chunk in _chunk(answer, config.MAX_MESSAGE_LENGTH):
        await message.answer(chunk)


@router.message()
async def handle_other(message: Message) -> None:
    """Картинки, голосовые и т.п. — пока не поддерживаем."""
    await message.answer(
        "Пока я понимаю только текстовые сообщения 🙂 "
        "Опиши, что ищешь, словами."
    )


def _chunk(text: str, size: int) -> list[str]:
    if len(text) <= size:
        return [text]
    return [text[i : i + size] for i in range(0, len(text), size)]
