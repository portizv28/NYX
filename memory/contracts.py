"""Puerto de persistencia para que JSON pueda sustituirse por SQLite después."""

from __future__ import annotations

from typing import Protocol

from memory.models import MemoryEntry


class MemoryStore(Protocol):
    def save(self, entry: MemoryEntry) -> MemoryEntry: ...

    def get(self, key: str) -> MemoryEntry | None: ...

    def list_entries(self) -> tuple[MemoryEntry, ...]: ...
