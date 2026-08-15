"""Calibración manual de ruido ambiente; nunca se ejecuta al iniciar NYX."""

from __future__ import annotations

import math
from dataclasses import dataclass

from voice.sensitivity import adaptive_threshold


@dataclass(frozen=True)
class NoiseCalibration:
    rms_average: float
    rms_peak: float
    recommended_threshold: float


def calibrate_noise(seconds: float = 4.0, sample_rate: int = 16_000) -> NoiseCalibration:
    import numpy as np
    import sounddevice as sd

    samples = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()
    blocks = np.array_split(samples.reshape(-1), max(1, int(seconds * 4)))
    rms = [math.sqrt(float(np.mean(block * block))) for block in blocks if len(block)]
    return NoiseCalibration(
        rms_average=sum(rms) / len(rms),
        rms_peak=max(rms),
        recommended_threshold=adaptive_threshold(rms),
    )
