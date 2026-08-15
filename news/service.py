"""Obtención, caché, filtrado y referencias de noticias sin UI ni cerebro."""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from news.models import NewsItem, NewsQueryResult, NewsSource, SourceStatus


try:
    MADRID = ZoneInfo("Europe/Madrid")
except ZoneInfoNotFoundError:
    # Python para Windows puede no incluir la base IANA hasta instalar tzdata.
    # El fallback permite arrancar y registrar fechas; la instalación completa
    # declara tzdata para conservar las reglas de horario de Madrid.
    MADRID = timezone.utc


class NewsFetchError(RuntimeError):
    """Fallo de una fuente; se conserva para diagnóstico, no se interpreta como vacío."""


class RssNewsProvider:
    """Lector RSS/Atom basado en la biblioteca estándar, con timeout explícito."""

    def __init__(self, timeout_seconds: float = 12.0) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self, source: NewsSource, limit: int = 20) -> tuple[NewsItem, ...]:
        request = urllib.request.Request(source.url, headers={"User-Agent": "NYX-News/1.0 (+local personal assistant)"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds, context=self._ssl_context()) as response:
                payload = response.read()
        except urllib.error.HTTPError as error:
            raise NewsFetchError(f"HTTP {error.code}") from error
        except urllib.error.URLError as error:
            raise NewsFetchError(f"Conexión: {error.reason}") from error
        except TimeoutError as error:
            raise NewsFetchError("Tiempo de espera agotado") from error
        try:
            root = ET.fromstring(payload)
        except ET.ParseError as error:
            raise NewsFetchError("RSS/Atom inválido") from error
        entries = root.findall(".//item") or root.findall(".//{*}item") or root.findall(".//{http://www.w3.org/2005/Atom}entry") or root.findall(".//{*}entry")
        if not entries:
            raise NewsFetchError("El feed no contiene entradas reconocibles")
        return tuple(self._entry_to_item(entry, source) for entry in entries[:limit])

    @staticmethod
    def _ssl_context():
        """Usa el almacén CA actualizado de certifi si está instalado, sin rebajar TLS."""
        try:
            import certifi
            import ssl
            return ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            return None

    def _entry_to_item(self, entry: ET.Element, source: NewsSource) -> NewsItem:
        atom = "{http://www.w3.org/2005/Atom}"
        title = self._text(entry, "title", atom) or "Sin titular"
        link = self._text(entry, "link", atom)
        if not link:
            link_node = entry.find(f"{atom}link")
            link = link_node.get("href", "") if link_node is not None else ""
        raw_summary = self._text(entry, "description", atom) or self._text(entry, "summary", atom) or self._text(entry, "content", atom)
        published = self._parse_date(self._text(entry, "pubDate", atom) or self._text(entry, "published", atom) or self._text(entry, "updated", atom))
        category_node = entry.find("category") or entry.find(f"{atom}category")
        category = category_node.get("term", "") if category_node is not None else ""
        identifier = hashlib.sha256(f"{source.identifier}|{link or title}".encode("utf-8")).hexdigest()[:16]
        return NewsItem(identifier, title, source.name, source.identifier, link, published, self._clean_text(raw_summary), category, source.source_classification)

    @staticmethod
    def _text(entry: ET.Element, name: str, atom: str) -> str:
        node = entry.find(name)
        if node is None:
            node = entry.find(f"{atom}{name}")
        if node is None:
            node = entry.find(f"{{*}}{name}")
        return node.text.strip() if node is not None and node.text else ""

    @staticmethod
    def _clean_text(value: str) -> str:
        return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html.unescape(value))).strip()

    @staticmethod
    def _parse_date(value: str) -> datetime | None:
        if not value:
            return None
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        return (parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)).astimezone(MADRID)


