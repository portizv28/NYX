"""Puertos para sustituir buscadores y lectores web."""

from typing import Protocol

from internet.models import SearchResult, WebPage


class SearchProvider(Protocol):
    def search(self, query: str) -> tuple[SearchResult, ...]: ...


class PageReader(Protocol):
    def read(self, url: str) -> WebPage: ...
