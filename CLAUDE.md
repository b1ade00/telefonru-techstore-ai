# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the bot

```bash
cp .env.example .env          # fill in TELEGRAM_TOKEN at minimum
source venv/bin/activate
python bot.py
```

LM Studio must be running with a model loaded before starting the bot (`http://localhost:1234/v1` by default). The catalog and system prompt are cached at startup via `@lru_cache` — restart the bot after changing either.

## Architecture

Telegram message → `handlers/message_handler.py` → `services/llm_service.py` → LM Studio (OpenAI-compatible API) → reply.

**Request flow in `llm_service.ask()`:**
1. `_system_prompt()` (cached) — reads `prompts/system_prompt.txt` + appends the full compact catalog from `ProductService.render_catalog_compact()`
2. `_relevant_details()` — keyword-searches the catalog for up to 3 matching products and appends their full specs to the system prompt
3. Single-turn `chat.completions.create()` — no conversation history, each message is stateless

**Singletons** — both services expose module-level instances (`llm_service` and `product_service`) imported directly: `from services import llm_service, product_service`.

**Product catalog** (`data/products.json`) — loaded once at startup into `ProductService._products`. Supports both `price_rub` and legacy `price_usd` fields. Search scores by name (5), category (3), tags (2), specs (1) and returns top-N.

## Configuration

All tunable values live in `config.py` (loaded from `.env`). Key ones:

| Variable | Default | Notes |
|---|---|---|
| `LM_STUDIO_MODEL` | `google/gemma-4-e4b` | Must match the model name shown in LM Studio |
| `LM_STUDIO_TIMEOUT` | `30` s | `.env.example` suggests 600 for slow hardware |
| `LM_STUDIO_MAX_TOKENS` | `256` | Keep low — answers are intentionally short |
| `TEMPERATURE` | `0.7` | `.env.example` suggests 0.6 for more consistent pricing |
| `MAX_RETRIES` | `3` | Only retried on connection/timeout errors, not API errors |

## Key constraints from the system prompt

- Answers must be 1–3 short sentences, no lists or headers unless the user asks
- Never reveal stock count, product IDs, tags, or internal categories
- Never suggest alternatives unless the user requests them or the item is out of stock
- Prices formatted as `45990₽` (no spaces, no decimals)
