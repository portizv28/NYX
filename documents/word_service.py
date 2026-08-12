"""Adaptador de creación de documentos Word."""

from pathlib import Path

from docx import Document

from documents.models import DocumentArtifact


class WordDocumentCreator:
    def create(self, content: str, name: str | None = None) -> DocumentArtifact:
        path = Path(name or "NYX_documento.docx")
        document = Document()
        document.add_paragraph(content)
        document.save(path)
        return DocumentArtifact(path=path, kind="word")
