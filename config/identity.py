"""Identidad visible y hablada del asistente.

Centralizarla evita que voz, interfaz y futuro reconocimiento mantengan listas
de nombres o pronunciaciones incompatibles.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class AssistantIdentity:
    display_name: str
    spoken_name: str
    wake_words: tuple[str, ...]

    def extract_command(self, text: str) -> str | None:
        """Devuelve la orden tras una palabra de activación o ``None``."""
        for wake_word in self.wake_words:
            match = re.search(rf"\b{re.escape(wake_word)}\b", text, flags=re.IGNORECASE)
            if match:
                return (text[:match.start()] + text[match.end():]).strip(" ,.!¿?")
        return None

    def for_speech(self, text: str) -> str:
        """Convierte el nombre escrito a la pronunciación natural para TTS."""
        return re.sub(
            rf"\b{re.escape(self.display_name)}\b",
            self.spoken_name,
            text,
            flags=re.IGNORECASE,
        )


NYX_IDENTITY = AssistantIdentity(
    display_name="NYX",
    spoken_name="Nix",
    wake_words=("nyx", "nix"),
)
