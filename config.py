"""Загрузка конфигурации из переменных окружения (.env)."""
import os
from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Переменная окружения {name} не задана. Проверь файл .env"
        )
    return value


# Telegram
TELEGRAM_TOKEN = _require("TELEGRAM_TOKEN")

# LM Studio
LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
LM_STUDIO_MODEL = os.getenv("LM_STUDIO_MODEL", "google/gemma-4-e4b")
LM_STUDIO_TIMEOUT = float(os.getenv("LM_STUDIO_TIMEOUT", "30"))
LM_STUDIO_MAX_TOKENS = int(os.getenv("LM_STUDIO_MAX_TOKENS", "256"))

# Параметры генерации
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
TOP_P = float(os.getenv("TOP_P", "0.9"))

# Поведение
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "4096"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Сообщения для пользователя
THINKING_MESSAGE = "⏳ Думаю над ответом..."
ERROR_MESSAGE = "😔 Извините, не смог обработать запрос. Попробуйте ещё раз."
STARTUP_MESSAGE = "✅ Бот запущен! Спроси меня о технике."
WELCOME_MESSAGE = (
    "Привет! 👋 Я помогу выбрать технику из нашего каталога.\n"
    "Просто напиши, что ищешь — например: «нужен ноутбук до 1500$ для работы»."
)
HELP_MESSAGE = (
    "Команды:\n"
    "/start — приветствие\n"
    "/help — это сообщение\n"
    "/catalog — показать каталог\n\n"
    "Или просто опиши, что нужно — я подскажу."
)

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products.json")
SYSTEM_PROMPT_FILE = os.path.join(BASE_DIR, "prompts", "system_prompt.txt")
