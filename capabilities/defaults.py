"""Composición de capacidades incluidas, fuera del cerebro."""

from automation.capability import DesktopAutomationCapability
from automation.filesystem_capability import FileSystemCapability
from automation.registry import ActionRegistry
from documents.capability import DocumentsCapability
from internet.capability import InternetCapability
from news.capability import NewsCapability, NilOjedaCapability
from news.service import NewsService
from news.sources import NewsSourceRepository
from capabilities.registry import CapabilityRegistry


def create_default_capability_registry(news_service: NewsService | None = None) -> CapabilityRegistry:
    news_service = news_service or NewsService()
    news_sources = NewsSourceRepository()
    capabilities = CapabilityRegistry()
    capabilities.register(InternetCapability())
    capabilities.register(NewsCapability(news_sources, news_service))
    capabilities.register(NilOjedaCapability(news_sources, news_service))
    capabilities.register(DesktopAutomationCapability())
    capabilities.register(FileSystemCapability())
    capabilities.register(DocumentsCapability())
    return capabilities


def create_default_action_registry(news_service: NewsService | None = None) -> ActionRegistry:
    capabilities = create_default_capability_registry(news_service)
    actions = ActionRegistry()
    capabilities.install_actions(actions)
    return actions
