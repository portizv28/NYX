"""Configuración de ejecución leída desde el entorno."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    openai_api_key: str | None
    openai_model: str
    ollama_url: str
    ollama_model: str


def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        ollama_url=os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
    )


# Conservado para los scripts existentes. El código de aplicación usa Settings.
API_KEY = get_settings().openai_api_key
