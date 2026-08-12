"""Contratos de reconocimiento y detección independientes de motores concretos."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RecognitionResult:
    text: str
    no_speech_probability: float = 0.0
    average_log_probability: float = 0.0

    @property
    def is_reliable(self) -> bool:
        return bool(self.text.strip()) and self.no_speech_probability < 0.65 and self.average_log_probability >= -1.2


class SpeechRecognizer(Protocol):
    def listen(
        self,
        cancel_event: threading.Event | None = None,
        initial_timeout_seconds: float = 20,
    ) -> str: ...

    def listen_result(
        self,
        cancel_event: threading.Event | None = None,
        initial_timeout_seconds: float = 20,
    ) -> RecognitionResult: ...
