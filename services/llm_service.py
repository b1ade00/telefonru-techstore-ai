"""Сервис обращения к локальному LM Studio через OpenAI-совместимый API."""
from __future__ import annotations

import asyncio
import logging
from functools import lru_cache

from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError

import config
from services.product_service import product_service

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    """Базовый системный промпт + компактный каталог."""
    try:
        with open(config.SYSTEM_PROMPT_FILE, "r", encoding="utf-8") as f:
            base = f.read().strip()
    except FileNotFoundError:
        logger.warning("system_prompt.txt не найден, использую дефолт.")
        base = "Ты вежливый продавец-консультант магазина техники."

    catalog = product_service.render_catalog_compact()
    return (
        f"{base}\n\n"
        f"АКТУАЛЬНЫЙ КАТАЛОГ (используй ТОЛЬКО эти товары и цены):\n{catalog}"
    )


def _relevant_details(user_text: str, limit: int = 3) -> str:
    """Если в сообщении пользователя есть слова из каталога, добавим деталей."""
    # Берём по 1 слову из запроса и ищем — наивно, но работает.
    words = [w for w in user_text.lower().split() if len(w) >= 3]
    seen: set[str] = set()
    matches = []
    for w in words:
        for p in product_service.search(w, limit=limit):
            if p.id in seen:
                continue
            seen.add(p.id)
            matches.append(p)
            if len(matches) >= limit:
                break
        if len(matches) >= limit:
            break
    if not matches:
        return ""
    detail = "\n".join(p.full() for p in matches)
    return f"\n\nДЕТАЛИ ПО РЕЛЕВАНТНЫМ ТОВАРАМ:\n{detail}"


class LLMService:
    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            base_url=config.LM_STUDIO_BASE_URL,
            api_key=config.LM_STUDIO_API_KEY,
            timeout=config.LM_STUDIO_TIMEOUT,
            max_retries=0,  # ретраи делаем сами, openai-клиент пусть не дёргает
        )

    async def ask(self, user_text: str) -> str:
        """Отправить сообщение пользователя и вернуть ответ модели."""
        system = _system_prompt() + _relevant_details(user_text)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ]

        last_error: Exception | None = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=config.LM_STUDIO_MODEL,
                    messages=messages,
                    max_tokens=config.LM_STUDIO_MAX_TOKENS,
                    temperature=config.TEMPERATURE,
                    top_p=config.TOP_P,
                )
                content = response.choices[0].message.content or ""
                return content.strip() or config.ERROR_MESSAGE
            except (APIConnectionError, APITimeoutError) as e:
                last_error = e
                logger.warning(
                    "LM Studio недоступна (попытка %d/%d): %s",
                    attempt, config.MAX_RETRIES, e,
                )
            except APIError as e:
                last_error = e
                logger.error("Ошибка API LM Studio: %s", e)
                break  # API-ошибка не лечится повторами
            except Exception as e:  # noqa: BLE001 — логируем и сдаёмся
                last_error = e
                logger.exception("Непредвиденная ошибка LLM: %s", e)
                break

            await asyncio.sleep(config.RETRY_DELAY * attempt)

        if isinstance(last_error, (APIConnectionError, APITimeoutError)):
            return (
                "⚠️ Не могу подключиться к LM Studio. "
                "Проверь, что сервер запущен на "
                f"{config.LM_STUDIO_BASE_URL} и модель загружена."
            )
        return config.ERROR_MESSAGE


# Синглтон, импортируется как `from services import llm_service`
llm_service = LLMService()
