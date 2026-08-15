import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

from automation.registry import ActionRegistry
from news.capability import NewsCapability, NilOjedaCapability
from news.models import NewsItem, NewsSource
from news.service import JsonNewsCache, NewsFetchError, NewsService, RssNewsProvider


def item(identifier, title, published, link="https://example.test/item", source="Fuente tech"):
    return NewsItem(identifier, title, source, "tech", link, published, "Resumen comprobable", "technology")


class FakeProvider:
    def __init__(self, items=(), error=None):
        self.items, self.error, self.calls = tuple(items), error, 0

    def fetch(self, source, limit=5):
        self.calls += 1
        if self.error:
            raise self.error
        return self.items


class FakeSources:
    def sources(self):
        return (NewsSource("tech", "Fuente tech", "https://example.test", ("technology",), refresh_minutes=60),)

    def trackers(self):
        return (NewsSource("nil", "Fuente pública", "https://example.test"),)


class Response:
    def __init__(self, payload): self.payload = payload
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def read(self): return self.payload


class NewsServiceTests(unittest.TestCase):
    def test_parses_rss_and_normalizes_date(self):
        payload = b"""<rss><channel><item><title>Titular</title><link>https://example.test/a</link><description>&lt;b&gt;Resumen&lt;/b&gt;</description><pubDate>Fri, 14 Aug 2026 12:00:00 +0000</pubDate></item></channel></rss>"""
        source = NewsSource("source", "Fuente", "https://example.test/feed")
        with patch("news.service.urllib.request.urlopen", return_value=Response(payload)):
            entries = RssNewsProvider().fetch(source)
        self.assertEqual("Titular", entries[0].title)
        self.assertEqual("Resumen", entries[0].summary)
        self.assertIsNotNone(entries[0].published_at)

    def test_separates_source_error_from_no_items(self):
        service = NewsService(FakeProvider(error=NewsFetchError("HTTP 403")), JsonNewsCache(Path(tempfile.mkdtemp()) / "cache.json"))
        result = service.collect(FakeSources().sources(), refresh=True)
        self.assertEqual(1, len(result.failures))
        self.assertIn("No he podido consultar", service.format(result))

    def test_filters_today_deduplicates_and_caches(self):
        now = datetime(2026, 8, 15, 12, tzinfo=__import__("news.service", fromlist=["MADRID"]).MADRID)
        provider = FakeProvider((item("one", "Una", now, "https://x/a"), item("two", "Duplicada", now, "https://x/a"), item("old", "Antigua", now - timedelta(days=2), "https://x/old")))
        service = NewsService(provider, JsonNewsCache(Path(tempfile.mkdtemp()) / "cache.json"))
        first = service.collect(FakeSources().sources(), period="today", now=now)
        second = service.collect(FakeSources().sources(), period="today", now=now)
        self.assertEqual(1, len(first.items))
        self.assertEqual(1, provider.calls)
        self.assertTrue(second.statuses[0].from_cache)

    def test_reference_resolves_second_news(self):
        now = datetime.now(__import__("news.service", fromlist=["MADRID"]).MADRID)
        service = NewsService(FakeProvider((item("one", "Primera noticia", now, "https://x/1"), item("two", "NVIDIA anuncia algo", now, "https://x/2", source="Nature"))), JsonNewsCache(Path(tempfile.mkdtemp()) / "cache.json"))
        service.collect(FakeSources().sources(), refresh=True)
        self.assertEqual("two", service.resolve_reference("Cuéntame más sobre la segunda").identifier)
        self.assertEqual("two", service.resolve_reference("Háblame de NVIDIA").identifier)
        self.assertEqual("two", service.resolve_reference("Amplía la de Nature").identifier)
        service.select_link("https://x/2")
        self.assertEqual("two", service.resolve_reference("Háblame de esa noticia").identifier)

    def test_capabilities_use_registered_actions(self):
        now = datetime.now(__import__("news.service", fromlist=["MADRID"]).MADRID)
        news = NewsCapability(FakeSources(), NewsService(FakeProvider((item("one", "Titular", now),)), JsonNewsCache(Path(tempfile.mkdtemp()) / "cache.json")))
        registry = ActionRegistry()
        news.register_actions(registry)
        result = registry.execute("¿Qué noticias hay hoy?")
        self.assertEqual("news_updates", result.action_name)
        detail = registry.execute("Cuéntame más sobre la primera")
        self.assertEqual("news_detail", detail.action_name)

    def test_nil_tracker_is_separate(self):
        registry = ActionRegistry()
        NilOjedaCapability(FakeSources(), NewsService(FakeProvider(), JsonNewsCache(Path(tempfile.mkdtemp()) / "cache.json"))).register_actions(registry)
        self.assertEqual("nil_ojeda_updates", registry.execute("¿Hay novedades de Nil Ojeda?").action_name)
