"""Estados de alto nivel del asistente.

El núcleo no conoce colores ni widgets: sólo describe qué está haciendo NYX.
"""

from enum import Enum


class AssistantState(str, Enum):
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    IDLE = "idle"


class MicrophoneState(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
