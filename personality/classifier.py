"""Selección local y explicable del modo de interacción."""

from personality.models import InteractionMode


class InteractionModeSelector:
    PROFESSIONAL_KEYWORDS = {
        "finanza", "inversión", "inversion", "economía", "economia", "mercado",
        "trabajo", "estudio", "analiza", "análisis", "analisis", "informe",
        "riesgo", "estrategia", "programa", "código", "codigo",
    }

    def select(self, text: str) -> InteractionMode:
        normalized = text.casefold()
        if any(keyword in normalized for keyword in self.PROFESSIONAL_KEYWORDS):
            return InteractionMode.PROFESSIONAL
        return InteractionMode.EVERYDAY
