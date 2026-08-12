"""Capacidad de automatización de escritorio disponible actualmente."""

from automation.default_actions import register_default_actions
from automation.registry import ActionRegistry


class DesktopAutomationCapability:
    identifier = "desktop_automation"
    description = "Apertura de navegador y programas locales conocidos."

    def register_actions(self, actions: ActionRegistry) -> None:
        register_default_actions(actions)
