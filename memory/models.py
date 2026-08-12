"""Modelos de memoria independientes del sistema de almacenamiento."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class MemoryEntry:
    key: str
    value: str
    category: str = "fact"
    source: str = "user"
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "MemoryEntry":
        return cls(
            key=data["key"],
            value=data["value"],
            category=data.get("category", "fact"),
            source=data.get("source", "user"),
            created_at=data.get("created_at", utc_now()),
            updated_at=data.get("updated_at", utc_now()),
        )
