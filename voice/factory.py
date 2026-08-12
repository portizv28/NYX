"""Selección de reconocimiento configurable con fallback seguro."""

from __future__ import annotations

import os


def create_default_recognizer():
    engine = os.getenv("NYX_STT_ENGINE", "faster_whisper").casefold()
    model = os.getenv("NYX_WHISPER_MODEL", "base")
    if engine == "faster_whisper":
        try:
            import faster_whisper  # noqa: F401
            from voice.faster_whisper_recognizer import FasterWhisperRecognizer

            return FasterWhisperRecognizer(model_name=model)
        except ImportError:
            print("faster-whisper no está instalado; se usa Whisper estándar.")
    from voice.listener import WhisperListener

    return WhisperListener(model_name=model)
