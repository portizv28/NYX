"""Acciones no destructivas de archivos y carpetas."""

from automation.explorer import abrir_explorador
from automation.files import crear_carpeta, listar_archivos
from automation.registry import ActionRegistry, RegisteredAction


class FileSystemCapability:
    identifier = "filesystem"
    description = "Operaciones no destructivas de carpetas y exploración de archivos."

    def register_actions(self, actions: ActionRegistry) -> None:
        actions.register(
            RegisteredAction(
                name="create_folder",
                description="Crea una carpeta.",
                matches=lambda text: text.casefold().startswith("crea carpeta "),
                execute=self._create_folder,
            )
        )
        actions.register(
            RegisteredAction(
                name="list_files",
                description="Lista archivos de una carpeta.",
                matches=lambda text: text.casefold().strip() == "lista archivos",
                execute=self._list_files,
            )
        )
        actions.register(
            RegisteredAction(
                name="open_folder",
                description="Abre una carpeta en el explorador.",
                matches=lambda text: text.casefold().startswith("abre carpeta "),
                execute=self._open_folder,
            )
        )

    def _create_folder(self, text: str) -> str:
        path = text.strip()[len("crea carpeta "):].strip()
        crear_carpeta(path)
        return f"He creado la carpeta {path}."

    def _list_files(self, _text: str) -> str:
        files = listar_archivos()
        if not files:
            return "No hay archivos en la carpeta actual."
        visible = ", ".join(files[:20])
        suffix = " …" if len(files) > 20 else ""
        return f"Archivos: {visible}{suffix}"

    def _open_folder(self, text: str) -> str:
        path = text.strip()[len("abre carpeta "):].strip()
        abrir_explorador(path)
        return f"Abriendo la carpeta {path}."
