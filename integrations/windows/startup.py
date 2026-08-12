"""Inicio automático de NYX mediante la clave de usuario de Windows.

No inicia nada por sí mismo: el usuario debe ejecutarlo explícitamente desde la
CLI. Cuando NYX se empaquete, este módulo usará el ejecutable congelado.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "NYX"


@dataclass(frozen=True)
class StartupCommand:
    executable: Path
    arguments: tuple[str, ...]

    @property
    def value(self) -> str:
        return subprocess.list2cmdline([str(self.executable), *self.arguments])

    @classmethod
    def for_current_installation(cls) -> "StartupCommand":
        if getattr(sys, "frozen", False):
            return cls(Path(sys.executable), ())

        root = Path(__file__).resolve().parents[2]
        interpreter = Path(sys.executable)
        windowed_interpreter = interpreter.with_name("pythonw.exe")
        if windowed_interpreter.exists():
            interpreter = windowed_interpreter
        return cls(interpreter, (str(root / "main.py"),))


class WindowsRunKeyStartupManager:
    def __init__(
        self,
        command: StartupCommand | None = None,
        value_name: str = VALUE_NAME,
        registry=None,
    ) -> None:
        if registry is None:
            if sys.platform != "win32":
                raise RuntimeError("El inicio automático de Windows sólo está disponible en Windows.")
            import winreg

            registry = winreg
        self._registry = registry
        self.command = command or StartupCommand.for_current_installation()
        self.value_name = value_name

    def enable(self) -> None:
        with self._registry.CreateKey(self._registry.HKEY_CURRENT_USER, RUN_KEY) as key:
            self._registry.SetValueEx(key, self.value_name, 0, self._registry.REG_SZ, self.command.value)

    def disable(self) -> None:
        try:
            with self._registry.OpenKey(
                self._registry.HKEY_CURRENT_USER, RUN_KEY, 0, self._registry.KEY_SET_VALUE
            ) as key:
                self._registry.DeleteValue(key, self.value_name)
        except FileNotFoundError:
            return

    def is_enabled(self) -> bool:
        try:
            with self._registry.OpenKey(self._registry.HKEY_CURRENT_USER, RUN_KEY) as key:
                self._registry.QueryValueEx(key, self.value_name)
            return True
        except FileNotFoundError:
            return False
