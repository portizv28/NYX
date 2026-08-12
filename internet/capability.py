"""Capacidad de Internet que registra acciones sin modificar NyxBrain."""

from automation.registry import ActionRegistry, RegisteredAction
from internet.providers import BrowserSearchProvider, UrlPageReader
from internet.service import InternetService


class InternetCapability:
    identifier = "internet"
    description = "Búsqueda web y lectura de páginas mediante proveedores intercambiables."

    def __init__(self, service: InternetService | None = None) -> None:
        self.service = service or InternetService(BrowserSearchProvider(), UrlPageReader())

    def register_actions(self, actions: ActionRegistry) -> None:
        actions.register(
            RegisteredAction(
                name="web_search",
                description="Busca una consulta en el navegador predeterminado.",
                matches=lambda text: text.casefold().startswith("busca "),
                execute=self._search,
            )
        )

    def _search(self, text: str) -> str:
        query = text.strip()[len("busca "):].strip()
        result = self.service.search(query)[0]
        return f"He abierto una búsqueda de {query}."
