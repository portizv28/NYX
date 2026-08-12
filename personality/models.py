"""Modelos configurables de personalidad y expresión de voz."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class InteractionMode(str, Enum):
    PROFESSIONAL = "professional"
    EVERYDAY = "everyday"


@dataclass(frozen=True)
class VoiceStyle:
    rate: int = 165
    volume: float = 1.0


@dataclass(frozen=True)
class PersonalityProfile:
    identifier: str
    display_name: str
    user_name: str
    core_traits: tuple[str, ...]
    professional_guidance: str
    everyday_guidance: str
    humor_guidance: str
    voice: VoiceStyle
