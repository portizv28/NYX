"""Almacén efímero útil para pruebas y ejecuciones sin persistencia."""

from memory.models import MemoryEntry


class InMemoryStore:
    def __init__(self) -> None:
        self._entries: dict[str, MemoryEntry] = {}

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        self._entries[entry.key.casefold().strip()] = entry
        return entry

    def get(self, key: str) -> MemoryEntry | None:
        return self._entries.get(key.casefold().strip())

    def list_entries(self) -> tuple[MemoryEntry, ...]:
        return tuple(self._entries.values())