class WebNewsProvider(RssNewsProvider):
    """Último recurso para editoriales sin RSS activo: extrae JSON-LD público."""

    def fetch(self, source: NewsSource, limit: int = 20) -> tuple[NewsItem, ...]:
        request = urllib.request.Request(source.url, headers={"User-Agent": "NYX-News/1.0 (+local personal assistant)"})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds, context=self._ssl_context()) as response:
                page = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as error:
            raise NewsFetchError(f"HTTP {error.code}") from error
        except urllib.error.URLError as error:
            raise NewsFetchError(f"Conexión: {error.reason}") from error
        entries: list[dict] = []
        for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', page, flags=re.I | re.S):
            try:
                data = json.loads(block)
            except json.JSONDecodeError:
                continue
            entries.extend(self._news_nodes(data))
            if not entries:
                entries.extend(self._articles_from_list(data, source, limit))
        if not entries:
            raise NewsFetchError("La página no publica noticias estructuradas")
        return tuple(self._json_item(entry, source) for entry in entries[:limit])

    def _articles_from_list(self, node, source: NewsSource, limit: int) -> list[dict]:
        """CollectionPage de Forbes ofrece URLs; cada artículo sí publica NewsArticle."""
        urls = self._list_urls(node)
        articles: list[dict] = []
        for url in urls[:limit]:
            try:
                request = urllib.request.Request(url, headers={"User-Agent": "NYX-News/1.0 (+local personal assistant)"})
                with urllib.request.urlopen(request, timeout=self.timeout_seconds, context=self._ssl_context()) as response:
                    article_page = response.read().decode("utf-8", errors="replace")
                for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', article_page, flags=re.I | re.S):
                    try:
                        articles.extend(self._news_nodes(json.loads(block)))
                    except json.JSONDecodeError:
                        continue
                if articles:
                    articles[-1].setdefault("url", url)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
                continue
        return articles

    def _list_urls(self, node) -> list[str]:
        if isinstance(node, list):
            return [url for child in node for url in self._list_urls(child)]
        if not isinstance(node, dict):
            return []
        urls = []
        if "ListItem" in str(node.get("@type", "")) and isinstance(node.get("url"), str):
            urls.append(node["url"])
        for value in node.values():
            urls.extend(self._list_urls(value))
        return urls

    def _news_nodes(self, node) -> list[dict]:
        if isinstance(node, list):
            return [item for child in node for item in self._news_nodes(child)]
        if not isinstance(node, dict):
            return []
        found = [node] if "NewsArticle" in str(node.get("@type", "")) else []
        for value in node.values():
            found.extend(self._news_nodes(value))
        return found

    def _json_item(self, data: dict, source: NewsSource) -> NewsItem:
        title = str(data.get("headline") or data.get("name") or "Sin titular")
        link = str(data.get("url") or "")
        identifier = hashlib.sha256(f"{source.identifier}|{link or title}".encode("utf-8")).hexdigest()[:16]
        return NewsItem(identifier, title, source.name, source.identifier, link, self._parse_date(str(data.get("datePublished") or "")), self._clean_text(str(data.get("description") or "")), source.categories[0] if source.categories else "", source.source_classification)


