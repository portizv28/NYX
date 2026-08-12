"""Composición de capacidades incluidas, fuera del cerebro."""

from automation.capability import DesktopAutomationCapability
from automation.filesystem_capability import FileSystemCapability
from automation.registry import ActionRegistry
from documents.capability import DocumentsCapability
from internet.capability import InternetCapability
from capabilities.registry import CapabilityRegistry


def create_default_capability_registry() -> CapabilityRegistry:
    capabilities = CapabilityRegistry()
    capabilities.register(InternetCapability())
    capabilities.register(DesktopAutomationCapability())
    capabilities.register(FileSystemCapability())
    capabilities.register(DocumentsCapability())
    return capabilities


def create_default_action_registry() -> ActionRegistry:
    capabilities = create_default_capability_registry()
    actions = ActionRegistry()
    capabilities.install_actions(actions)
    return actions
