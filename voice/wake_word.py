"""Adaptador temporal para la API de palabra de activación original."""

from collections.abc import Callable

from voice.service import VoiceService


class WakeWord:
    def __init__(self, callback: Callable[[], None]) -> None:
        self._service = VoiceService(
            on_activated=callback,
            on_command=lambda _text: None,
            on_command_timeout=lambda: None,
        )

    def iniciar(self) -> None:
        self._service.start()

    def detener(self) -> None:
        self._service.stop()
