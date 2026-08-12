"""Traduce un perfil en instrucciones y respuestas de tono coherente."""

from __future__ import annotations

from personality.classifier import InteractionModeSelector
from personality.models import InteractionMode, PersonalityProfile


class PersonalityEngine:
    def __init__(self, profile: PersonalityProfile, selector: InteractionModeSelector | None = None) -> None:
        self.profile = profile
        self.selector = selector or InteractionModeSelector()

    def mode_for(self, text: str) -> InteractionMode:
        return self.selector.select(text)

    def instruction_for(self, text: str) -> str:
        mode = self.mode_for(text)
        mode_guidance = (
            self.profile.professional_guidance
            if mode is InteractionMode.PROFESSIONAL
            else self.profile.everyday_guidance
        )
        traits = ", ".join(self.profile.core_traits)
        return (
            f"Eres {self.profile.display_name}, una inteligencia personal para {self.profile.user_name}. "
            f"Tu presencia transmite {traits}. Mantén una actitud serena, sabia, profunda y nunca agresiva. "
            f"{mode_guidance} {self.profile.humor_guidance} "
            "No afirmes haber realizado acciones o consultado fuentes que no consten en el contexto."
        )

    def prepare_prompt(self, text: str) -> str:
        return f"Instrucciones de identidad:\n{self.instruction_for(text)}\n\nSolicitud:\n{text}"

    def format_direct_response(self, request: str, response: str) -> str:
        """Da calidez a respuestas locales sin reescribir contenido factual."""
        if not response or "pablo" in response[:80].casefold():
            return response
        if request.casefold().strip().startswith("abre "):
            return "Ahora mismo, señorito Pablo."
        if self.mode_for(request) is InteractionMode.PROFESSIONAL:
            return f"Por supuesto, Pablo. {response}"
        return f"Claro, Pablo. {response}"
