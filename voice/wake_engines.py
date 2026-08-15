"""Motores de wake word acústicos o basados en transcripción."""

from __future__ import annotations

import os
import threading
from dataclasses import dataclass
from typing import Protocol

from voice.contracts import SpeechRecognizer
from voice.wake_detector import WakeWordDetector


@dataclass(frozen=True)
class WakeEvent:
    command: str = ""
    engine: str = "unknown"
    confidence: float | None = None


class WakeEngine(Protocol):
    def wait(self, cancel_event: threading.Event) -> WakeEvent | None: ...


class TranscriptionWakeEngine:
    """Fallback sin credenciales: detecta NYX después de transcribir voz."""

    def __init__(self, recognizer: SpeechRecognizer, detector: WakeWordDetector) -> None:
        self.recognizer = recognizer
        self.detector = detector

    def wait(self, cancel_event: threading.Event) -> WakeEvent | None:
        result_reader = getattr(self.recognizer, "listen_result", None)
        if result_reader:
            result = result_reader(cancel_event=cancel_event, initial_timeout_seconds=3.0)
            text = result.text if result.is_reliable else ""
        else:
            text = self.recognizer.listen(cancel_event=cancel_event, initial_timeout_seconds=3.0)
        detection = self.detector.detect(text)
        return WakeEvent(detection.command, engine="transcription-fallback") if detection else None


class PorcupineWakeEngine:
    """Wake word acústico local de baja latencia con modelo personalizado .ppn."""

    def __init__(
        self,
        access_key: str,
        keyword_path: str,
        model_path: str | None = None,
        sensitivity: float = 0.55,
    ) -> None:
        self.access_key = access_key
        self.keyword_path = keyword_path
        self.model_path = model_path
        self.sensitivity = sensitivity

    def wait(self, cancel_event: threading.Event) -> WakeEvent | None:
        import pvporcupine
        import sounddevice as sd

        options = {
            "access_key": self.access_key,
            "keyword_paths": [self.keyword_path],
            "sensitivities": [self.sensitivity],
        }
        if self.model_path:
            options["model_path"] = self.model_path
        engine = pvporcupine.create(**options)
        try:
            with sd.InputStream(
                samplerate=engine.sample_rate,
                channels=1,
                dtype="int16",
                blocksize=engine.frame_length,
            ) as stream:
                while not cancel_event.is_set():
                    frame, _overflowed = stream.read(engine.frame_length)
                    if engine.process(frame.reshape(-1).tolist()) >= 0:
                        return WakeEvent(engine="porcupine", confidence=1.0)
        finally:
            engine.delete()
        return None


def create_default_wake_engine(recognizer: SpeechRecognizer, detector: WakeWordDetector) -> WakeEngine:
    """Usa detector acústico sólo cuando su modelo y clave están configurados."""
    access_key = os.getenv("PICOVOICE_ACCESS_KEY")
    keyword_path = os.getenv("NYX_PORCUPINE_KEYWORD_PATH")
    if access_key and keyword_path:
        return PorcupineWakeEngine(
            access_key=access_key,
            keyword_path=keyword_path,
            model_path=os.getenv("NYX_PORCUPINE_MODEL_PATH") or None,
            sensitivity=float(os.getenv("NYX_WAKE_SENSITIVITY", "0.45")),
        )
    return TranscriptionWakeEngine(recognizer, detector)
