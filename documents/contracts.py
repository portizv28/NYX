"""Contratos preparados para PDF, Word, Excel y lectores futuros."""

from typing import Protocol

from documents.models import DocumentArtifact


class DocumentCreator(Protocol):
    def create(self, content: str, name: str | None = None) -> DocumentArtifact: ...


class DocumentReader(Protocol):
    def read(self, path: str) -> str: ...
