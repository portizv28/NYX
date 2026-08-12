"""Adaptador temporal de la API ``WakeDetector`` anterior.

La detección real vive en :mod:`voice.service`; este archivo se conserva para
no romper integraciones existentes y se retirará sólo tras una migración
explícita de sus consumidores.
"""

from collections.abc import Callable

from voice.service import VoiceService


class WakeDetector:
    def __init__(self, callback: Callable[[str], None]) -> None:
        self._service = VoiceService(
            on_activated=lambda: None,
            on_command=callback,
            on_command_timeout=lambda: None,
        )

    def start(self) -> None:
        self._service.start()

    def stop(self) -> None:
        self._service.stop()
