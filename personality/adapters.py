"""Adaptadores que aplican personalidad fuera del router y el cerebro."""

from ai.contracts import AIProvider
from personality.contracts import TextProcessor
from personality.engine import PersonalityEngine


class PersonalityAwareProvider:
    """Añade identidad al prompt sin conocer el proveedor que lo atenderá."""

    def __init__(self, provider: AIProvider, personality: PersonalityEngine) -> None:
        self.provider = provider
        self.personality = personality
        self.name = provider.name

    def ask(self, text: str) -> str:
        return self.provider.ask(self.personality.prepare_prompt(text))


class PersonalityAwareProcessor:
    """Aplica el tono a acciones y reglas que no pasan por IA."""

    def __init__(self, processor: TextProcessor, personality: PersonalityEngine) -> None:
        self.processor = processor
        self.personality = personality

    def procesar(self, text: str) -> str:
        return self.personality.format_direct_response(text, self.processor.procesar(text))
