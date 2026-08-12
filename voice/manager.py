"""Adaptador temporal para ``VoiceManager``; usar ``VoiceService`` nuevo."""

from collections.abc import Callable

from voice.service import VoiceService


class VoiceManager:
    def __init__(self, callback: Callable[[str], None]) -> None:
        self._service = VoiceService(
            on_activated=lambda: None,
            on_command=callback,
            on_command_timeout=lambda: None,
        )

    def iniciar(self) -> None:
        self._service.start()

    def detener(self) -> None:
        self._service.stop()
