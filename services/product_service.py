"""Каталог товаров: загрузка из JSON, поиск, форматирование для LLM."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Iterable

import config

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    category: str
    price_rub: int
    stock: int
    specs: str
    tags: list[str]

    def short(self) -> str:
        return f"{self.name} — {self.price_rub}₽ ({self.category})"

    def full(self) -> str:
        avail = "есть в наличии" if self.stock > 0 else "сейчас нет"
        return (
            f"• {self.name} — {self.price_rub}₽\n"
            f"  {self.specs}\n"
            f"  {avail}"
        )


class ProductService:
    """Загружает каталог один раз и отдаёт по запросу."""

    def __init__(self, path: str = config.PRODUCTS_FILE) -> None:
        self._path = path
        self._products: list[Product] = []
        self._load()

    def _load(self) -> None:
        try:
            with open(self._path, "r", encoding="utf-8") as f:
                raw = json.load(f)
        except FileNotFoundError:
            logger.warning("Каталог не найден: %s. Использую пустой.", self._path)
            self._products = []
            return
        except json.JSONDecodeError as e:
            logger.error("Каталог повреждён (%s): %s", self._path, e)
            self._products = []
            return

        products: list[Product] = []
        for item in raw:
            try:
                # Поддерживаем и старое поле price_usd, и новое price_rub.
                if "price_rub" in item:
                    price = int(round(float(item["price_rub"])))
                elif "price_usd" in item:
                    price = int(round(float(item["price_usd"])))
                else:
                    raise KeyError("price_rub/price_usd")

                products.append(
                    Product(
                        id=str(item["id"]),
                        name=str(item["name"]),
                        category=str(item["category"]).lower(),
                        price_rub=price,
                        stock=int(item.get("stock", 0)),
                        specs=str(item.get("specs", "")),
                        tags=[str(t).lower() for t in item.get("tags", [])],
                    )
                )
            except (KeyError, TypeError, ValueError) as e:
                logger.warning("Пропускаю битую запись %r: %s", item, e)
        self._products = products
        logger.info("Загружено товаров: %d", len(products))

    def all(self) -> list[Product]:
        return list(self._products)

    def search(self, query: str, limit: int = 5) -> list[Product]:
        """Простой полнотекстовый поиск по имени, категории и тегам."""
        if not query:
            return []
        q = query.lower()
        scored: list[tuple[int, Product]] = []
        for p in self._products:
            score = 0
            if q in p.name.lower():
                score += 5
            if q in p.category:
                score += 3
            if any(q in t for t in p.tags):
                score += 2
            if q in p.specs.lower():
                score += 1
            if score > 0:
                scored.append((score, p))
        scored.sort(key=lambda x: (-x[0], x[1].price_rub))
        return [p for _, p in scored[:limit]]

    def render_catalog(self, products: Iterable[Product] | None = None) -> str:
        items = list(products) if products is not None else self._products
        if not items:
            return "Каталог пуст."
        return "\n".join(p.full() for p in items)

    def render_catalog_compact(
        self, products: Iterable[Product] | None = None
    ) -> str:
        """Однострочный список: название — цена — наличие. Без specs."""
        items = list(products) if products is not None else self._products
        if not items:
            return "Каталог пуст."
        lines: list[str] = []
        for p in items:
            avail = "есть" if p.stock > 0 else "нет"
            lines.append(f"{p.name} — {p.price_rub}₽ ({avail})")
        return "\n".join(lines)


# Синглтон, импортируется как `from services import product_service`
product_service = ProductService()
