"""Modelos de datos inmutables del dominio de noticias."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class NewsSource:
    identifier: str
    name: str
    url: str
    categories: tuple[str, ...] = ()
    kind: str = "rss"
    enabled: bool = True
    source_classification: str = "publisher"
    refresh_minutes: int = 60


@dataclass(frozen=True)
class NewsItem:
    identifier: str
    title: str
    source: str
    source_id: str
    link: str
    published_at: datetime | None = None
    summary: str = ""
    category: str = ""
    source_classification: str = "publisher"

    @property
    def published_label(self) -> str:
        return self.published_at.isoformat() if self.published_at else "Fecha no indicada"


@dataclass(frozen=True)
class SourceStatus:
    source_id: str
    source_name: str
    ok: bool
    item_count: int = 0
    from_cache: bool = False
    error: str = ""


@dataclass(frozen=True)
class NewsQueryResult:
    items: tuple[NewsItem, ...]
    statuses: tuple[SourceStatus, ...]
    period: str = "all"
    category: str | None = None

    @property
    def failures(self) -> tuple[SourceStatus, ...]:
        return tuple(status for status in self.statuses if not status.ok)
