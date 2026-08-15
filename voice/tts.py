"""Proveedores intercambiables de síntesis; la personalidad no vive aquí."""

from __future__ import annotations

import os
import subprocess
import tempfile
import threading
from pathlib import Path
from typing import Protocol


class TTSProvider(Protocol):
    def speak(self, text: str) -> None: ...
    def stop(self) -> None: ...


class Pyttsx3Provider:
    def __init__(self, rate: int, volume: float) -> None:
        self.rate = rate
        self.volume = volume
        self._engine = None
        self._lock = threading.Lock()

    def speak(self, text: str) -> None:
        import pyttsx3

        with self._lock:
            if self._engine is None:
                self._engine = pyttsx3.init()
                self._engine.setProperty("rate", self.rate)
                self._engine.setProperty("volume", self.volume)
                self._select_spanish_voice()
            engine = self._engine
        engine.say(text)
        engine.runAndWait()

    def stop(self) -> None:
        with self._lock:
            if self._engine is not None:
                self._engine.stop()

    def _select_spanish_voice(self) -> None:
        for voice in self._engine.getProperty("voices"):
            details = " ".join(str(value) for value in (getattr(voice, "id", ""), getattr(voice, "name", ""), getattr(voice, "languages", ""))).casefold()
            if "spanish" in details or "español" in details or "es-" in details:
                self._engine.setProperty("voice", voice.id)
                return


class PiperProvider:
    """Adaptador opcional para Piper CLI y un modelo local seleccionado por el usuario."""

    def __init__(self, executable: str, model_path: str) -> None:
        self.executable = executable
        self.model_path = Path(model_path)
        self._process: subprocess.Popen | None = None

    def speak(self, text: str) -> None:
        if not self.model_path.is_file():
            raise RuntimeError("El modelo Piper configurado no existe.")
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as output:
            output_path = Path(output.name)
        try:
            self._process = subprocess.Popen(
                [self.executable, "--model", str(self.model_path), "--output_file", str(output_path)],
                stdin=subprocess.PIPE,
                text=True,
            )
            self._process.communicate(text)
            if self._process.returncode:
                raise RuntimeError("Piper no pudo sintetizar la respuesta.")
            if os.name != "nt":
                raise RuntimeError("La reproducción Piper integrada está disponible actualmente en Windows.")
            import winsound
            winsound.PlaySound(str(output_path), winsound.SND_FILENAME)
        finally:
            self._process = None
            output_path.unlink(missing_ok=True)

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()


def create_tts_provider(engine: str, rate: int, volume: float) -> TTSProvider:
    if engine.casefold() == "piper":
        return PiperProvider(
            executable=os.getenv("NYX_PIPER_EXECUTABLE", "piper"),
            model_path=os.getenv("NYX_PIPER_MODEL_PATH", ""),
        )
    return Pyttsx3Provider(rate=rate, volume=volume)
