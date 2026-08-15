"""Diagnóstico silencioso del pipeline de voz.

No muestra mensajes en la interfaz: mantiene una ventana acotada de eventos para
la pantalla de depuración, los logs y las pruebas.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VoiceDiagnosticEvent:
    name: str
    timestamp: float
    details: dict[str, Any]


class VoiceDiagnostics:
    def __init__(self, capacity: int = 200) -> None:
        self._events: deque[VoiceDiagnosticEvent] = deque(maxlen=capacity)
        self._logger = logging.getLogger("nyx.voice")

    def record(self, name: str, **details: Any) -> None:
        event = VoiceDiagnosticEvent(name=name, timestamp=time.time(), details=details)
        self._events.append(event)
        self._logger.debug("%s %s", name, details)

    def recent(self) -> tuple[VoiceDiagnosticEvent, ...]:
        return tuple(self._events)
