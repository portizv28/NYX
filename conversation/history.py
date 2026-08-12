"""Historial acotado que prepara contexto para cualquier proveedor de IA."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class ConversationMessage:
    role: str
    content: str


class ConversationHistory:
    def __init__(self, max_messages: int = 12) -> None:
        self._messages: deque[ConversationMessage] = deque(maxlen=max_messages)

    def add_user(self, text: str) -> None:
        self._messages.append(ConversationMessage("Usuario", text))

    def add_assistant(self, text: str) -> None:
        self._messages.append(ConversationMessage("NYX", text))

    def prompt_for_ai(self, current_text: str) -> str:
        """Devuelve el texto original si no hay contexto anterior.

        Así los proveedores siguen recibiendo exactamente el comportamiento
        anterior en la primera interacción y ganan contexto a partir de la
        segunda.
        """
        previous = list(self._messages)
        if previous and previous[-1] == ConversationMessage("Usuario", current_text):
            previous.pop()
        if not previous:
            return current_text
        formatted = "\n".join(f"{message.role}: {message.content}" for message in previous)
        return (
            "Contexto reciente de la conversación:\n"
            f"{formatted}\n\n"
            f"Usuario: {current_text}\n"
            "Responde teniendo en cuenta el contexto, sin inventar datos."
        )

    def messages(self) -> tuple[ConversationMessage, ...]:
        return tuple(self._messages)
