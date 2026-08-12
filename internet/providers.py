"""Proveedores estándar, sin acoplarlos al cerebro ni a una API concreta."""

from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
import webbrowser
from html.parser import HTMLParser

from internet.models import SearchResult, WebPage


class BrowserSearchProvider:
    """Abre una búsqueda en el navegador elegido por el usuario.

    Es el proveedor inicial: no exige API, credenciales ni un servicio externo
    específico. Un proveedor de resultados estructurados podrá sustituirlo.
    """

    def __init__(self, base_url: str = "https://www.google.com/search?q=") -> None:
        self.base_url = base_url

    def search(self, query: str) -> tuple[SearchResult, ...]:
        url = self.base_url + urllib.parse.quote_plus(query)
        webbrowser.open(url)
        return (SearchResult(title=f"Búsqueda: {query}", url=url),)


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self._in_title = False
        self._parts: list[str] = []

    def handle_starttag(self, tag, attrs) -> None:
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag) -> None:
        if tag == "title":
            self._in_title = False

    def handle_data(self, data) -> None:
        text = data.strip()
        if not text:
            return
        if self._in_title:
            self.title += text
        self._parts.append(text)

    @property
    def text(self) -> str:
        return " ".join(self._parts)


class UrlPageReader:
    """Lector ligero de páginas HTML; la síntesis se delega a IA en el futuro."""

    def read(self, url: str) -> WebPage:
        _validate_url(url)
        request = urllib.request.Request(url, headers={"User-Agent": "NYX/0.1"})
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read().decode(response.headers.get_content_charset() or "utf-8", "replace")
        parser = _TextExtractor()
        parser.feed(content)
        return WebPage(url=url, title=html.unescape(parser.title), text=html.unescape(parser.text))


def _validate_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("La dirección web debe empezar por http:// o https://.")
