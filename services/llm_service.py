"""Сервис обращения к Groq API (OpenAI-совместимый протокол)."""
from __future__ import annotations

import asyncio
import logging
from collections import deque
from functools import lru_cache

from openai import AsyncOpenAI, APIConnectionError, APIError, APITimeoutError

import config
from services.product_service import product_service

logger = logging.getLogger(__name__)

HISTORY_LIMIT = 10  # максимум сообщений на пользователя (5 пар вопрос-ответ)


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
        f"Ты консультант магазина «{config.SHOP_NAME}».\n{base}\n\n"
        f"АКТУАЛЬНЫЙ КАТАЛОГ (используй ТОЛЬКО эти товары и цены):\n{catalog}"
    )


def _relevant_details(search_text: str, limit: int = 3) -> str:
    """Ищем релевантные товары по тексту (берём слова длиннее 2 букв)."""
    words = [w for w in search_text.lower().split() if len(w) >= 3]
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
            base_url=config.GROQ_BASE_URL,
            api_key=config.GROQ_API_KEY,
            timeout=config.GROQ_TIMEOUT,
            max_retries=0,
        )
        # История диалогов: user_id → deque из {"role": ..., "content": ...}
        self._history: dict[int, deque[dict]] = {}

    def clear_history(self, user_id: int) -> None:
        self._history.pop(user_id, None)

    async def ask(self, user_text: str, user_id: int = 0) -> str:
        """Отправить сообщение пользователя (с историей) и вернуть ответ модели."""
        history = self._history.setdefault(user_id, deque(maxlen=HISTORY_LIMIT))

        # Для поиска релевантных товаров берём последние реплики + текущую
        recent_text = " ".join(m["content"] for m in history if m["role"] == "user")
        search_text = f"{recent_text} {user_text}"
        system = _system_prompt() + _relevant_details(search_text)

        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        last_error: Exception | None = None
        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                response = await self._client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=messages,
                    max_tokens=config.GROQ_MAX_TOKENS,
                    temperature=config.TEMPERATURE,
                    top_p=config.TOP_P,
                )
                content = response.choices[0].message.content or ""
                answer = content.strip() or config.ERROR_MESSAGE

                # Сохраняем в историю только успешные обмены
                history.append({"role": "user", "content": user_text})
                history.append({"role": "assistant", "content": answer})

                return answer
            except (APIConnectionError, APITimeoutError) as e:
                last_error = e
                logger.warning(
                    "Groq недоступен (попытка %d/%d): %s",
                    attempt, config.MAX_RETRIES, e,
                )
            except APIError as e:
                last_error = e
                logger.error("Ошибка Groq API: %s", e)
                break
            except Exception as e:  # noqa: BLE001
                last_error = e
                logger.exception("Непредвиденная ошибка LLM: %s", e)
                break

            await asyncio.sleep(config.RETRY_DELAY * attempt)

        if isinstance(last_error, (APIConnectionError, APITimeoutError)):
            return "⚠️ Не могу подключиться к Groq. Проверь интернет-соединение."
        return config.ERROR_MESSAGE


# Синглтон, импортируется как `from services import llm_service`
llm_service = LLMService()
