import unittest

from internet.models import SearchResult, WebPage
from internet.service import InternetService


class FakeSearchProvider:
    def __init__(self):
        self.query = None

    def search(self, query):
        self.query = query
        return (SearchResult("resultado", "https://example.test"),)


class FakePageReader:
    def read(self, url):
        return WebPage(url, "Página", "contenido")


class InternetServiceTests(unittest.TestCase):
    def test_uses_injected_search_provider(self):
        provider = FakeSearchProvider()
        service = InternetService(provider, FakePageReader())

        result = service.search("arquitectura limpia")

        self.assertEqual("arquitectura limpia", provider.query)
        self.assertEqual("resultado", result[0].title)

    def test_rejects_empty_search(self):
        with self.assertRaises(ValueError):
            InternetService(FakeSearchProvider(), FakePageReader()).search("  ")
