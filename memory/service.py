"""Casos de uso de memoria, independientes de comandos de lenguaje."""

from __future__ import annotations

from memory.contracts import MemoryStore
from memory.models import MemoryEntry


class MemoryService:
    def __init__(self, store: MemoryStore) -> None:
        self.store = store

    def remember(self, key: str, value: str, category: str = "fact") -> MemoryEntry:
        return self.store.save(MemoryEntry(key=key, value=value, category=category))

    def recall(self, key: str) -> MemoryEntry | None:
        return self.store.get(key)

    def summary(self, limit: int = 20) -> str:
        entries = self.store.list_entries()[-limit:]
        return "\n".join(f"- {entry.key}: {entry.value}" for entry in entries)
