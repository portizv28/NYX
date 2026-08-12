"""Contratos para decorar proveedores y procesadores sin acoplarlos."""

from typing import Protocol


class TextProcessor(Protocol):
    def procesar(self, text: str) -> str: ...
