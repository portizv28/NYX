"""Composición de la aplicación de escritorio actual.

Aquí se eligen implementaciones concretas. El cerebro no sabe si se ejecuta en
Windows, una Raspberry Pi o un futuro servidor doméstico.
"""

from ai.router import create_default_router
from brain.core import NyxBrain
from capabilities.defaults import create_default_action_registry, create_default_capability_registry
from core.store import StateStore
from memory.json_store import JsonMemoryStore
from memory.service import MemoryService
from personality.adapters import PersonalityAwareProcessor, PersonalityAwareProvider
from personality.engine import PersonalityEngine
from personality.profiles import NYX_PROFILE
from pathlib import Path


def create_desktop_brain(state_store: StateStore | None = None) -> PersonalityAwareProcessor:
    personality = PersonalityEngine(NYX_PROFILE)
    router = create_default_router()
    capabilities = create_default_capability_registry()
    if state_store:
        state_store.update(
            memory_available=True,
            capabilities=tuple(capability.identifier for capability in capabilities.list_capabilities()),
        )

        def report_model(decision) -> None:
            state_store.update(active_model="OpenAI" if decision.provider == "external" else "Ollama")

        router.subscribe_decisions(report_model)

    brain = NyxBrain(
        router=PersonalityAwareProvider(router, personality),
        actions=create_default_action_registry(),
        memory=MemoryService(JsonMemoryStore(Path(__file__).resolve().parents[1] / "memory" / "memory.json")),
        on_action=(lambda action: state_store.update(last_action=action)) if state_store else None,
    )
    return PersonalityAwareProcessor(brain, personality)
