"""Estado observable, independiente de interfaz y plataforma."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from threading import RLock

from core.state import AssistantState, MicrophoneState


@dataclass(frozen=True)
class AssistantSnapshot:
    state: AssistantState = AssistantState.SLEEPING
    activity: str = "Esperando la palabra de activación"
    microphone: MicrophoneState = MicrophoneState.ACTIVE
    active_model: str = "Ollama"
    memory_available: bool = False
    capabilities: tuple[str, ...] = ()
    last_action: str = "Ninguna"
    updated_at: str = ""


StateObserver = Callable[[AssistantSnapshot], None]


class StateStore:
    """Única fuente de verdad y punto de suscripción para el estado de NYX."""

    def __init__(self, initial: AssistantSnapshot | None = None) -> None:
        self._lock = RLock()
        self._snapshot = initial or AssistantSnapshot(updated_at=self._now())
        self._observers: dict[int, StateObserver] = {}
        self._next_observer_id = 0

    def snapshot(self) -> AssistantSnapshot:
        with self._lock:
            return self._snapshot

    def update(self, **changes) -> AssistantSnapshot:
        with self._lock:
            self._snapshot = replace(self._snapshot, **changes, updated_at=self._now())
            snapshot = self._snapshot
            observers = tuple(self._observers.values())
        for observer in observers:
            try:
                observer(snapshot)
            except Exception as error:
                print("Error notificando el estado de NYX:", error)
        return snapshot

    def subscribe(self, observer: StateObserver, emit_current: bool = False) -> Callable[[], None]:
        with self._lock:
            identifier = self._next_observer_id
            self._next_observer_id += 1
            self._observers[identifier] = observer
            current = self._snapshot
        if emit_current:
            observer(current)

        def unsubscribe() -> None:
            with self._lock:
                self._observers.pop(identifier, None)

        return unsubscribe

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()
