"""Acciones registradas de noticias; el cerebro solo ejecuta el registro."""

from __future__ import annotations

from automation.registry import ActionRegistry, RegisteredAction
from news.models import NewsItem
from news.service import NewsService
from news.sources import NewsSourceRepository


class NewsCapability:
    identifier = "news"
    description = "Actualidad RSS configurable, con caché, estado por fuente y referencias conversacionales."

    def __init__(self, sources: NewsSourceRepository | None = None, service: NewsService | None = None) -> None:
        self.sources = sources or NewsSourceRepository()
        self.service = service or NewsService()

    def register_actions(self, actions: ActionRegistry) -> None:
        actions.register(RegisteredAction("news_detail", "Amplía una noticia mostrada recientemente.", self._is_detail_request, self._detail))
        actions.register(RegisteredAction("news_updates", "Consulta novedades de fuentes permitidas.", self._matches, self._execute))

    def refresh(self, text: str = "", force: bool = True):
        category, period = self._query(text)
        return self.service.collect(self.sources.sources(), category=category, period=period, refresh=force)

    @staticmethod
    def _matches(text: str) -> bool:
        normalized = text.casefold()
        return any(token in normalized for token in ("novedad", "noticias", "qué ha pasado", "que ha pasado")) and "nil ojeda" not in normalized

    def _execute(self, text: str) -> str:
        category, period = self._query(text)
        result = self.service.collect(self.sources.sources(), category=category, period=period)
        return self.service.format(result, spoken=True)

    def _is_detail_request(self, text: str) -> bool:
        if not self.service.last_result():
            return False
        normalized = text.casefold()
        return any(token in normalized for token in ("primera", "segunda", "tercera", "cuarta", "háblame más", "hablame más", "cuéntame más", "cuentame más", "amplía", "amplia", "por qué es importante", "porque es importante")) or self.service.resolve_reference(text) is not None

    def _detail(self, text: str) -> str:
        item = self.service.resolve_reference(text)
        if not item:
            return "No he podido identificar la noticia a la que te refieres. Puedes indicarme su número o titular."
        return self._format_detail(item, comprehensive=any(token in text.casefold() for token in ("todo", "detall", "importante")))

    @staticmethod
    def _format_detail(item: NewsItem, comprehensive: bool) -> str:
        summary = item.summary or "La fuente no incluye un resumen adicional en su RSS."
        if not comprehensive:
            return f"{item.title}. Según {item.source}, {summary} Puedes abrir el artículo original en {item.link}."
        return f"Resumen de la información disponible en {item.source}:\n{item.title}\n{summary}\nOrigen: {item.link}"

    @staticmethod
    def _query(text: str) -> tuple[str | None, str]:
        normalized = text.casefold()
        category = next((key for key, token in {"technology": "tecnolog", "science": "ciencia", "economy": "econom"}.items() if token in normalized), None)
        if "ayer" in normalized:
            period = "yesterday"
        elif "3 días" in normalized or "tres días" in normalized or "3 dias" in normalized:
            period = "3days"
        elif "semana" in normalized:
            period = "week"
        elif "hoy" in normalized:
            period = "today"
        else:
            period = "all"
        return category, period


class NilOjedaCapability:
    identifier = "nil_ojeda_tracker"
    description = "Seguimiento público y verificable de Nil Ojeda mediante fuentes permitidas."

    def __init__(self, sources: NewsSourceRepository | None = None, service: NewsService | None = None) -> None:
        self.sources = sources or NewsSourceRepository()
        self.service = service or NewsService()

    def register_actions(self, actions: ActionRegistry) -> None:
        actions.register(RegisteredAction("nil_ojeda_updates", "Consulta novedades públicas sobre Nil Ojeda.", lambda text: "nil ojeda" in text.casefold(), self._execute))

    def _execute(self, text: str) -> str:
        result = self.service.collect(self.sources.trackers())
        message = self.service.format(result, spoken=True)
        return message + " Las referencias de terceros se muestran como tales; no constituyen declaraciones confirmadas por Nil Ojeda."
