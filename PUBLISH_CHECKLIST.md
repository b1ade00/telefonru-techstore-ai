# 🚀 Чек-лист публикации: GitHub → рилс

Прямо в таком порядке — иначе словишь проблемы.

---

## ⚠️ Шаг 0: ротация токена (КРИТИЧНО)

Текущий токен светился у меня в ассистенте, в `.env` и раньше в `bot.py`.
Если он попадёт в публичный репозиторий — за минуты твоего бота угонят
автоматические сканеры GitHub.

1. Открой в Telegram [@BotFather](https://t.me/BotFather)
2. `/mybots` → выбери своего бота → **API Token** → **Revoke current token**
3. Скопируй новый токен
4. Открой `.env` в проекте, замени `TELEGRAM_TOKEN=...` на новый
5. Перезапусти бота: `Ctrl+C` в терминале, потом `./venv/bin/python bot.py`

---

## 📦 Шаг 1: подготовка репозитория

В терминале (`cd ~/ai-bot`):

```bash
# проверь, что .env в .gitignore и НЕ попадёт в коммит
cat .gitignore | grep .env

# если git ещё не инициализирован
git init
git add .
git status
# ВНИМАНИЕ: в списке файлов для коммита НЕ должно быть .env и venv/
# должны быть: bot.py, config.py, handlers/, services/, prompts/, data/,
# requirements.txt, .env.example, .gitignore, LICENSE, README.md,
# README.en.md, CONTENT_PLAN.md, PUBLISH_CHECKLIST.md, setup.sh

git commit -m "Initial commit: tech store AI bot on local LLM"
```

Если случайно увидел `.env` в `git status` — НЕ коммить. Сначала проверь
`.gitignore`, повтори `git rm --cached .env`, потом коммит.

---

## 🌐 Шаг 2: репозиторий на GitHub

1. Открой [github.com/new](https://github.com/new)
2. Repository name: `tech-store-ai-bot` (или своё)
3. Description: `Telegram bot for an offline tech store, powered by a local LLM (Qwen 2.5 14B via LM Studio). Russian/English README.`
4. **Public**
5. **Не** ставь галки на «Add README/license/.gitignore» — у тебя они уже есть
6. Жми **Create repository**

GitHub покажет команды. Тебе нужны эти три:

```bash
git remote add origin https://github.com/<твой-логин>/tech-store-ai-bot.git
git branch -M main
git push -u origin main
```

После пуша обнови страницу — увидишь README. Проверь, что выглядит
красиво (заголовки, эмодзи, схема ASCII).

---

## 🏷 Шаг 3: оформление репо на GitHub

В правом верхнем углу страницы репо — шестерёнка ⚙️ возле «About».

- **Description**: продублируй ту, что писал при создании
- **Website**: пока пусто (или ссылка на твой LinkedIn)
- **Topics**: `python`, `telegram-bot`, `aiogram`, `llm`, `local-llm`,
  `lmstudio`, `qwen`, `ai-assistant`, `russian`, `junior-developer`
- Галки: «Releases», «Packages» — снять, не нужны для одиночного проекта

В корне репо в README уже есть бейджи-эмодзи. Если хочешь добавить
техно-бейджи (Python version, License) — позже, не парься сейчас.

---

## 🎬 Шаг 4: записать GIF/видео для README

Без визуала README выглядит сухо. Тебе нужны 1 GIF (5–10 сек) + 1 скриншот.

**GIF (диалог в Telegram):**

1. На iPhone открой чат с ботом
2. Включи запись экрана (Control Center → красный кружок)
3. Напиши: «сколько стоит iphone 17 pro max?» — дождись ответа
4. Напиши: «посоветуй смартфон до 25 тыщ» — дождись ответа
5. Останови запись
6. На Mac закинь видео в [ezgif.com/video-to-gif](https://ezgif.com/video-to-gif),
   обрежь до 10 секунд, сожми до < 5 МБ
7. Сохрани как `docs/demo.gif` в репозитории

**Скриншот терминала:**

```bash
mkdir -p docs
# сделай скриншот терминала где видно "✅ Бот запущен!" и логи запросов
# Cmd+Shift+4 → выдели окно
```

Сохрани как `docs/terminal.png`.

Закоммить:

```bash
git add docs/
git commit -m "Add demo gif and terminal screenshot"
git push
```

В README замени строку `> Скриншот / GIF будет здесь...` на:

```markdown
![Demo](docs/demo.gif)
```

И сделай ещё один коммит.

---

## 🎥 Шаг 5: рилс / TikTok / Shorts

Подробный сценарий — в `CONTENT_PLAN.md`. Краткая версия:

1. **Запись**: QuickTime (Mac) для скринкаста кода + iOS Screen Recording
   для Telegram
2. **Монтаж**: CapCut. Импортируй оба видео, склей по таймлайну из плана
3. **Субтитры**: CapCut → Text → Auto-captions (он умеет русский)
4. **Музыка**: библиотека CapCut, что-то техно-минималистичное без слов
5. **Экспорт**: 1080×1920, 30 fps, H.264
6. **Публикация**:
   - TikTok: обложка из самого яркого кадра, описание = первый твит из плана
   - Instagram Reels: то же видео, repost
   - YouTube Shorts: то же

Хэштеги (для TikTok/Reels):
`#программист #junior #python #telegram #ai #нейросети #кодинг #разработка #it`

---

## 🐦 Шаг 6: посты в X / LinkedIn / Хабр / dev.to

Тексты готовы в `CONTENT_PLAN.md`. **Важно**: НЕ публикуй всё в один день.

Расписание на неделю:

| День | Площадка | Что |
|---|---|---|
| Пн (сегодня) | GitHub | Залить репо, выложить рилс |
| Вт | TikTok / Reels | Опубликовать рилс |
| Ср | X (Twitter) | Тред из 6 твитов |
| Пт | LinkedIn | Длинный пост |
| Сб | Хабр | Статья |
| Вс | dev.to | EN-версия статьи |

Так алгоритмы каждой площадки не будут конкурировать друг с другом за
внимание твоей аудитории, и каждый день будет что-то новое.

---

## 📊 Шаг 7: измерять и итерировать

Через 7 дней посмотри:

- GitHub: сколько звёзд, форков, посетителей (Insights → Traffic)
- TikTok/Reels: какой рилс зашёл лучше всех — повтори формат
- LinkedIn: кто лайкнул — добавь в контакты, особенно рекрутеров
- Хабр: сколько в закладках (это сильнее лайков)

Если не зашло — это нормально. Снимай следующий рилс через неделю,
не сдавайся после первой попытки. Личный бренд строится за 3–6 месяцев,
не за один пост.

---

## 🆘 Если что-то пошло не так

- **Случайно закоммитил .env** — НЕМЕДЛЕННО revoke токен в @BotFather
  и `git filter-repo` или просто удали репо и создай заново. Дальше
  отдельный новый коммит.
- **Бот сломался после правок** — `git checkout .` откатит все изменения
  в рабочей копии, но НЕ в коммитах. Если коммит уже сделан —
  `git reset --hard HEAD~1` уберёт последний коммит.
- **Не знаешь, что коммитить** — `git status` показывает что изменилось,
  `git diff` — что именно.
- **README выглядит криво на GitHub** — открой preview во VS Code
  (Cmd+Shift+V на .md файле), правь до тех пор, пока не нравится.
