"""Registro de capacidades, separado del registro de acciones."""

from __future__ import annotations

from automation.registry import ActionRegistry
from capabilities.contracts import Capability


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    def register(self, capability: Capability) -> None:
        if capability.identifier in self._capabilities:
            raise ValueError(f"La capacidad '{capability.identifier}' ya está registrada.")
        self._capabilities[capability.identifier] = capability

    def install_actions(self, actions: ActionRegistry) -> None:
        for capability in self._capabilities.values():
            capability.register_actions(actions)

    def list_capabilities(self) -> tuple[Capability, ...]:
        return tuple(self._capabilities.values())
