"""Contratos independientes de proveedores concretos de IA."""

from __future__ import annotations

from typing import Protocol


class AIProvider(Protocol):
    name: str

    def ask(self, text: str) -> str:
        """Genera una respuesta para una consulta de lenguaje natural."""

