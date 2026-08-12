"""Implementación JSON versionada y compatible con el formato inicial."""

from __future__ import annotations

import json
from pathlib import Path

from memory.models import MemoryEntry, utc_now


class JsonMemoryStore:
    VERSION = 1

    def __init__(self, path: str | Path = "memory/memory.json") -> None:
        self.path = Path(path)

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        entries = list(self.list_entries())
        key = entry.key.casefold().strip()
        replacement = MemoryEntry(
            key=entry.key.strip(),
            value=entry.value.strip(),
            category=entry.category,
            source=entry.source,
            created_at=entry.created_at,
            updated_at=utc_now(),
        )
        for index, existing in enumerate(entries):
            if existing.key.casefold().strip() == key:
                replacement = MemoryEntry(
                    key=replacement.key,
                    value=replacement.value,
                    category=replacement.category,
                    source=replacement.source,
                    created_at=existing.created_at,
                    updated_at=replacement.updated_at,
                )
                entries[index] = replacement
                self._write(entries)
                return replacement
        entries.append(replacement)
        self._write(entries)
        return replacement

    def get(self, key: str) -> MemoryEntry | None:
        normalized = key.casefold().strip()
        return next(
            (entry for entry in self.list_entries() if entry.key.casefold().strip() == normalized),
            None,
        )

    def list_entries(self) -> tuple[MemoryEntry, ...]:
        data = self._read()
        return tuple(MemoryEntry.from_dict(item) for item in data["entries"])

    def _read(self) -> dict[str, object]:
        if not self.path.exists():
            return {"version": self.VERSION, "entries": []}
        with self.path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
        if isinstance(raw, dict) and "entries" in raw:
            return raw
        # Migración transparente de la memoria inicial: {"clave": "valor"}.
        if isinstance(raw, dict):
            return {
                "version": self.VERSION,
                "entries": [MemoryEntry(key=key, value=str(value)).to_dict() for key, value in raw.items()],
            }
        raise ValueError("El archivo de memoria tiene un formato no reconocido.")

    def _write(self, entries: list[MemoryEntry]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                {"version": self.VERSION, "entries": [entry.to_dict() for entry in entries]},
                file,
                indent=2,
                ensure_ascii=False,
            )
        temporary_path.replace(self.path)
