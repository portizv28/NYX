"""Adaptador opcional de bandeja del sistema para el escritorio Windows."""

from __future__ import annotations

import threading
from collections.abc import Callable


class WindowsTrayIntegration:
    """Conecta un controlador de escritorio a pystray sin acoplarlo a NYX."""

    def __init__(
        self,
        open_center: Callable[[str], None],
        toggle_listening: Callable[[], None],
        shutdown: Callable[[], None],
        status: Callable[[], str],
    ) -> None:
        self.open_center = open_center
        self.toggle_listening = toggle_listening
        self.shutdown = shutdown
        self.status = status
        self._icon = None

    def start(self) -> bool:
        """Inicia la bandeja si pystray está disponible; nunca bloquea NYX."""
        try:
            import pystray
            from PIL import Image, ImageDraw
        except ImportError:
            print("Bandeja de NYX no disponible: instala pystray.")
            return False

        image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill="#00BFFF", outline="#BFEFFF", width=3)
        draw.ellipse((22, 22, 42, 42), fill="#050505")
        menu = pystray.Menu(
            pystray.MenuItem("Abrir NYX", lambda _icon, _item: self.open_center("Conversaciones")),
            pystray.MenuItem("Centro de control", lambda _icon, _item: self.open_center("Sistema")),
            pystray.MenuItem("Activar/desactivar escucha", lambda _icon, _item: self.toggle_listening()),
            pystray.MenuItem(lambda _item: self.status(), lambda _icon, _item: self.open_center("Sistema")),
            pystray.MenuItem("Configuración", lambda _icon, _item: self.open_center("Configuración")),
            pystray.MenuItem("Cerrar NYX", lambda icon, _item: self._close(icon)),
        )
        self._icon = pystray.Icon("NYX", image, "NYX", menu)
        threading.Thread(target=self._icon.run, daemon=True, name="nyx-tray").start()
        return True

    def _close(self, icon) -> None:
        self.shutdown()
        icon.stop()

    def stop(self) -> None:
        if self._icon:
            self._icon.stop()