class JsonNewsCache:
    """Caché JSON reemplazable por SQLite sin afectar al proveedor ni capability."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or Path(".nyx") / "news_cache.json"

    def get(self, source: NewsSource) -> tuple[NewsItem, ...] | None:
        data = self._read().get(source.identifier)
        if not data or time.time() - data["saved_at"] > source.refresh_minutes * 60:
            return None
        return tuple(self._deserialize(item) for item in data["items"])

    def put(self, source: NewsSource, items: Iterable[NewsItem]) -> None:
        data = self._read()
        data[source.identifier] = {"saved_at": time.time(), "items": [self._serialize(item) for item in items]}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def _read(self) -> dict:
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _serialize(item: NewsItem) -> dict:
        return {**item.__dict__, "published_at": item.published_at.isoformat() if item.published_at else None}

    @staticmethod
    def _deserialize(data: dict) -> NewsItem:
        published = datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None
        return NewsItem(**{**data, "published_at": published})


class NewsService:
    def __init__(self, provider: RssNewsProvider | None = None, cache: JsonNewsCache | None = None, web_provider: WebNewsProvider | None = None) -> None:
        self.provider = provider or RssNewsProvider()
        self.web_provider = web_provider or WebNewsProvider()
        self.cache = cache or JsonNewsCache()
        self._last_result: NewsQueryResult | None = None
        self._selected_item_id: str | None = None

    def collect(self, sources: Iterable[NewsSource], category: str | None = None, period: str = "all", limit: int = 8, refresh: bool = False, now: datetime | None = None) -> NewsQueryResult:
        statuses: list[SourceStatus] = []
        all_items: list[NewsItem] = []
        for source in sources:
            if category and category not in source.categories:
                continue
            cached = None if refresh else self.cache.get(source)
            try:
                provider = self.web_provider if source.kind == "web" else self.provider
                items = cached if cached is not None else provider.fetch(source, limit=max(limit * 3, 15))
                if cached is None:
                    self.cache.put(source, items)
                statuses.append(SourceStatus(source.identifier, source.name, True, len(items), cached is not None))
                all_items.extend(items)
            except NewsFetchError as error:
                statuses.append(SourceStatus(source.identifier, source.name, False, error=str(error)))
            except Exception as error:
                statuses.append(SourceStatus(source.identifier, source.name, False, error=f"Error inesperado: {type(error).__name__}"))
        filtered = self._deduplicate(self._filter_period(all_items, period, now))
        filtered.sort(key=lambda item: item.published_at or datetime.min.replace(tzinfo=MADRID), reverse=True)
        self._last_result = NewsQueryResult(tuple(filtered[:limit]), tuple(statuses), period, category)
        return self._last_result

    def last_result(self) -> NewsQueryResult | None:
        return self._last_result

    def resolve_reference(self, text: str) -> NewsItem | None:
        if not self._last_result:
            return None
        normalized = text.casefold()
        if any(token in normalized for token in ("esta noticia", "esa noticia")) and self._selected_item_id:
            return next((item for item in self._last_result.items if item.identifier == self._selected_item_id), None)
        ordinals = {"primera": 0, "primero": 0, "segunda": 1, "segundo": 1, "tercera": 2, "tercero": 2, "cuarta": 3, "cuarto": 3}
        for word, position in ordinals.items():
            if word in normalized and position < len(self._last_result.items):
                return self._last_result.items[position]
        for item in self._last_result.items:
            if item.source.casefold() in normalized:
                return item
            if item.title.casefold() in normalized or any(word in normalized for word in item.title.casefold().split() if len(word) > 4):
                return item
        return None

    def select_link(self, link: str) -> None:
        if self._last_result:
            selected = next((item for item in self._last_result.items if item.link == link), None)
            self._selected_item_id = selected.identifier if selected else None

    @staticmethod
    def _filter_period(items: Iterable[NewsItem], period: str, now: datetime | None) -> list[NewsItem]:
        reference = (now or datetime.now(MADRID)).astimezone(MADRID)
        if period == "all":
            return list(items)
        start = {"today": reference.replace(hour=0, minute=0, second=0, microsecond=0), "yesterday": (reference - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0), "3days": reference - timedelta(days=3), "week": reference - timedelta(days=7)}[period]
        end = reference if period != "yesterday" else start + timedelta(days=1)
        return [item for item in items if item.published_at and start <= item.published_at <= end]

    @staticmethod
    def _deduplicate(items: Iterable[NewsItem]) -> list[NewsItem]:
        seen: set[str] = set()
        result: list[NewsItem] = []
        for item in items:
            key = item.link.casefold().rstrip("/") or item.title.casefold()
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

    @staticmethod
    def format(result: NewsQueryResult, spoken: bool = False) -> str:
        if not result.items:
            failed = len(result.failures)
            if failed:
                return f"No he podido consultar {failed} fuente{'s' if failed != 1 else ''} configurada{'s' if failed != 1 else ''}. Revisa el panel Noticias para ver su estado."
            return "Las fuentes se han consultado correctamente, pero no hay noticias para ese periodo."
        selected = result.items[:3] if spoken else result.items
        prefix = f"Tengo {len(result.items)} novedades relevantes de tus fuentes. " if spoken else "Información encontrada en fuentes configuradas:\n"
        rows = [f"{index + 1}. {item.title} ({item.source}, {item.published_label})" for index, item in enumerate(selected)]
        suffix = " Puedes pedirme cualquiera de las demás." if spoken and len(result.items) > len(selected) else ""
        return prefix + "\n".join(rows) + suffix
