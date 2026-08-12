"""Síntesis de voz serializada para NYX."""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable

import pyttsx3

from config.identity import NYX_IDENTITY
from personality.models import VoiceStyle
from personality.profiles import NYX_PROFILE


class SpeechService:
    """Ejecuta una frase cada vez para evitar voces superpuestas."""

    def __init__(self, style: VoiceStyle = NYX_PROFILE.voice) -> None:
        self.style = style
        self._queue: queue.Queue[tuple[str, Callable[[bool], None] | None]] = queue.Queue()
        self._engine_lock = threading.Lock()
        self._engine = None
        self._thread = threading.Thread(target=self._run, daemon=True, name="nyx-speech")
        self._thread.start()

    def speak(self, text: str, on_complete: Callable[[bool], None] | None = None) -> None:
        self._queue.put((NYX_IDENTITY.for_speech(text), on_complete))

    def stop(self) -> None:
        """Solicita detener de inmediato la frase que está sonando."""
        with self._engine_lock:
            if self._engine is not None:
                self._engine.stop()

    def _run(self) -> None:
        engine = None
        while True:
            text, on_complete = self._queue.get()
            succeeded = False
            try:
                if engine is None:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", self.style.rate)
                    engine.setProperty("volume", self.style.volume)
                    self._select_spanish_voice(engine)
                with self._engine_lock:
                    self._engine = engine
                engine.say(text)
                engine.runAndWait()
                succeeded = True
            except Exception as error:
                print("Error de síntesis:", error)
                engine = None
            finally:
                with self._engine_lock:
                    self._engine = None
                try:
                    if on_complete:
                        on_complete(succeeded)
                finally:
                    self._queue.task_done()

    @staticmethod
    def _select_spanish_voice(engine) -> None:
        for voice in engine.getProperty("voices"):
            details = " ".join(str(value) for value in (getattr(voice, "id", ""), getattr(voice, "name", ""), getattr(voice, "languages", ""))).casefold()
            if "spanish" in details or "español" in details or "es-" in details:
                engine.setProperty("voice", voice.id)
                return


_default_speaker = SpeechService()


def hablar(texto: str) -> None:
    """Compatibilidad con el uso funcional anterior."""
    _default_speaker.speak(texto)
