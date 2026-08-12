"""Cálculo puro de sensibilidad de micrófono, fácil de calibrar y probar."""


def adaptive_threshold(
    ambient_volumes: list[float],
    minimum: float = 0.004,
    multiplier: float = 1.8,
    maximum: float = 0.012,
) -> float:
    if not ambient_volumes:
        return minimum
    noise_floor = sum(ambient_volumes) / len(ambient_volumes)
    return min(maximum, max(minimum, noise_floor * multiplier))
