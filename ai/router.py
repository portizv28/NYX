"""Decisión transparente entre IA local y proveedor externo."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from ai.contracts import AIProvider


@dataclass(frozen=True)
class RoutingDecision:
    provider: str
    reason: str


@dataclass
class RoutingPolicy:
    """Reglas conservadoras: local es siempre la opción predeterminada."""

    complexity_keywords: set[str] = field(
        default_factory=lambda: {
            "programa", "código", "codigo", "algoritmo", "razona", "razonamiento",
            "analiza", "análisis", "explica en detalle", "resumen", "creativo",
            "estrategia", "comparativa", "plan detallado",
        }
    )
    long_request_characters: int = 350

    def choose(self, text: str, external_available: bool) -> RoutingDecision:
        if not external_available:
            return RoutingDecision("local", "El proveedor externo no está configurado.")

        normalized = text.casefold()
        if len(normalized) >= self.long_request_characters:
            return RoutingDecision("external", "La solicitud es extensa.")
        if any(keyword in normalized for keyword in self.complexity_keywords):
            return RoutingDecision("external", "La solicitud requiere razonamiento o creatividad avanzada.")
        return RoutingDecision("local", "Consulta normal: se prioriza privacidad y rapidez local.")


class HybridRouter:
    name = "hybrid"

    def __init__(
        self,
        local: AIProvider,
        external: AIProvider | None = None,
        policy: RoutingPolicy | None = None,
    ) -> None:
        self.local = local
        self.external = external
        self.policy = policy or RoutingPolicy()
        self.last_decision: RoutingDecision | None = None
        self._decision_observers: list[Callable[[RoutingDecision], None]] = []

    def subscribe_decisions(self, observer: Callable[[RoutingDecision], None]) -> Callable[[], None]:
        self._decision_observers.append(observer)

        def unsubscribe() -> None:
            if observer in self._decision_observers:
                self._decision_observers.remove(observer)

        return unsubscribe

    def _publish_decision(self, decision: RoutingDecision) -> None:
        for observer in tuple(self._decision_observers):
            observer(decision)

    def ask(self, text: str) -> str:
        decision = self.policy.choose(text, external_available=self.external is not None)
        self.last_decision = decision
        if decision.provider == "local":
            self._publish_decision(decision)
            return self.local.ask(text)

        try:
            self._publish_decision(decision)
            return self.external.ask(text)  # type: ignore[union-attr]
        except Exception as error:
            print("Proveedor externo no disponible; se usa IA local:", error)
            self.last_decision = RoutingDecision("local", "Fallback tras error del proveedor externo.")
            self._publish_decision(self.last_decision)
            return self.local.ask(text)

    def preguntar(self, texto: str) -> str:
        """Alias de compatibilidad con la nomenclatura inicial."""
        return self.ask(texto)


def create_default_router() -> HybridRouter:
    """Crea proveedores sólo al iniciar la aplicación, no al importar módulos."""
    from ai.local import LocalAI
    from config.settings import get_settings

    settings = get_settings()
    external = None
    if settings.openai_api_key:
        from ai.gpt import GPT

        external = GPT(settings.openai_api_key, model=settings.openai_model)
    return HybridRouter(
        local=LocalAI(url=settings.ollama_url, model=settings.ollama_model),
        external=external,
    )
