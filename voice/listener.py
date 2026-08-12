"""Reconocimiento de voz por flujo con Whisper, sin archivos temporales."""

from __future__ import annotations

import threading
import time
import os

import numpy as np
import sounddevice as sd
import whisper
from voice.sensitivity import adaptive_threshold
from voice.contracts import RecognitionResult


class WhisperListener:
    """Graba una frase y la transcribe; no decide activación ni conversación."""

    def __init__(
        self,
        model_name: str | None = None,
        sample_rate: int = 16_000,
        minimum_threshold: float = 0.004,
        noise_multiplier: float = 1.8,
        maximum_threshold: float = 0.012,
        silence_seconds: float = 0.75,
        block_seconds: float = 0.2,
    ) -> None:
        self.model_name = model_name or os.getenv("NYX_WHISPER_MODEL", "base")
        self.sample_rate = sample_rate
        self.minimum_threshold = minimum_threshold
        self.noise_multiplier = noise_multiplier
        self.maximum_threshold = maximum_threshold
        self.silence_seconds = silence_seconds
        self.block_seconds = block_seconds
        self._model = None
        self._model_lock = threading.Lock()

    def calculate_threshold(self, ambient_volumes: list[float]) -> float:
        """Ajusta sensibilidad a cada entorno sin ignorar voces suaves."""
        return adaptive_threshold(
            ambient_volumes,
            minimum=self.minimum_threshold,
            multiplier=self.noise_multiplier,
            maximum=self.maximum_threshold,
        )

    def _get_model(self):
        with self._model_lock:
            if self._model is None:
                self._model = whisper.load_model(self.model_name)
            return self._model

    def listen(
        self,
        cancel_event: threading.Event | None = None,
        initial_timeout_seconds: float = 20,
    ) -> str:
        return self.listen_result(cancel_event, initial_timeout_seconds).text

    def listen_result(
        self,
        cancel_event: threading.Event | None = None,
        initial_timeout_seconds: float = 20,
    ) -> RecognitionResult:
        """Captura una sola intervención mediante un flujo de audio persistente."""
        block_size = int(self.block_seconds * self.sample_rate)
        silence_limit = max(1, int(self.silence_seconds / self.block_seconds))
        blocks: list[np.ndarray] = []
        recording = False
        silence_blocks = 0
        started_at = time.monotonic()
        ambient_volumes: list[float] = []
        threshold = self.minimum_threshold

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=block_size,
        ) as stream:
            while not cancel_event or not cancel_event.is_set():
                if not recording and time.monotonic() - started_at >= initial_timeout_seconds:
                    return RecognitionResult("")
                block, _overflowed = stream.read(block_size)
                volume = float(np.abs(block).mean())
                if not recording:
                    ambient_volumes.append(volume)
                    # Tras unas décimas de segundo, el entorno ajusta el umbral.
                    if len(ambient_volumes) >= 3:
                        threshold = self.calculate_threshold(ambient_volumes[-10:])
                if volume > threshold:
                    recording = True
                    silence_blocks = 0
                    blocks.append(block.copy())
                elif recording:
                    blocks.append(block.copy())
                    silence_blocks += 1
                    if silence_blocks >= silence_limit:
                        break

        if not blocks or (cancel_event and cancel_event.is_set()):
            return RecognitionResult("")
        audio = np.concatenate(blocks, axis=0).reshape(-1)
        return self._transcribe(audio)

    def _transcribe(self, audio: np.ndarray) -> RecognitionResult:
        result = self._get_model().transcribe(
            audio,
            language="es",
            fp16=False,
            initial_prompt="La palabra de activación del asistente es Nix, también escrita NYX.",
        )
        segments = result.get("segments", [])
        if not segments:
            return RecognitionResult(result["text"].strip(), no_speech_probability=1.0)
        weights = [max(0.1, segment.get("end", 0) - segment.get("start", 0)) for segment in segments]
        weight = sum(weights)
        no_speech = sum(segment.get("no_speech_prob", 0.0) * item_weight for segment, item_weight in zip(segments, weights)) / weight
        log_probability = sum(segment.get("avg_logprob", 0.0) * item_weight for segment, item_weight in zip(segments, weights)) / weight
        return RecognitionResult(result["text"].strip(), no_speech, log_probability)


_default_listener = WhisperListener()


def escuchar() -> str:
    """Compatibilidad con scripts existentes; preferir ``WhisperListener``."""
    return _default_listener.listen()
