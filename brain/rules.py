"""Respuestas deterministas que no requieren un proveedor de IA."""

from __future__ import annotations


class SmallTalkRules:
    def respond(self, text: str) -> str | None:
        normalized = text.casefold()
        if "hola" in normalized:
            return "Muy buenas, Pablo."
        if "quien eres" in normalized or "quién eres" in normalized:
            return "Soy NYX, tu asistente personal. Se pronuncia Nix."
        return None
