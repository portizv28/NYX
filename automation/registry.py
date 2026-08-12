"""Registro extensible de acciones de automatización."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


ActionMatcher = Callable[[str], bool]
ActionHandler = Callable[[str], str]


@dataclass(frozen=True)
class RegisteredAction:
    name: str
    description: str
    matches: ActionMatcher
    execute: ActionHandler


@dataclass(frozen=True)
class ActionResult:
    action_name: str
    message: str


class ActionRegistry:
    """Almacena capacidades sin acoplarlas al cerebro."""

    def __init__(self) -> None:
        self._actions: list[RegisteredAction] = []

    def register(self, action: RegisteredAction) -> None:
        if any(existing.name == action.name for existing in self._actions):
            raise ValueError(f"La acción '{action.name}' ya está registrada.")
        self._actions.append(action)

    def execute(self, text: str) -> ActionResult | None:
        for action in self._actions:
            if action.matches(text):
                try:
                    return ActionResult(action.name, action.execute(text))
                except Exception as error:
                    print(f"Error ejecutando la acción '{action.name}':", error)
                    return ActionResult(
                        action.name,
                        "No he podido completar esa acción. Comprueba que el programa está disponible.",
                    )
        return None

    def list_actions(self) -> tuple[RegisteredAction, ...]:
        return tuple(self._actions)
