"""Síntesis de voz serializada y desacoplada del proveedor concreto."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable

from config.identity import NYX_IDENTITY
from config.settings import get_settings
from personality.models import VoiceStyle
from personality.profiles import NYX_PROFILE
from voice.tts import TTSProvider, create_tts_provider


class SpeechService:
    """Ejecuta una frase cada vez y permite cambiar de motor sin tocar NYX."""

    def __init__(self, style: VoiceStyle = NYX_PROFILE.voice, provider: TTSProvider | None = None) -> None:
        settings = get_settings()
        self.style = style
        self.provider = provider or create_tts_provider(settings.tts_engine, settings.tts_rate or style.rate, settings.tts_volume)
        self._queue: queue.Queue[tuple[str, Callable[[bool], None] | None]] = queue.Queue()
        self._muted = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True, name="nyx-speech")
        self._thread.start()

    def speak(self, text: str, on_complete: Callable[[bool], None] | None = None) -> None:
        self._queue.put((NYX_IDENTITY.for_speech(text), on_complete))

    def stop(self) -> None:
        self.provider.stop()

    @property
    def muted(self) -> bool:
        return self._muted.is_set()

    def set_muted(self, muted: bool) -> None:
        if muted:
            self._muted.set()
            self.stop()
        else:
            self._muted.clear()

    def toggle_muted(self) -> bool:
        self.set_muted(not self.muted)
        return self.muted

    def _run(self) -> None:
        while True:
            text, on_complete = self._queue.get()
            succeeded = False
            try:
                if not self.muted:
                    self.provider.speak(text)
                succeeded = True
            except Exception as error:
                print("Error de síntesis:", error)
            finally:
                if on_complete:
                    on_complete(succeeded)
                self._queue.task_done()


_default_speaker = SpeechService()


def hablar(texto: str) -> None:
    """Compatibilidad con el uso funcional anterior."""
    _default_speaker.speak(texto)
