"""Repositorio de fuentes permitido; no hay URLs incrustadas en el cerebro."""

from __future__ import annotations

import json
from pathlib import Path

from config.settings import get_settings
from news.models import NewsSource


class NewsSourceRepository:
    def __init__(self, path: Path | None = None) -> None:
        configured_path = Path(get_settings().news_sources_path)
        self.path = path or (
            configured_path if configured_path.is_absolute()
            else Path(__file__).resolve().parents[1] / configured_path
        )

    def sources(self) -> tuple[NewsSource, ...]:
        return self._read("sources")

    def trackers(self) -> tuple[NewsSource, ...]:
        return self._read("trackers")

    def _read(self, key: str) -> tuple[NewsSource, ...]:
        data = json.loads(self.path.read_text(encoding="utf-8"))
        return tuple(
            NewsSource(
                identifier=item["id"], name=item["name"], url=item["url"],
                categories=tuple(item.get("categories", ())), kind=item.get("kind", "rss"),
                enabled=bool(item.get("enabled", True)),
                source_classification=item.get("source_classification", "publisher"),
                refresh_minutes=int(item.get("refresh_minutes", 60)),
            )
            for item in data.get(key, ()) if item.get("enabled", True)
        )
