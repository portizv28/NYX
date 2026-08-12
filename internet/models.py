"""Modelos neutrales para proveedores de Internet."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str = ""


@dataclass(frozen=True)
class WebPage:
    url: str
    title: str
    text: str
