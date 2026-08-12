"""Capacidad documental inicial: Word y Excel sin tocar el cerebro."""

from automation.registry import ActionRegistry, RegisteredAction
from documents.excel_service import ExcelDocumentCreator
from documents.word_service import WordDocumentCreator


class DocumentsCapability:
    identifier = "documents"
    description = "Creación de documentos Word y libros Excel extensible a otros formatos."

    def __init__(self, word_creator=None, excel_creator=None) -> None:
        self.word_creator = word_creator or WordDocumentCreator()
        self.excel_creator = excel_creator or ExcelDocumentCreator()

    def register_actions(self, actions: ActionRegistry) -> None:
        actions.register(
            RegisteredAction(
                name="create_word_document",
                description="Crea un documento Word con el texto indicado.",
                matches=lambda text: text.casefold().startswith("crea documento "),
                execute=self._create_word,
            )
        )
        actions.register(
            RegisteredAction(
                name="create_excel_document",
                description="Crea un libro Excel inicial.",
                matches=lambda text: text.casefold().strip() == "crea excel",
                execute=self._create_excel,
            )
        )

    def _create_word(self, text: str) -> str:
        content = text.strip()[len("crea documento "):].strip()
        artifact = self.word_creator.create(content)
        return f"He creado el documento en {artifact.path}."

    def _create_excel(self, _text: str) -> str:
        artifact = self.excel_creator.create()
        return f"He creado el libro Excel en {artifact.path}."
