"""Casos de uso de Internet, independientes de comandos y de IA."""

from internet.contracts import PageReader, SearchProvider
from internet.models import SearchResult, WebPage


class InternetService:
    def __init__(self, search_provider: SearchProvider, page_reader: PageReader) -> None:
        self.search_provider = search_provider
        self.page_reader = page_reader

    def search(self, query: str) -> tuple[SearchResult, ...]:
        if not query.strip():
            raise ValueError("Indica qué quieres buscar.")
        return self.search_provider.search(query.strip())

    def read_page(self, url: str) -> WebPage:
        return self.page_reader.read(url.strip())
