"""CLI explícita para gestionar el arranque automático de NYX."""

from __future__ import annotations

import argparse

from integrations.windows.startup import WindowsRunKeyStartupManager


def main() -> int:
    parser = argparse.ArgumentParser(description="Gestiona el inicio automático de NYX en Windows.")
    parser.add_argument("command", choices=("enable", "disable", "status"))
    args = parser.parse_args()
    manager = WindowsRunKeyStartupManager()

    if args.command == "enable":
        manager.enable()
        print("Inicio automático de NYX activado.")
    elif args.command == "disable":
        manager.disable()
        print("Inicio automático de NYX desactivado.")
    else:
        print("activado" if manager.is_enabled() else "desactivado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
