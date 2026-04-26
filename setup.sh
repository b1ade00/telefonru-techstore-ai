#!/usr/bin/env bash
# Пересоздать venv и установить зависимости. Запускать из папки ai-bot.
set -euo pipefail

cd "$(dirname "$0")"

# 1. Найти подходящий python (>=3.10)
PY="${PYTHON:-python3}"
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "❌ Не найден $PY. Установи Python 3.10+ (например: brew install python@3.12)"
  exit 1
fi
echo "→ Использую $($PY --version)"

# 2. Удалить старый venv
if [ -d venv ]; then
  echo "→ Удаляю старый venv"
  rm -rf venv
fi

# 3. Создать новый
echo "→ Создаю venv"
"$PY" -m venv venv

# 4. Установить зависимости
echo "→ Устанавливаю зависимости"
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

echo ""
echo "✅ Готово. Запуск:"
echo "   ./venv/bin/python bot.py"
