"""Interpreta comandos sencillos de memoria sin acoplarlos al cerebro."""

from __future__ import annotations

import re

from memory.service import MemoryService


class MemoryIntentHandler:
    def __init__(self, memory: MemoryService) -> None:
        self.memory = memory

    def respond(self, text: str) -> str | None:
        remember = re.match(
            r"^recuerda que (?:mi )?(.+?) es (.+?)[.!]?$", text.strip(), flags=re.IGNORECASE
        )
        if remember:
            key, value = remember.groups()
            entry = self.memory.remember(key.strip(), value.strip())
            return f"Recordaré que tu {entry.key} es {entry.value}."

        recall = re.match(r"^¿?qué (.+?) tengo[?]?$", text.strip(), flags=re.IGNORECASE)
        if recall:
            key = recall.group(1).strip()
            entry = self.memory.recall(key)
            if entry:
                return f"Tu {entry.key} es {entry.value}."
            return f"Aún no tengo información sobre tu {key}."
        return None
