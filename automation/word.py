"""Compatibilidad con la utilidad original; la implementación vive en documents."""

from documents.word_service import WordDocumentCreator


def crear_documento(texto, nombre="NYX_documento.docx"):
    return str(WordDocumentCreator().create(texto, nombre).path)
