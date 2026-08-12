"""Detección textual de la palabra de activación tras una transcripción."""

from __future__ import annotations

import re
from dataclasses import dataclass

from config.identity import AssistantIdentity, NYX_IDENTITY


@dataclass(frozen=True)
class WakeDetection:
    command: str


class WakeWordDetector:
    """Acepta sólo variantes explícitas de «Nix» para limitar falsos positivos."""

    def __init__(self, identity: AssistantIdentity = NYX_IDENTITY) -> None:
        self.identity = identity
        # Variantes explícitas habituales de la pronunciación «Nix».
        variants = (*identity.wake_words, "nicks", "nick", "nik")
        self._pattern = re.compile(
            rf"\b({'|'.join(re.escape(word) for word in variants)})\b", re.IGNORECASE
        )

    def detect(self, text: str) -> WakeDetection | None:
        match = self._pattern.search(text)
        if not match:
            return None
        command = (text[:match.start()] + text[match.end():]).strip(" ,.!¿?")
        return WakeDetection(command=command)

    def is_interruption(self, text: str) -> bool:
        normalized = text.casefold().strip(" ,.!¿?")
        stop_words = ("para", "espera", "cállate", "callate", "detente")
        has_wake_word = self.detect(text) is not None
        return any(word in normalized.split() for word in stop_words) and (has_wake_word or normalized in stop_words)
