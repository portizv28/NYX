"""Esfera flotante de NYX."""

import math
import tkinter as tk
from collections.abc import Callable

from core.state import AssistantState
from gui.state_style import STATE_COLORS


class NyxOrb:
    def __init__(self) -> None:
        self.root = tk.Toplevel()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.config(bg="magenta")
        self.root.wm_attributes("-transparentcolor", "magenta")
        self.root.geometry("160x160+100+100")

        self.canvas = tk.Canvas(
            self.root, width=160, height=160, bg="magenta", highlightthickness=0
        )
        self.canvas.pack()
        self.glow = self.canvas.create_oval(
            30, 30, 130, 130, fill="", outline="#00BFFF", width=10
        )
        self.circle = self.canvas.create_oval(50, 50, 110, 110, fill="#00BFFF", outline="")
        self._time = 0.0
        self._drag_x = 0
        self._drag_y = 0
        self._callback: Callable[[], None] | None = None

        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<Double-Button-1>", self._open)
        self.canvas.bind("<B1-Motion>", self._drag)
        self._animate()

    def _animate(self) -> None:
        self._time += 0.08
        radius = 30 * (1 + math.sin(self._time) * 0.05)
        self.canvas.coords(self.circle, 80 - radius, 80 - radius, 80 + radius, 80 + radius)
        halo = 50 + math.sin(self._time) * 3
        self.canvas.coords(self.glow, 80 - halo, 80 - halo, 80 + halo, 80 + halo)
        self.root.after(20, self._animate)

    def _start_drag(self, event) -> None:
        self._drag_x, self._drag_y = event.x, event.y

    def _open(self, _event) -> None:
        if self._callback:
            self._callback()

    def _drag(self, event) -> None:
        x = self.root.winfo_x() + event.x - self._drag_x
        y = self.root.winfo_y() + event.y - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def set_callback(self, callback: Callable[[], None]) -> None:
        self._callback = callback

    def render_state(self, state: AssistantState) -> None:
        color = STATE_COLORS[state]
        self.canvas.itemconfig(self.circle, fill=color)
        self.canvas.itemconfig(
            self.glow, outline="#333333" if state is AssistantState.SLEEPING else color
        )

    def set_position(self, x: int, y: int) -> None:
        """Posiciona la esfera; futuro movimiento inteligente usará esta API."""
        self.root.geometry(f"+{x}+{y}")

    def position(self) -> tuple[int, int]:
        return self.root.winfo_x(), self.root.winfo_y()

    def move_to(self, x: int, y: int) -> None:
        """Alias semántico para controladores de movimiento futuros."""
        self.set_position(x, y)

    # Compatibilidad con las llamadas de la versión inicial.
    def dormir(self) -> None:
        self.render_state(AssistantState.SLEEPING)

    def escuchar(self) -> None:
        self.render_state(AssistantState.LISTENING)

    def pensar(self) -> None:
        self.render_state(AssistantState.THINKING)

    def hablar(self) -> None:
        self.render_state(AssistantState.SPEAKING)

    def normal(self) -> None:
        self.render_state(AssistantState.IDLE)

    def ocultar(self) -> None:
        self.root.withdraw()

    def hide(self) -> None:
        self.ocultar()

    def mostrar(self) -> None:
        self.root.deiconify()

    def show(self) -> None:
        self.mostrar()
