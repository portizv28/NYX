"""Compatibilidad con la utilidad original; la implementación vive en documents."""

from documents.excel_service import ExcelDocumentCreator


def crear_excel(nombre="NYX_excel.xlsx"):
    return str(ExcelDocumentCreator().create(name=nombre).path)


def escribir_datos(nombre, datos):
    return str(ExcelDocumentCreator().append_rows(nombre, datos).path)
