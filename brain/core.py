"""Cerebro de NYX: ordena prioridades, no implementa capacidades."""

from __future__ import annotations

from collections.abc import Callable
from ai.contracts import AIProvider
from automation.registry import ActionRegistry
from brain.memory_intents import MemoryIntentHandler
from brain.rules import SmallTalkRules
from conversation.history import ConversationHistory
from memory.in_memory_store import InMemoryStore
from memory.service import MemoryService


class NyxBrain:
    """Prioridad: acciones registradas, reglas locales y finalmente IA."""

    def __init__(
        self,
        router: AIProvider,
        actions: ActionRegistry | None = None,
        rules: SmallTalkRules | None = None,
        memory: MemoryService | None = None,
        conversation: ConversationHistory | None = None,
        on_action: Callable[[str], None] | None = None,
    ) -> None:
        self.estado = "Esperando"  # Compatibilidad con la versión inicial.
        self.router = router
        self.actions = actions or ActionRegistry()
        self.rules = rules or SmallTalkRules()
        self.memory = memory or MemoryService(InMemoryStore())
        self.memory_intents = MemoryIntentHandler(self.memory)
        self.conversation = conversation or ConversationHistory()
        self.on_action = on_action

    def procesar(self, mensaje: str) -> str:
        text = mensaje.strip()
        if not text:
            return "No he recibido ninguna orden."

        self.conversation.add_user(text)

        action_result = self.actions.execute(text)
        if action_result:
            if self.on_action:
                self.on_action(action_result.action_name)
            return self._respond(action_result.message)

        memory_response = self.memory_intents.respond(text)
        if memory_response:
            return self._respond(memory_response)

        rule_response = self.rules.respond(text)
        if rule_response:
            return self._respond(rule_response)

        return self._respond(self.router.ask(self.conversation.prompt_for_ai(text)))

    def _respond(self, response: str) -> str:
        self.conversation.add_assistant(response)
        return response
