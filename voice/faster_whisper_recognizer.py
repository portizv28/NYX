"""Adaptador faster-whisper con VAD para órdenes más rápidas y limpias."""

from __future__ import annotations

import numpy as np

from voice.contracts import RecognitionResult
from voice.listener import WhisperListener


class FasterWhisperRecognizer(WhisperListener):
    def __init__(self, model_name: str = "base", compute_type: str = "int8", **kwargs) -> None:
        super().__init__(model_name=model_name, **kwargs)
        self.compute_type = compute_type

    def _get_model(self):
        with self._model_lock:
            if self._model is None:
                from faster_whisper import WhisperModel

                self._model = WhisperModel(self.model_name, device="cpu", compute_type=self.compute_type)
            return self._model

    def _transcribe(self, audio: np.ndarray) -> RecognitionResult:
        segments, _info = self._get_model().transcribe(
            audio,
            language="es",
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt="La palabra de activación es Nix, también escrita NYX.",
            beam_size=5,
        )
        items = list(segments)
        if not items:
            return RecognitionResult("")
        weights = [max(0.1, item.end - item.start) for item in items]
        total = sum(weights)
        text = " ".join(item.text.strip() for item in items).strip()
        no_speech = sum(getattr(item, "no_speech_prob", 0.0) * weight for item, weight in zip(items, weights)) / total
        log_probability = sum(getattr(item, "avg_logprob", 0.0) * weight for item, weight in zip(items, weights)) / total
        return RecognitionResult(text, no_speech, log_probability)
