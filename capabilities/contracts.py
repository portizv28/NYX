"""Contrato de una capacidad independiente de NYX."""

from __future__ import annotations

from typing import Protocol

from automation.registry import ActionRegistry


class Capability(Protocol):
    identifier: str
    description: str

    def register_actions(self, actions: ActionRegistry) -> None:
        """Instala las acciones que la capacidad ofrece a NYX."""

