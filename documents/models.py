"""Resultado neutral de una operación documental."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DocumentArtifact:
    path: Path
    kind: str
