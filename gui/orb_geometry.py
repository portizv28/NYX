"""Geometría pura de la representación visual de NYX.

Mantenerla fuera de Tk permite garantizar y probar que el anillo no toca la
esfera, independientemente del tamaño de ventana o de la animación.
"""

from __future__ import annotations

from dataclasses import dataclass

from core.state import AssistantState


# Arcos verticales simétricos: huecos centrados arriba (90º) y abajo (270º).
LEFT_SEGMENT = (125, 110)
RIGHT_SEGMENT = (305, 110)


@dataclass(frozen=True)
class OrbGeometry:
    center_x: float
    center_y: float
    inner_radius: float
    ring_center_radius: float
    ring_thickness: float
    gap: float

    @property
    def ring_inner_radius(self) -> float:
        return self.ring_center_radius - self.ring_thickness / 2

    @property
    def separation(self) -> float:
        return self.ring_inner_radius - self.inner_radius


def geometry_for(state: AssistantState, phase: float, center_x: float, center_y: float, base_radius: float) -> OrbGeometry:
    """Devuelve una geometría centrada con hueco mínimo de 16 px escalados."""
    profile = {
        AssistantState.SLEEPING: (0.025, 0.028),
        AssistantState.LISTENING: (0.035, 0.075),
        AssistantState.THINKING: (0.018, 0.055),
        AssistantState.SPEAKING: (0.030, 0.095),
        AssistantState.IDLE: (0.020, 0.040),
    }[state]
    import math

    inner_breath, ring_breath = profile
    inner_radius = base_radius * (1 + math.sin(phase * 0.72) * inner_breath)
    gap = max(16.0, base_radius * 0.25)
    thickness = max(12.0, base_radius * 0.22)
    # El anillo cambia solo hacia fuera; su borde interior permanece separado.
    ring_inner = inner_radius + gap + max(0.0, math.sin(phase) * base_radius * ring_breath)
    return OrbGeometry(center_x, center_y, inner_radius, ring_inner + thickness / 2, thickness, gap)
