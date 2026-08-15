"""Configuración de ejecución leída desde el entorno."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # Permite importar contratos y ejecutar pruebas mínimas sin extras.
    def load_dotenv() -> bool:
        return False


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    ollama_url: str
    ollama_model: str
    wake_sensitivity: float
    wake_cooldown_seconds: float
    stt_engine: str
    stt_model: str
    tts_engine: str
    tts_rate: int
    tts_volume: float
    news_sources_path: str


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
        wake_sensitivity=float(os.getenv("NYX_WAKE_SENSITIVITY", "0.45")),
        wake_cooldown_seconds=float(os.getenv("NYX_WAKE_COOLDOWN_SECONDS", "2.0")),
        stt_engine=os.getenv("NYX_STT_ENGINE", "faster_whisper"),
        stt_model=os.getenv("NYX_WHISPER_MODEL", "base"),
        tts_engine=os.getenv("NYX_TTS_ENGINE", "pyttsx3"),
        tts_rate=int(os.getenv("NYX_TTS_RATE", "155")),
        tts_volume=float(os.getenv("NYX_TTS_VOLUME", "0.9")),
        news_sources_path=os.getenv("NYX_NEWS_SOURCES_PATH", "config/news_sources.json"),
    )


# Conservado para los scripts existentes. El código de aplicación usa Settings.
API_KEY = get_settings().openai_api_key
