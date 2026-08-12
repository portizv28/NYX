"""Contrato portable de inicio automático."""

from typing import Protocol


class StartupManager(Protocol):
    def enable(self) -> None: ...

    def disable(self) -> None: ...

    def is_enabled(self) -> bool: ...
