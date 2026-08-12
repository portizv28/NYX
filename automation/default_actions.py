"""Acciones disponibles por defecto en la versión actual de NYX."""

from automation.browser import abrir_google, abrir_web, abrir_youtube
from automation.launcher import abrir_programa
from automation.registry import ActionRegistry, RegisteredAction


def _matches_open_program(text: str) -> bool:
    return text.casefold().startswith("abre ") and len(text.strip()) > len("abre ")


def _open_program(text: str) -> str:
    program = text.strip()[len("abre "):].strip()
    return abrir_programa(program)


def _matches_open_google(text: str) -> bool:
    return text.casefold().strip() == "abre google"


def _open_google(_text: str) -> str:
    abrir_google()
    return "Abriendo Google."


def _matches_open_youtube(text: str) -> bool:
    return text.casefold().strip() == "abre youtube"


def _open_youtube(_text: str) -> str:
    abrir_youtube()
    return "Abriendo YouTube."


def _matches_open_google_docs(text: str) -> bool:
    return text.casefold().strip() in {"abre google docs", "abre documentos de google"}


def _open_google_docs(_text: str) -> str:
    abrir_web("https://docs.google.com")
    return "Abriendo Google Docs."


def register_default_actions(registry: ActionRegistry) -> None:
    registry.register(
        RegisteredAction(
            name="open_google_docs",
            description="Abre Google Docs en el navegador predeterminado.",
            matches=_matches_open_google_docs,
            execute=_open_google_docs,
        )
    )
    registry.register(
        RegisteredAction(
            name="open_google",
            description="Abre Google en el navegador predeterminado.",
            matches=_matches_open_google,
            execute=_open_google,
        )
    )
    registry.register(
        RegisteredAction(
            name="open_youtube",
            description="Abre YouTube en el navegador predeterminado.",
            matches=_matches_open_youtube,
            execute=_open_youtube,
        )
    )
    registry.register(
        RegisteredAction(
            name="open_program",
            description="Abre uno de los programas conocidos por NYX.",
            matches=_matches_open_program,
            execute=_open_program,
        )
    )


def create_default_registry() -> ActionRegistry:
    registry = ActionRegistry()
    register_default_actions(registry)
    return registry
