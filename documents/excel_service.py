"""Adaptador de creación y escritura básica de libros Excel."""

from pathlib import Path

from openpyxl import Workbook

from documents.models import DocumentArtifact


class ExcelDocumentCreator:
    def create(self, content: str = "", name: str | None = None) -> DocumentArtifact:
        path = Path(name or "NYX_excel.xlsx")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Datos NYX"
        sheet["A1"] = content or "Creado por NYX"
        workbook.save(path)
        return DocumentArtifact(path=path, kind="excel")

    def append_rows(self, name: str, rows) -> DocumentArtifact:
        workbook = Workbook()
        sheet = workbook.active
        for row in rows:
            sheet.append(row)
        path = Path(name)
        workbook.save(path)
        return DocumentArtifact(path=path, kind="excel")
